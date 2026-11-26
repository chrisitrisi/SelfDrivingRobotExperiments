import sys,json,re,math,time; sys.path.insert(0,'/tmp/claude-1000/-home-spiderhead87-School-DA/ac92c1f8-fe08-4559-847c-0964da7411fb/scratchpad')
import pcbnew, rt
src,drc,dst,margin=sys.argv[1],sys.argv[2],sys.argv[3],float(sys.argv[4])
b=pcbnew.LoadBoard(src)
d=json.load(open(drc))
POWER={'5V','3.3V','VBAT_SW','/Power Supply/BAT_FUSED','PACK_SAFE','VBUS_SAFE','/Peripherals/M1_P','/Peripherals/M1_N','/Peripherals/M2_P','/Peripherals/M2_N','/Power Supply/SW_3V3','/RGB LEDs/RGB_5V','CHG_BAT'}
def layers(desc):
    if 'F.Cu - B.Cu' in desc or 'THT' in desc: return ['B','F']
    if 'on B.Cu' in desc: return ['B']
    return ['F']
jobs=[]
for u in d['unconnected_items']:
    a,c=u['items'][0],u['items'][1]
    net=re.search(r'\[(.*?)\]',a['description']).group(1).replace(' / ',' {slash} ') if 'USB-C' in a['description'] else re.search(r'\[(.*?)\]',a['description']).group(1)
    pa=(a['pos']['x'],a['pos']['y']); pc=(c['pos']['x'],c['pos']['y'])
    jobs.append((math.hypot(pa[0]-pc[0],pa[1]-pc[1]),net,pa,layers(a['description']),pc,layers(c['description'])))
jobs.sort(key=lambda j:(0 if j[1] in POWER else 1, j[0]))
ok=fail=0; failed=[]
for dist,net,pa,la,pc,lc in jobs:
    if b.FindNet(net) is None: print('Netz?',net); fail+=1; continue
    w=0.5 if net in POWER else (0.4 if net=='GND' else 0.2)
    x0=min(pa[0],pc[0])-margin; x1=max(pa[0],pc[0])+margin; y0=min(pa[1],pc[1])-margin; y1=max(pa[1],pc[1])+margin
    G=rt.Grid(b,x0,y0,x1,y1,res=0.05)
    best=None
    for sl in la:
        for gl in lc:
            p=rt.astar(G,net,w/2,(pa[0],pa[1],sl),(pc[0],pc[1],gl),layers=('F','B'),via_cost=60,free_r=0.12)
            if p and (best is None or len(p)<len(best[0])): best=(p,sl,gl)
        if best: break
    if best is None and w>0.25:
        w=0.3
        for sl in la:
            for gl in lc:
                p=rt.astar(G,net,w/2,(pa[0],pa[1],sl),(pc[0],pc[1],gl),layers=('F','B'),via_cost=60,free_r=0.12)
                if p: best=(p,sl,gl); break
            if best: break
    if best is None: fail+=1; failed.append((net,round(dist,1))); continue
    rt.commit(b,G,best[0],net,w,start_xy=pa,goal_xy=pc); ok+=1
print('geroutet',ok,'fehlgeschlagen',fail); print(failed)
pcbnew.SaveBoard(dst,b)
