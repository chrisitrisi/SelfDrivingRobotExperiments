#!/usr/bin/env bash
# drcw.sh <board> : prueft Arbeitsplatine gegen aktuellen Schaltplan
S=/tmp/claude-1000/-home-spiderhead87-School-DA/ac92c1f8-fe08-4559-847c-0964da7411fb/scratchpad
P=/home/spiderhead87/School/DA/SelfDrivingRobotExperiments/PCB/Tumbler_Mainboard
rm -rf $S/t && mkdir -p $S/t && rsync -a --exclude='*.lck' --exclude='Tumbler2_Redesign-backups' $P/ $S/t/
cp "$1" $S/t/Tumbler2_Redesign.kicad_pcb
cd $S/t && kicad-cli pcb drc --refill-zones --schematic-parity --format json -o $S/drcw.json Tumbler2_Redesign.kicad_pcb 2>&1 | grep -E 'Found' 
python3 - <<'PY'
import json,collections
d=json.load(open('/tmp/claude-1000/-home-spiderhead87-School-DA/ac92c1f8-fe08-4559-847c-0964da7411fb/scratchpad/drcw.json'))
print('ERR',collections.Counter(v['type'] for v in d['violations'] if v['severity']=='error').most_common())
print('WARN',collections.Counter(v['type'] for v in d['violations'] if v['severity']!='error').most_common())
for v in d['schematic_parity']: print('PAR',v['type'],v['description'][:90],[i['description'][:50] for i in v['items']])
for u in d['unconnected_items']: print('UNC',[(i['description'][:45],i['pos']['x'],i['pos']['y']) for i in u['items']])
known={frozenset(x) for x in [('U9','J12'),('H4','J12'),('H4','J13'),('C41','U13'),('J12','J13'),('U11','C31'),('U3','J6')]}
for v in d['violations']:
    if v['severity']!='error': continue
    if v['type']=='courtyards_overlap':
        refs=frozenset(i['description'].split()[-1] for i in v['items'])
        if refs in known: continue
    if v['type']=='hole_clearance' and all('J4' in i['description'] for i in v['items']): continue
    print('E',v['type'],v['description'][:70],[ (i['description'][:40]) for i in v['items']],v['items'][0]['pos'])
PY
