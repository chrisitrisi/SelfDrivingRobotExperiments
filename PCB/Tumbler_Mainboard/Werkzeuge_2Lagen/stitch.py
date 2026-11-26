import sys,math; sys.path.insert(0,'/tmp/claude-1000/-home-spiderhead87-School-DA/ac92c1f8-fe08-4559-847c-0964da7411fb/scratchpad')
import pcbnew, rt, numpy as np
src,dst,spacing=sys.argv[1],sys.argv[2],float(sys.argv[3])
b=pcbnew.LoadBoard(src)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
gnd=b.FindNet('GND')
fills={}
for z in b.Zones():
    if z.GetNetname()!='GND' or z.GetIsRuleArea(): continue
    for L,k in ((pcbnew.F_Cu,'F'),(pcbnew.B_Cu,'B')):
        if z.IsOnLayer(L): fills[k]=z.GetFilledPolysList(L)
def island(k,x,y):
    ps=fills[k]; p=pcbnew.VECTOR2I(rt.MM(x),rt.MM(y))
    for i in range(ps.OutlineCount()):
        if ps.Outline(i).PointInside(p):
            # nicht in einem Loch dieser Insel
            inhole=any(ps.Hole(i,h).PointInside(p) for h in range(ps.HoleCount(i)))
            return None if inhole else i
    return None
eb=b.GetBoardEdgesBoundingBox()
G=rt.Grid(b,rt.TO(eb.GetLeft()),rt.TO(eb.GetTop()),rt.TO(eb.GetRight()),rt.TO(eb.GetBottom()),res=0.1)
vm=G.via_mask('GND')
# Fuer Vias zusaetzlich 0,15 mm Abstand zum Flaechenrand: Punkt + 4 Nachbarn muessen innerhalb liegen
cands=[]
for j in range(0,vm.shape[0],5):
    for i in range(0,vm.shape[1],5):
        if vm[j,i]: continue
        x,y=G.xy(j,i)
        fi=island('F',x,y); bi=island('B',x,y)
        if fi is None or bi is None: continue
        if any(island('F',x+dx,y+dy)!=fi or island('B',x+dx,y+dy)!=bi for dx,dy in((0.45,0),(-0.45,0),(0,0.45),(0,-0.45))): continue
        cands.append((x,y,fi,bi))
print('moegliche Via-Plaetze',len(cands))
# Union-Find ueber Inseln
par={}
def f(a):
    par.setdefault(a,a)
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
placed=[]
def ok_dist(x,y,mind): return all((x-a)**2+(y-c)**2>=mind*mind for a,c in placed)
# 1) Inseln verbinden
for x,y,fi,bi in cands:
    if f(('F',fi))!=f(('B',bi)) and ok_dist(x,y,1.0):
        par[f(('F',fi))]=f(('B',bi)); placed.append((x,y))
n_conn=len(placed)
# 2) Stitching-Raster
for x,y,fi,bi in cands:
    if ok_dist(x,y,spacing): placed.append((x,y))
for x,y in placed:
    v=pcbnew.PCB_VIA(b); v.SetPosition(pcbnew.VECTOR2I(rt.MM(x),rt.MM(y))); v.SetWidth(rt.MM(0.6)); v.SetDrill(rt.MM(0.3)); v.SetNet(gnd); b.Add(v)
print('Vias Verbindung',n_conn,'Stitching',len(placed)-n_conn)
pcbnew.SaveBoard(dst,b)
