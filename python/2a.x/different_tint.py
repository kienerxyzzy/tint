ACAT_OK=0
ACAT_BRK=1
ACAT_CNT=2
ACAT_RTN=3
NUMOPS={"+":(lambda x,y:x+y),"-":(lambda x,y:x-y),"*":(lambda x,y:x*y),"/":(lambda x,y:x/y),">":(lambda x,y:1 if x>y else 0),"<":(lambda x,y:1 if x<y else 0),">=":(lambda x,y:1 if x>=y else 0),"<=":(lambda x,y:1 if x<=y else 0)}
NUMCONVS=[int,float]
class Instance:
  def __init__(this):
    this.vars=dict()
    this.procs=dict()
    this.stack=[]
    #this.HTHRES=100
  def _run(this,l):
    #this.HTHRES-=1
    #if this.HTHRES<=0:
    #  raise Exception("CEASE COMPUTATION! CEASE COMPUTATION!")
    #print("RUNNING",l)
    assert len(l)>0
    res=""
    if l[0]=="set":
      this.vars[l[1]]=l[2]
    elif l[0] in NUMOPS:
      for CONV in NUMCONVS:
        try:
          res=str(NUMOPS[l[0]](CONV(l[1]),CONV(l[2])))
          break
        except:
          pass
    elif l[0]=="==":res=("1" if l[1]==l[2] else "0")
    elif l[0]=="!=":res=("1" if l[1]!=l[2] else "0")
    elif l[0]=="print":print(" ".join(l[1:]))
    elif l[0]=="input":res=input(" ".join(l[1:]))
    elif l[0]=="_":
      assert len(l)%2==0
      ltmp=[(i if len(i)==0 or i[0]!="$" else this.vars.get(i[1:],"")) for i in l]
      res=ltmp[1]
      for i in range(2,len(l),2):
        res=this._run([ltmp[i],res,ltmp[i+1]])[1]
    elif l[0]=="break":
      return (ACAT_BRK,"")
    elif l[0]=="continue":
      return (ACAT_CNT,"")
    elif l[0]=="return":
      return (ACAT_RTN," ".join(l[1:]))
    elif l[0]=="if":
      if len(l)==3:
        tmp=this._execute("_ "+l[1])
        if tmp[1]!="" and tmp[1]!="0":
          tmp=this._execute(l[2])
          return tmp
      elif (len(l)+1)%3!=0:raise Exception("Malformed if-statement!")
      else:
        for i in range(0,len(l)-2,3):
          tmp=this._execute("_ "+l[i+1])
          if tmp[1]!="" and tmp[1]!="0":
            tmp=this._execute(l[i+2])
            return tmp
        return this._execute(l[-1])
    elif l[0]=="while":
      while True:
        tmp=this._execute("_ "+l[1])
        if tmp[1]=="" or tmp[1]=="0":
          break
        else:
          tmp=this._execute(l[2])
          if tmp[0]==ACAT_BRK:break
          elif tmp[0]==ACAT_CNT:continue
          elif tmp[0]==ACAT_RTN:return tmp
    elif l[0]=="chr":
      res=chr(int(l[1]))
    elif l[0]=="function":
      this.procs[l[1]]=l[2]
    elif l[0]=="uplevel":
      tmp=this.vars.copy()
      this.vars=this.stack.pop()
      res=this._execute(l[1])[1]
      this.stack.append(this.vars.copy())
      this.vars=tmp.copy()
    elif l[0]=="assert":
      if l[1]=="" or l[1]=="0":
        raise Exception(l[2])
    elif l[0] in this.procs:
      this.stack.append(this.vars.copy())
      this.vars={}
      for i,j in enumerate(l[1:]):
        this.vars[str(i)]=j
      this.vars["#"]=str(len(l)-1)
      res=this._execute(this.procs[l[0]])[1]
      this.vars=this.stack.pop()
    else:
      raise Exception(f"{l[0]}?")
    #print(l,"->",res)
    return (ACAT_OK,res)
  def _execute(this,S):
    #print("EXECUTING",S)
    bufstack=[""]
    brackstack=[]
    cmd=[]
    curlies=0
    res=""
    assert len(bufstack)==1+len(brackstack)
    for c in S+"\n":
      if c=="{":
        if curlies>0:
          bufstack[-1]+="{"
        brackstack.append("{")
        curlies+=1
      elif c=="}":
        if len(brackstack)==0 or brackstack.pop()!="{":
          raise Exception("'}' WITHOUT OPENING '{'")
        else:
          curlies-=1
          if curlies>0:
            bufstack[-1]+="}"
      elif c in "[(" and curlies==0:
        brackstack.append(c)
        bufstack.append("")
      elif c=="]" and curlies==0:
        if len(brackstack)==0 or brackstack.pop()!="[":
          raise Exception("']' WITHOUT OPENING '['")
        else:
          tmp=this._execute(bufstack.pop())[1]
          bufstack[-1]+=tmp
      elif c==")" and curlies==0:
        if len(brackstack)==0 or brackstack.pop()!="(":
          raise Exception("')' WITHOUT OPENING '('")
        else:
          tmp=this._execute("_ "+bufstack.pop())[1]
          bufstack[-1]+=tmp
      elif c in " \n;" and len(brackstack)==0:
        if len(bufstack[0])>0:
          cmd.append(bufstack[-1])
          bufstack[-1]=""
        if c!=" " and len(cmd)>0:
          tmp=this._run(cmd)
          if tmp[0]!=ACAT_OK:return tmp
          res=tmp[1]
          cmd=[]
      else:
        bufstack[-1]+=c
    return (ACAT_OK,res)
