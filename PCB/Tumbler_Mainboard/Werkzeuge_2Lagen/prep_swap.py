import sys,xml.etree.ElementTree as ET; import pcbnew
src,netxml,dst=sys.argv[1:4]
b=pcbnew.LoadBoard(src)
# 1) Innenlagen weg
for t in [t for t in b.GetTracks() if t.GetClass()=='PCB_TRACK' and t.GetLayer()==pcbnew.In2_Cu]: b.Delete(t)
for z in [z for z in b.Zones() if not z.GetIsRuleArea() and (z.GetLayerSet().Contains(pcbnew.In1_Cu) or z.GetLayerSet().Contains(pcbnew.In2_Cu))]: b.Delete(z)
for z in b.Zones():
    if z.GetIsRuleArea():
        ls=pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu); z.SetLayerSet(ls)
b.SetCopperLayerCount(2)
# 2) Pad-Netze aus neuer Netzliste fuer U3 und J3
r=ET.parse(netxml).getroot(); want={}
for n in r.iter('net'):
    for x in n.iter('node'):
        if x.get('ref') in ('U3','J3'): want[(x.get('ref'),x.get('pin'))]=n.get('name')
changed=set()
for ref in ('U3','J3'):
    f=b.FindFootprintByReference(ref)
    for p in f.Pads():
        nn=want.get((ref,p.GetNumber()))
        if nn is None: continue
        if p.GetNetname()!=nn:
            ni=b.FindNet(nn) if nn else None
            if nn and ni is None: ni=pcbnew.NETINFO_ITEM(b,nn); b.Add(ni)
            changed.add(p.GetNetname()); changed.add(nn)
            p.SetNet(ni if ni else b.FindNet(''))
changed.discard('')
# 3) Alle Bahnen/Vias der betroffenen Netze loeschen
dead=[t for t in b.GetTracks() if t.GetNetname() in changed]
for t in dead: b.Delete(t)
print('Netze neu verbinden:',len(changed),'| geloeschte Bahnen/Vias:',len(dead))
print(sorted(changed))
pcbnew.SaveBoard(dst,b)
