import sys,json,uuid,re; sys.path.insert(0,'/tmp/claude-1000/-home-spiderhead87-School-DA/ac92c1f8-fe08-4559-847c-0964da7411fb/scratchpad')
from sx import *
F='mcu.kicad_sch'; text=open(F).read(); sch=parse(text)
A=json.load(open('/tmp/claude-1000/-home-spiderhead87-School-DA/ac92c1f8-fe08-4559-847c-0964da7411fb/scratchpad/2L/assign.json'))
lp=libpins(sch)
u3=[c for c in find(sch,'symbol') if prop(c,'Reference')=='U3'][0]; PP={k:(round(v[0],2),round(v[1],2)) for k,v in pinpos(u3,lp).items()}
allpins=set()
for c in find(sch,'symbol'):
    if prop(c,'Reference') and not prop(c,'Reference').startswith('#'):
        for k,v in pinpos(c,lp).items(): allpins.add((round(v[0],2),round(v[1],2)))
R=lambda p:(round(p[0],2),round(p[1],2))
wires=[]
for c in find(sch,'wire'):
    p=[R((float(q[1]),float(q[2]))) for q in first(c,'pts')[1:]]; wires.append((p,unq(first(c,'uuid')[1])))
labels=[]
for c in sch:
    if isinstance(c,list) and c and c[0] in ('label','hierarchical_label','global_label'):
        a=first(c,'at'); labels.append((c[0],unq(c[1]),R((float(a[1]),float(a[2]))),unq(first(c,'uuid')[1]),c))
entries=[]
for c in find(sch,'bus_entry'):
    a=first(c,'at'); sz=first(c,'size'); p0=R((float(a[1]),float(a[2]))); p1=R((p0[0]+float(sz[1]),p0[1]+float(sz[2])))
    entries.append(((p0,p1),unq(first(c,'uuid')[1])))
juncs=[(R((float(first(c,'at')[1]),float(first(c,'at')[2]))),unq(first(c,'uuid')[1])) for c in find(sch,'junction')]
ncs=[(R((float(first(c,'at')[1]),float(first(c,'at')[2]))),unq(first(c,'uuid')[1])) for c in find(sch,'no_connect')]
def on_seg(p,a,b):
    if a[0]==b[0]==p[0]: return min(a[1],b[1])-1e-6<=p[1]<=max(a[1],b[1])+1e-6
    if a[1]==b[1]==p[1]: return min(a[0],b[0])-1e-6<=p[0]<=max(a[0],b[0])+1e-6
    return p==a or p==b
AFFECT=sorted(set(A.values())|{4,5,6,7,8,9,10,11,12,15,17,18,19,20,21,22,23,24,25,30,31,32,33,34,35,38,39})
kill=set(); sig_labels={}
for pin in AFFECT:
    start=R(PP[str(pin)]); pts={start}; tree=set(); changed=True
    while changed:
        changed=False
        for p,u in wires:
            if u in tree: continue
            if any(on_seg(q,p[0],p[-1]) for q in pts) or any(on_seg(x,*[y for y in [p[0],p[-1]]]) for x in pts if False):
                tree.add(u); pts|={p[0],p[-1]}; changed=True
        for (p0,p1),u in entries:
            if u in tree: continue
            if p0 in pts or p1 in pts: tree.add(u); changed=True   # Bus-Eintrag gehoert dazu, aber nicht weiter verfolgen
    others=[q for q in pts if q in allpins and q!=start]
    if others: raise SystemExit(f'Pin {pin}: Drahtbaum fuehrt zu anderem Pin {others}')
    labs=[l for l in labels if any(on_seg(l[2],p[0],p[-1]) for p,u in wires if u in tree) or l[2]==start]
    kill|=tree|{l[3] for l in labs}|{u for q,u in juncs if q in pts}|{u for q,u in ncs if q==start}
    sig_labels[pin]=labs
# Signal -> Labels (vom alten Pin)
OLDPIN={'LS1':4,'LS2':5,'LS3':6,'LS4':7,'BTN':8,'ECHO':9,'SPARE1':10,'SPARE2':11,'RGB':12,'BAT_ADC':15,'LS5':17,'LS6':18,'TRIG':19,'INT1':20,'SDA':21,'SCL':22,'ENCA_A':23,'PWMA':24,'DIR_A':25,'MUX_RSTn':30,'ENCB_A':31,'MOTOR_STBY':32,'USB_PRESENTn':33,'DIR_B':34,'PWMB':35,'ENCA_B':38,'ENCB_B':39}
for s,p in OLDPIN.items():
    names={l[1] for l in sig_labels[p]}
    print(s,'alt Pin',p,'Labels',[(l[0],l[1]) for l in sig_labels[p]])
# Objekte entfernen (Top-Level-Bloecke mit diesen UUIDs)
def remove_blocks(t,uuids):
    out=[];i=0;n=0
    lines=t.split('\n'); res=[]; skip=False; buf=[]
    # Blockweise auf Top-Level (eine Tab-Einrueckung)
    blocks=re.split(r'(?m)^(?=\t\()',t)
    keep=[]
    for b in blocks:
        m=re.search(r'\(uuid "([^"]+)"\)',b)
        head=b.lstrip('\t').split('\n')[0]
        if m and m.group(1) in uuids and re.match(r'\((wire|label|hierarchical_label|global_label|bus_entry|junction|no_connect)\b',head):
            n+=1; continue
        keep.append(b)
    return ''.join(keep),n
text,n=remove_blocks(text,kill); print('entfernt',n,'Objekte')
# Neu aufbauen
new=[]
def wire(a,b): return f'\t(wire\n\t\t(pts\n\t\t\t(xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})\n\t\t)\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n'
def relabel(lab,name,x,y,ang):
    kind=lab[0]; blk=lab[4]
    j=('left' if ang==0 else 'right')+(' bottom' if kind=='label' else '')
    shape=first(blk,'shape')
    s=f'\t({kind} "{name}"\n'
    if shape: s+=f'\t\t(shape {shape[1]})\n'
    s+=f'\t\t(at {x} {y} {ang})\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {j})\n\t\t)\n\t\t(uuid "{uuid.uuid4()}")\n'
    if kind=='global_label': s+=f'\t\t(property "Intersheetrefs" "${{INTERSHEET_REFS}}"\n\t\t\t(at {x} {y} {ang})\n\t\t\t(hide yes)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n'
    return s+'\t)\n'
used=set()
for sig,newpin in A.items():
    px,py=PP[str(newpin)]; left=px<106; d=-1 if left else 1
    end=(round(px+d*7.62,2),py); mid=(round(px+d*3.81,2),py)
    new.append(wire((px,py),end)); used.add(newpin)
    labs=sig_labels[OLDPIN[sig]]
    # nach Typ sortieren: hierarchisch/global ans Ende, lokale in die Mitte
    labs=sorted(labs,key=lambda l:0 if l[0]!='label' else 1)
    seen=set()
    for k,l in enumerate(labs):
        name=sig if sig.startswith('SPARE') else l[1]
        if (l[0],name) in seen: continue
        seen.add((l[0],name))
        pos=end if k==0 else mid
        new.append(relabel(l,name,pos[0],pos[1],180 if left else 0))
for pin in AFFECT:
    if pin not in used:
        px,py=PP[str(pin)]; new.append(f'\t(no_connect\n\t\t(at {px} {py})\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n'); print('NC an Pin',pin)
# J3-seitige IO17/IO18 umbenennen
text=text.replace('(label "IO17"','(label "SPARE1"').replace('(label "IO18"','(label "SPARE2"')
idx=text.rstrip().rindex(')')-1
text=text[:idx+1]+''.join(new)+text[idx+1:]
open(F,'w').write(text); print('fertig')
