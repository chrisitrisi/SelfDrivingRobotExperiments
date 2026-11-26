import sys,json,re,math,collections; sys.path.insert(0,'/tmp/claude-1000/-home-spiderhead87-School-DA/ac92c1f8-fe08-4559-847c-0964da7411fb/scratchpad')
import pcbnew, rt, numpy as np
b=pcbnew.LoadBoard(sys.argv[1]); d=json.load(open(sys.argv[2]))
eb=b.GetBoardEdgesBoundingBox()
G=rt.Grid(b,rt.TO(eb.GetLeft()),rt.TO(eb.GetTop()),rt.TO(eb.GetRight()),rt.TO(eb.GetBottom()),res=0.1)
segs_all=G.segs; circ_all=G.circ
heat=np.zeros((G.ny,G.nx))
blockers=collections.Counter(); fails=0
for u in d['unconnected_items']:
    a,c=u['items']; m=re.search(r'\[(.*?)\]',a['description']); net=m.group(1)
    if net=='GND': continue
    if 'USB-C' in net: net=net.replace(' / ',' {slash} ')
    pa=(a['pos']['x'],a['pos']['y'],'F'); pc=(c['pos']['x'],c['pos']['y'],'F')
    G.segs=[]; G.circ=[]   # nur Pads/Loecher als Hindernis
    p=rt.astar(G,net,0.1,pa,pc,layers=('F','B'),via_cost=40,free_r=0.15)
    G.segs=segs_all; G.circ=circ_all
    if not p: fails+=1; continue
    for x,y,L in p:
        j,i=G.cell(x,y); heat[max(0,j-3):j+4,max(0,i-3):i+4]+=1
        # welche fremden Bahnen liegen hier?
        for s in segs_all:
            if s[0]==L and s[1]!=net:
                x1,y1,x2,y2=s[2:6]
                if min(x1,x2)-0.3<x<max(x1,x2)+0.3 and min(y1,y2)-0.3<y<max(y1,y2)+0.3:
                    dx,dy=x2-x1,y2-y1;L2=dx*dx+dy*dy or 1e-9;t=max(0,min(1,((x-x1)*dx+(y-y1)*dy)/L2))
                    if math.hypot(x-x1-t*dx,y-y1-t*dy)<s[6]+0.25: blockers[s[1]]+=1
print('ohne Bahnen nicht routbar:',fails)
print('Netze, deren Bahnen am haeufigsten im Weg liegen:'); print(blockers.most_common(20))
# Hot spots -> Bauteile in der Naehe
fps=[(f.GetReference(),rt.TO(f.GetPosition().x),rt.TO(f.GetPosition().y)) for f in b.GetFootprints()]
hot=np.argwhere(heat>=heat.max()*0.5)
near=collections.Counter()
for j,i in hot[::5]:
    x,y=G.xy(j,i); r=min(fps,key=lambda f:(f[1]-x)**2+(f[2]-y)**2); near[r[0]]+=1
print('Bauteile an Engstellen:',near.most_common(15))
img=(np.clip(heat/heat.max(),0,1)*255).astype(np.uint8)
rgb=np.stack([img,np.zeros_like(img),255-img],-1); rgb[heat==0]=[240,240,240]
open(sys.argv[3],'wb').write(b'P6 %d %d 255\n'%(G.nx,G.ny)+rgb.tobytes())
