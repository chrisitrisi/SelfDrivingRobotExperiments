import re,math,sys
def tok(s):
    i=0;n=len(s)
    while i<n:
        c=s[i]
        if c in '()': yield c; i+=1
        elif c.isspace(): i+=1
        elif c=='"':
            j=i+1
            while s[j]!='"':
                j+= 2 if s[j]=='\\' else 1
            yield s[i:j+1]; i=j+1
        else:
            j=i
            while j<n and not s[j].isspace() and s[j] not in '()': j+=1
            yield s[i:j]; i=j
def parse(s):
    st=[[]]
    for t in tok(s):
        if t=='(': st.append([])
        elif t==')': x=st.pop(); st[-1].append(x)
        else: st[-1].append(t)
    return st[0][0]
def unq(x): return x[1:-1] if isinstance(x,str) and x.startswith('"') else x
def find(node,key): return [c for c in node if isinstance(c,list) and c and c[0]==key]
def first(node,key):
    r=find(node,key); return r[0] if r else None
def prop(sym,name):
    for p in find(sym,'property'):
        if unq(p[1])==name: return unq(p[2])
def libpins(sch):
    out={}
    for ls in first(sch,'lib_symbols')[1:]:
        name=unq(ls[1]); pins={}
        def walk(n):
            for c in n:
                if isinstance(c,list):
                    if c and c[0]=='pin':
                        at=first(c,'at'); num=unq(first(c,'number')[1])
                        pins[num]=(float(at[1]),float(at[2]))
                    else: walk(c)
        walk(ls); out[name]=pins
    return out
def pinpos(sym,lp):
    at=first(sym,'at'); x,y,rot=float(at[1]),float(at[2]),float(at[3]) if len(at)>3 else 0
    mir=first(sym,'mirror'); res={}
    for num,(px,py) in lp[unq(first(sym,'lib_id')[1])].items():
        py=-py
        if mir and mir[1]=='x': py=-py
        if mir and mir[1]=='y': px=-px
        r=math.radians(-rot) 
        rx=px*math.cos(r)-py*math.sin(r); ry=px*math.sin(r)+py*math.cos(r)
        res[num]=(round(x+rx,3),round(y+ry,3))
    return res
