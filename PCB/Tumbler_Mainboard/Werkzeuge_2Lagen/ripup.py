import sys,json,re,math; sys.path.insert(0,'/tmp/claude-1000/-home-spiderhead87-School-DA/ac92c1f8-fe08-4559-847c-0964da7411fb/scratchpad')
import pcbnew, rt
src,drc,dst,margin,softc=sys.argv[1],sys.argv[2],sys.argv[3],float(sys.argv[4]),float(sys.argv[5])
b=pcbnew.LoadBoard(src); d=json.load(open(drc))
POWER={'5V','3.3V','VBAT_SW','/Power Supply/BAT_FUSED','PACK_SAFE','VBUS_SAFE','/Peripherals/M1_P','/Peripherals/M1_N','/Peripherals/M2_P','/Peripherals/M2_N','/Power Supply/SW_3V3','/RGB LEDs/RGB_5V','CHG_BAT'}
def layers(desc):
    if 'F.Cu - B.Cu' in desc or 'PTH' in desc: return ['B','F']
    return ['B'] if 'on B.Cu' in desc else ['F']
jobs=[]
for u in d['unconnected_items']:
    a,c=u['items']; net=re.search(r'\[(.*?)\]',a['description']).group(1)
    if net=='GND' or 'Zone' in a['description'] or 'Zone' in c['description']: continue
    if 'USB-C' in net: net=net.replace(' / ',' {slash} ')
    pa=(a['pos']['x'],a['pos']['y']); pc=(c['pos']['x'],c['pos']['y'])
    jobs.append((0 if net in POWER else 1, math.dist(pa,pc), net, pa, layers(a['description']), pc, layers(c['description'])))
jobs.sort()
TO=rt.TO
def find_track(L,n,x1,y1,x2,y2):
    for t in b.GetTracks():
        if t.GetClass()=='PCB_TRACK' and t.GetNetname()==n and rt.LNAME.get(t.GetLayer())==L:
            s,e=t.GetStart(),t.GetEnd()
            if abs(TO(s.x)-x1)<1e-3 and abs(TO(s.y)-y1)<1e-3 and abs(TO(e.x)-x2)<1e-3 and abs(TO(e.y)-y2)<1e-3: return t
def find_via(n,x,y):
    for t in b.GetTracks():
        if t.GetClass()=='PCB_VIA' and t.GetNetname()==n:
            p=t.GetPosition()
            if abs(TO(p.x)-x)<1e-3 and abs(TO(p.y)-y)<1e-3: return t
ok=rip=fail=0; ripped_nets=set()
for _,dist,net,pa,la,pc,lc in jobs:
    if b.FindNet(net) is None: fail+=1; continue
    w=0.5 if net in POWER else 0.2
    G=rt.Grid(b,min(pa[0],pc[0])-margin,min(pa[1],pc[1])-margin,max(pa[0],pc[0])+margin,max(pa[1],pc[1])+margin,res=0.05)
    best=None
    for sl in la:
        for gl in lc:
            p=rt.astar(G,net,w/2,(pa[0],pa[1],sl),(pc[0],pc[1],gl),layers=('F','B'),via_cost=60,free_r=0.12)
            if p: best=p; break
        if best: break
    if best:
        rt.commit(b,G,best,net,w,start_xy=pa,goal_xy=pc); ok+=1; continue
    # Rip-up
    for sl in la:
        for gl in lc:
            p=rt.astar_soft(G,net,w/2,(pa[0],pa[1],sl),(pc[0],pc[1],gl),layers=('F','B'),via_cost=60,soft_cost=softc,free_r=0.12,protect={'GND'})
            if p: best=p; break
        if best: break
    if not best: fail+=1; continue
    vs,vv=rt.victims(G,net,best,w)
    for k in sorted(vs,reverse=True):
        L,n,x1,y1,x2,y2,hw=G.segs[k]; t=find_track(L,n,x1,y1,x2,y2)
        if t: b.Delete(t); ripped_nets.add(n)
        G.segs.pop(k)
    for k in sorted(vv,reverse=True):
        L,n,x,y,r=G.circ[k]; t=find_via(n,x,y)
        if t: b.Delete(t); ripped_nets.add(n)
        G.circ.pop(k)
    rt.commit(b,G,best,net,w,start_xy=pa,goal_xy=pc); rip+=1
print(f'direkt {ok}, mit Rip-up {rip}, fehlgeschlagen {fail}, aufgerissene Netze {len(ripped_nets)}')
pcbnew.SaveBoard(dst,b)
