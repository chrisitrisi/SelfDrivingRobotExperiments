"""Kleines Raster-Routing-Werkzeug fuer pcbnew (KiCad 10).
Raster 0.05 mm in einem Fenster. Hindernisse werden je Route mit
(Breite/2 + Abstand) aufgeblasen. Gleiche Netze sind kein Hindernis."""
import pcbnew, numpy as np, heapq, math

MM = pcbnew.FromMM
TO = pcbnew.ToMM
LAYERS = {'F': pcbnew.F_Cu, 'I2': pcbnew.In2_Cu, 'B': pcbnew.B_Cu}
LNAME = {v: k for k, v in LAYERS.items()}


class Grid:
    def __init__(self, board, x0, y0, x1, y1, res=0.05, clr=0.16):
        self.b = board; self.x0, self.y0 = x0, y0; self.res = res; self.clr = clr
        self.nx = int((x1 - x0) / res) + 1; self.ny = int((y1 - y0) / res) + 1
        self.X = x0 + np.arange(self.nx) * res
        self.Y = y0 + np.arange(self.ny) * res
        self.collect()

    # ---------------- Sammeln der Kupferobjekte -----------------
    def collect(self):
        b = self.b
        self.segs = []   # (layer, net, x1,y1,x2,y2, halfwidth)
        self.circ = []   # (layerset or None(all), net, x,y, r, is_hole_r)
        self.rects = []  # (layer or None, net, xa,ya,xb,yb)  pad bbox
        self.holes = []  # (x,y,r)
        self.smd = []    # (net, xa,ya,xb,yb) eigene SMD-Pads: keine Via hinein
        for t in b.GetTracks():
            net = t.GetNetname()
            if t.GetClass() == 'PCB_VIA':
                p = t.GetPosition()
                self.circ.append((None, net, TO(p.x), TO(p.y), TO(t.GetWidth(pcbnew.F_Cu)) / 2))
                self.holes.append((TO(p.x), TO(p.y), TO(t.GetDrillValue()) / 2))
            elif t.GetClass() == 'PCB_TRACK':
                if t.GetLayer() not in LNAME: continue
                a, c = t.GetStart(), t.GetEnd()
                self.segs.append((LNAME[t.GetLayer()], net, TO(a.x), TO(a.y), TO(c.x), TO(c.y), TO(t.GetWidth()) / 2))
            elif t.GetClass() == 'PCB_ARC':
                a, c, m = t.GetStart(), t.GetEnd(), t.GetMid()
                for (p, q) in [(a, m), (m, c)]:
                    self.segs.append((LNAME.get(t.GetLayer(), 'X'), net, TO(p.x), TO(p.y), TO(q.x), TO(q.y), TO(t.GetWidth()) / 2))
        for f in b.GetFootprints():
            for p in f.Pads():
                net = p.GetNetname() or ('__nc_%s_%s' % (f.GetReference(), p.GetNumber()))
                bb = p.GetBoundingBox()
                xa, ya, xb, yb = TO(bb.GetLeft()), TO(bb.GetTop()), TO(bb.GetRight()), TO(bb.GetBottom())
                ls = p.GetLayerSet()
                if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD: self.smd.append((net, xa, ya, xb, yb))
                for k, L in LAYERS.items():
                    if ls.Contains(L):
                        self.rects.append((k, net, xa, ya, xb, yb))
                if p.HasHole():
                    q = p.GetPosition(); ds = p.GetDrillSize()
                    self.holes.append((TO(q.x), TO(q.y), TO(max(ds.x, ds.y)) / 2))
                    if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                        for k in LAYERS: self.rects.append((k, '__npth', TO(q.x) - TO(ds.x) / 2, TO(q.y) - TO(ds.y) / 2, TO(q.x) + TO(ds.x) / 2, TO(q.y) + TO(ds.y) / 2))
        # Sperrflaechen (Rule areas)
        self.keep = []
        for z in b.Zones():
            if z.GetIsRuleArea():
                bb = z.GetBoundingBox()
                self.keep.append((TO(bb.GetLeft()), TO(bb.GetTop()), TO(bb.GetRight()), TO(bb.GetBottom())))
        eb = b.GetBoardEdgesBoundingBox()
        self.edge = (TO(eb.GetLeft()), TO(eb.GetTop()), TO(eb.GetRight()), TO(eb.GetBottom()))

    # --------------- Rasterisierung -----------------
    def _idx(self, xa, xb, ya, yb):
        i0 = max(0, int((xa - self.x0) / self.res)); i1 = min(self.nx, int((xb - self.x0) / self.res) + 2)
        j0 = max(0, int((ya - self.y0) / self.res)); j1 = min(self.ny, int((yb - self.y0) / self.res) + 2)
        i0 = min(i0, self.nx); j0 = min(j0, self.ny); i1 = max(i1, i0); j1 = max(j1, j0)
        return i0, i1, j0, j1

    def mask(self, layer, net, halfw, extra=0.0):
        """True = belegt fuer eine Bahn der halben Breite halfw des Netzes net."""
        m = np.zeros((self.ny, self.nx), bool)
        c = self.clr + halfw + extra
        for (L, n, x1, y1, x2, y2, hw) in self.segs:
            if L != layer or n == net: continue
            r = hw + c
            i0, i1, j0, j1 = self._idx(min(x1, x2) - r, max(x1, x2) + r, min(y1, y2) - r, max(y1, y2) + r)
            if i0 >= i1 or j0 >= j1: continue
            X, Y = np.meshgrid(self.X[i0:i1], self.Y[j0:j1])
            dx, dy = x2 - x1, y2 - y1; L2 = dx * dx + dy * dy
            t = np.clip(((X - x1) * dx + (Y - y1) * dy) / L2, 0, 1) if L2 > 0 else 0
            d2 = (X - x1 - t * dx) ** 2 + (Y - y1 - t * dy) ** 2
            m[j0:j1, i0:i1] |= d2 <= r * r
        for (L, n, x, y, rr) in self.circ:
            if n == net: continue
            r = rr + c
            i0, i1, j0, j1 = self._idx(x - r, x + r, y - r, y + r)
            if i0 >= i1 or j0 >= j1: continue
            X, Y = np.meshgrid(self.X[i0:i1], self.Y[j0:j1])
            m[j0:j1, i0:i1] |= (X - x) ** 2 + (Y - y) ** 2 <= r * r
        for (L, n, xa, ya, xb, yb) in self.rects:
            if L != layer or n == net: continue
            i0, i1, j0, j1 = self._idx(xa - c, xb + c, ya - c, yb + c)
            if i0 >= i1 or j0 >= j1: continue
            X, Y = np.meshgrid(self.X[i0:i1], self.Y[j0:j1])
            dx = np.maximum(np.maximum(xa - X, X - xb), 0); dy = np.maximum(np.maximum(ya - Y, Y - yb), 0)
            m[j0:j1, i0:i1] |= dx * dx + dy * dy <= c * c
        for (xa, ya, xb, yb) in self.keep:
            i0, i1, j0, j1 = self._idx(xa - c, xb + c, ya - c, yb + c)
            m[j0:j1, i0:i1] = True
        ex = 0.3 + halfw
        xa, ya, xb, yb = self.edge
        m[:, self.X < xa + ex] = True; m[:, self.X > xb - ex] = True
        m[self.Y < ya + ex, :] = True; m[self.Y > yb - ex, :] = True
        return m

    def via_mask(self, net, vd=0.6, drill=0.3):
        m = np.zeros((self.ny, self.nx), bool)
        for k in LAYERS: m |= self.mask(k, net, vd / 2)
        for (n, xa, ya, xb, yb) in self.smd:
            if n != net: continue
            i0, i1, j0, j1 = self._idx(xa - 0.35, xb + 0.35, ya - 0.35, yb + 0.35)
            m[j0:j1, i0:i1] = True
        # Loch-zu-Loch
        for (x, y, r) in self.holes:
            rr = r + drill / 2 + 0.26
            i0, i1, j0, j1 = self._idx(x - rr, x + rr, y - rr, y + rr)
            if i0 >= i1 or j0 >= j1: continue
            X, Y = np.meshgrid(self.X[i0:i1], self.Y[j0:j1])
            m[j0:j1, i0:i1] |= (X - x) ** 2 + (Y - y) ** 2 <= rr * rr
        return m

    def cell(self, x, y):
        return int(round((y - self.y0) / self.res)), int(round((x - self.x0) / self.res))

    def xy(self, j, i):
        return self.x0 + i * self.res, self.y0 + j * self.res


def astar(G, net, halfw, start, goal, layers=('B',), via_cost=40, viaok=True, free_r=0.0):
    """start/goal: (x,y,layer).  Rueckgabe Liste von (x,y,layer)."""
    masks = {L: G.mask(L, net, halfw) for L in layers}
    vm = G.via_mask(net) if (viaok and len(layers) > 1) else None
    # Start/Ziel-Umgebung freiraeumen (eigene Pads)
    for (x, y, L) in (start, goal):
        j, i = G.cell(x, y); k = max(1, int(free_r / G.res))
        masks[L][max(0, j - k):j + k + 1, max(0, i - k):i + k + 1] = False
    sj, si = G.cell(start[0], start[1]); gj, gi = G.cell(goal[0], goal[1])
    S = (start[2], sj, si); Gl = (goal[2], gj, gi)
    li = {L: n for n, L in enumerate(layers)}
    dirs = [(0, 1, 1), (1, 0, 1), (0, -1, 1), (-1, 0, 1), (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]
    h = lambda j, i: math.hypot(j - gj, i - gi)
    openh = [(h(sj, si), 0.0, S, None, None)]
    came = {}; gbest = {S: 0.0}
    while openh:
        f, g, node, par, d = heapq.heappop(openh)
        if node in came: continue
        came[node] = (par, d)
        if node == Gl: break
        L, j, i = node
        for dj, di, c in dirs:
            nj, ni = j + dj, i + di
            if not (0 <= nj < G.ny and 0 <= ni < G.nx): continue
            if masks[L][nj, ni]: continue
            turn = 0 if d is None or d == (dj, di) else 0.6
            nn = (L, nj, ni); ng = g + c + turn
            if ng < gbest.get(nn, 1e18):
                gbest[nn] = ng; heapq.heappush(openh, (ng + h(nj, ni), ng, nn, node, (dj, di)))
        if vm is not None and not vm[j, i]:
            for L2 in layers:
                if L2 == L: continue
                nn = (L2, j, i); ng = g + via_cost
                if ng < gbest.get(nn, 1e18):
                    gbest[nn] = ng; heapq.heappush(openh, (ng + h(j, i), ng, nn, node, None))
    if Gl not in came: return None
    path = []; n = Gl
    while n is not None:
        path.append(n); n = came[n][0]
    path.reverse()
    return [(G.xy(j, i)[0], G.xy(j, i)[1], L) for (L, j, i) in path]


def simplify(path):
    """Kollineare Punkte zusammenfassen, Lagenwechsel behalten."""
    out = [path[0]]
    for k in range(1, len(path) - 1):
        a, b, c = out[-1], path[k], path[k + 1]
        if b[2] != a[2] or c[2] != b[2]:
            out.append(b); continue
        d1 = (round(b[0] - a[0], 4), round(b[1] - a[1], 4)); d2 = (round(c[0] - b[0], 4), round(c[1] - b[1], 4))
        n1 = math.hypot(*d1); n2 = math.hypot(*d2)
        if n1 and n2 and abs(d1[0] / n1 - d2[0] / n2) < 1e-6 and abs(d1[1] / n1 - d2[1] / n2) < 1e-6: continue
        out.append(b)
    out.append(path[-1])
    return out


def commit(board, G, path, netname, width, start_xy=None, goal_xy=None):
    """Bahnen + Vias anlegen; start_xy/goal_xy = exakte Pad-Mitte (Rasterversatz)."""
    net = board.FindNet(netname)
    pts = simplify(path)
    if start_xy: pts[0] = (start_xy[0], start_xy[1], pts[0][2])
    if goal_xy: pts[-1] = (goal_xy[0], goal_xy[1], pts[-1][2])
    made = []
    for a, c in zip(pts, pts[1:]):
        if a[2] != c[2]:
            v = pcbnew.PCB_VIA(board); v.SetPosition(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
            v.SetWidth(MM(0.6)); v.SetDrill(MM(0.3)); v.SetNet(net); v.SetViaType(pcbnew.VIATYPE_THROUGH)
            board.Add(v); made.append(v)
            G.circ.append((None, netname, a[0], a[1], 0.3)); G.holes.append((a[0], a[1], 0.15))
            continue
        if abs(a[0] - c[0]) < 1e-6 and abs(a[1] - c[1]) < 1e-6: continue
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(c[0]), MM(c[1])))
        t.SetWidth(MM(width)); t.SetLayer(LAYERS[a[2]]); t.SetNet(net)
        board.Add(t); made.append(t)
        G.segs.append((a[2], netname, a[0], a[1], c[0], c[1], width / 2))
    return made


def astar_soft(G, net, halfw, start, goal, layers=('F', 'B'), via_cost=60, soft_cost=40, free_r=0.12, protect=()):
    """Wie astar, aber Bahnen/Vias anderer Netze sind gegen Aufpreis passierbar (Rip-up).
    protect: Netze, deren Bahnen hart bleiben."""
    segs, circ = G.segs, G.circ
    hard_s = [s for s in segs if s[1] in protect]; hard_c = [c for c in circ if c[1] in protect]
    G.segs, G.circ = hard_s, hard_c
    hard = {L: G.mask(L, net, halfw) for L in layers}; vhard = G.via_mask(net)
    G.segs, G.circ = segs, circ
    full = {L: G.mask(L, net, halfw) for L in layers}; vfull = G.via_mask(net)
    soft = {L: full[L] & ~hard[L] for L in layers}; vsoft = vfull & ~vhard
    for (x, y, L) in (start, goal):
        j, i = G.cell(x, y); k = max(1, int(free_r / G.res))
        hard[L][max(0, j - k):j + k + 1, max(0, i - k):i + k + 1] = False
        soft[L][max(0, j - k):j + k + 1, max(0, i - k):i + k + 1] = False
    sj, si = G.cell(start[0], start[1]); gj, gi = G.cell(goal[0], goal[1])
    S = (start[2], sj, si); Gl = (goal[2], gj, gi)
    dirs = [(0, 1, 1), (1, 0, 1), (0, -1, 1), (-1, 0, 1), (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]
    h = lambda j, i: math.hypot(j - gj, i - gi)
    openh = [(h(sj, si), 0.0, S, None, None)]; came = {}; gbest = {S: 0.0}
    while openh:
        f, g, node, par, d = heapq.heappop(openh)
        if node in came: continue
        came[node] = (par, d)
        if node == Gl: break
        L, j, i = node
        for dj, di, c in dirs:
            nj, ni = j + dj, i + di
            if not (0 <= nj < G.ny and 0 <= ni < G.nx) or hard[L][nj, ni]: continue
            cc = c + (0 if d is None or d == (dj, di) else 0.6) + (soft_cost if soft[L][nj, ni] else 0)
            nn = (L, nj, ni); ng = g + cc
            if ng < gbest.get(nn, 1e18):
                gbest[nn] = ng; heapq.heappush(openh, (ng + h(nj, ni), ng, nn, node, (dj, di)))
        if not vhard[j, i]:
            for L2 in layers:
                if L2 == L: continue
                nn = (L2, j, i); ng = g + via_cost + (soft_cost * 3 if vsoft[j, i] else 0)
                if ng < gbest.get(nn, 1e18):
                    gbest[nn] = ng; heapq.heappush(openh, (ng + h(j, i), ng, nn, node, None))
    if Gl not in came: return None
    path = []; n = Gl
    while n is not None: path.append(n); n = came[n][0]
    path.reverse()
    return [(G.xy(j, i)[0], G.xy(j, i)[1], L) for (L, j, i) in path]


def victims(G, net, path, width):
    """Bahnen/Vias anderer Netze, die der Pfad verletzt."""
    import numpy as np
    vs = set(); vv = set()
    P = {}
    for (x, y, L) in path: P.setdefault(L, []).append((x, y))
    allp = [(x, y) for (x, y, L) in path]
    # Lagenwechsel = Via-Stellen
    vias = [(a[0], a[1]) for a, b in zip(path, path[1:]) if a[2] != b[2]]
    for k, (L, n, x1, y1, x2, y2, hw) in enumerate(G.segs):
        if n == net: continue
        pts = P.get(L, [])
        need = hw + G.clr + width / 2
        cand = pts + [(vx, vy) for vx, vy in vias]
        if not cand: continue
        a = np.array(cand); dx, dy = x2 - x1, y2 - y1; L2 = dx * dx + dy * dy or 1e-12
        t = np.clip(((a[:, 0] - x1) * dx + (a[:, 1] - y1) * dy) / L2, 0, 1)
        d = np.hypot(a[:, 0] - x1 - t * dx, a[:, 1] - y1 - t * dy)
        lim = np.full(len(cand), need); lim[len(pts):] = hw + G.clr + 0.3
        if (d < lim).any(): vs.add(k)
    for k, (L, n, x, y, r) in enumerate(G.circ):
        if n == net: continue
        a = np.array(allp); d = np.hypot(a[:, 0] - x, a[:, 1] - y)
        if (d < r + G.clr + width / 2).any() or any(math.hypot(vx - x, vy - y) < r + 0.3 + G.clr for vx, vy in vias): vv.add(k)
    return vs, vv
