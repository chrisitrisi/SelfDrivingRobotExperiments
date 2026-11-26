#!/usr/bin/env bash
# loop.sh <start> <runden> : Rip-up-Schleife, behaelt besten Stand (offen + 5*Abstandsfehler)
S=/tmp/claude-1000/-home-spiderhead87-School-DA/ac92c1f8-fe08-4559-847c-0964da7411fb/scratchpad; cd $S/2L
cur=$1; best=""; bestscore=99999
for i in $(seq 1 $2); do
  $S/drcw.sh $S/2L/$cur.kicad_pcb >/dev/null 2>&1; cp $S/drcw.json drc_$cur.json
  read n g e <<<$(python3 -c "
import json,re;d=json.load(open('drc_$cur.json'));u=d['unconnected_items']
g=sum(1 for x in u if '[GND]' in x['items'][0]['description'])
e=sum(1 for v in d['violations'] if v['type'] in('clearance','shorting_items','tracks_crossing'))
print(len(u),g,e)")
  score=$((n+5*e)); echo "Runde $i: $cur offen $n (GND $g) Fehler $e"
  if [ $score -lt $bestscore ]; then bestscore=$score; best=$cur; fi
  soft=$((30+10*i)); nxt=r$i
  python3 ripup.py $cur.kicad_pcb drc_$cur.json $nxt.kicad_pcb 15 $soft 2>&1 | grep -v -e swig -e Debug | tail -1
  cur=$nxt
done
echo "BEST $best score $bestscore"
