import math,json
# ESP-Pads (aus PCB): Modulpin -> (GPIO, x, y, Kante)
P={4:(4,185.45,101.75,'T'),5:(5,184.18,101.75,'T'),6:(6,182.91,101.75,'T'),7:(7,181.64,101.75,'T'),8:(15,180.37,101.75,'T'),9:(16,179.1,101.75,'T'),10:(17,177.83,101.75,'T'),11:(18,176.56,101.75,'T'),12:(8,175.29,101.75,'T'),
   15:(3,171.5,103.52,'L'),17:(9,171.5,106.06,'L'),18:(10,171.5,107.33,'L'),19:(11,171.5,108.59,'L'),20:(12,171.5,109.86,'L'),21:(13,171.5,111.14,'L'),22:(14,171.5,112.41,'L'),23:(21,171.5,113.67,'L'),24:(47,171.5,114.94,'L'),25:(48,171.5,116.22,'L'),
   28:(35,174.02,119.25,'B'),29:(36,175.29,119.25,'B'),30:(37,176.56,119.25,'B'),31:(38,177.83,119.25,'B'),32:(39,179.1,119.25,'B'),33:(40,180.37,119.25,'B'),34:(41,181.64,119.25,'B'),35:(42,182.91,119.25,'B'),38:(2,186.72,119.25,'B'),39:(1,187.99,119.25,'B')}
NORM={'T':(0,-1),'L':(-1,0),'B':(0,1)}
ADC={1,2,3,4,5,6,7,8,9,10}
# Signal -> Ankerpunkt (Quelle), ADC-Pflicht, verbotene GPIOs
SIG={'LS1':((165.2,135.5),1),'LS2':((163.2,137.8),1),'LS3':((169.2,135.5),1),'LS4':((173.0,136.3),1),'LS5':((175.0,136.3),1),'LS6':((177.0,136.3),1),
 'BAT_ADC':((158,99),1),'RGB':((136,132),0),'ENCA_A':((134,90.7),0),'ENCB_A':((134,89.4),0),'ENCA_B':((134,93.3),0),'ENCB_B':((134,92.0),0),
 'TRIG':((128,99.8),0),'ECHO':((128,93.3),0),'INT1':((146,99),0),'SDA':((138,110),0),'SCL':((138,111.5),0),
 'PWMA':((154.5,86.1),0),'DIR_A':((154.5,87.4),0),'PWMB':((154.5,91.3),0),'DIR_B':((154.5,90.0),0),'MOTOR_STBY':((154.5,88.7),0),
 'USB_PRESENTn':((169.4,131.5),0),'MUX_RSTn':((130,115),0),'BTN':((175,125),0),'SPARE1':((166,116.7),0),'SPARE2':((166,119.3),0)}
FORBID={'MOTOR_STBY':{39,18},'PWMA':{18},'PWMB':{18},'DIR_A':{18},'DIR_B':{18},'SPARE1':set(),'SPARE2':set()}
WEIGHT={'SPARE1':0.2,'SPARE2':0.2}
sigs=list(SIG); pins=list(P); INF=1e6
def cost(s,p):
    g,x,y,e=P[p]; (ax,ay),adc=SIG[s]
    if adc and g not in ADC: return INF
    if g in FORBID.get(s,set()): return INF
    d=math.hypot(ax-x,ay-y); n=NORM[e]
    if (ax-x)*n[0]+(ay-y)*n[1]<0: d+=25     # Quelle liegt auf der anderen Modulseite -> Umweg
    if not adc and g in ADC: d+=6            # ADC-Pins moeglichst fuer ADC freihalten
    return d*WEIGHT.get(s,1)
# Hungarian (rechteckig: Signale <= Pins)
n=len(sigs); m=len(pins); C=[[cost(s,p) for p in pins] for s in sigs]
u=[0]*(n+1); v=[0]*(m+1); pp=[0]*(m+1); way=[0]*(m+1)
for i in range(1,n+1):
    pp[0]=i; j0=0; minv=[INF*10]*(m+1); used=[False]*(m+1)
    while True:
        used[j0]=True; i0=pp[j0]; delta=INF*10; j1=0
        for j in range(1,m+1):
            if not used[j]:
                cur=C[i0-1][j-1]-u[i0]-v[j]
                if cur<minv[j]: minv[j]=cur; way[j]=j0
                if minv[j]<delta: delta=minv[j]; j1=j
        for j in range(m+1):
            if used[j]: u[pp[j]]+=delta; v[j]-=delta
            else: minv[j]-=delta
        j0=j1
        if pp[j0]==0: break
    while True:
        j1=way[j0]; pp[j0]=pp[j1]; j0=j1
        if j0==0: break
res={sigs[pp[j]-1]:pins[j-1] for j in range(1,m+1) if pp[j]}
old={'LS1':4,'LS2':5,'LS3':6,'LS4':7,'LS5':17,'LS6':18,'BAT_ADC':15,'RGB':12,'ENCA_A':23,'ENCB_A':31,'ENCA_B':38,'ENCB_B':39,'TRIG':19,'ECHO':9,'INT1':20,'SDA':21,'SCL':22,'PWMA':24,'DIR_A':25,'PWMB':35,'DIR_B':34,'MOTOR_STBY':32,'USB_PRESENTn':33,'MUX_RSTn':30,'BTN':8,'SPARE1':10,'SPARE2':11}
tot_old=sum(cost(s,old[s]) for s in sigs); tot_new=sum(cost(s,res[s]) for s in sigs)
print('Kosten alt %.0f  neu %.0f'%(tot_old,tot_new))
for s in sigs:
    po,pn=old[s],res[s]; print(f'{s:13s} GPIO{P[po][0]:>2} (Pin{po:>2},{P[po][3]})  ->  GPIO{P[pn][0]:>2} (Pin{pn:>2},{P[pn][3]})' + ('' if po!=pn else '   unveraendert'))
json.dump({s:res[s] for s in sigs},open('/tmp/claude-1000/-home-spiderhead87-School-DA/ac92c1f8-fe08-4559-847c-0964da7411fb/scratchpad/2L/assign.json','w'))
