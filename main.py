# TINT (TINT Is Not Tcl)
# A simple scripting language with Tcl-based syntax
#fmt: off
def _istrue(S):
    t=S[1]
    return t!="0" and t!=""
class Instance:
  def __init__(self):
    self.variables=dict()
    self.procedures=dict()
    self.globals=dict()
    self.vstack=[]
  DEFAULT_RETVAL=""
  def _run(self,command: list[str]):
    retval=self.DEFAULT_RETVAL
    if len(command)==0:return [0,None]
    else:
      cmd=command[0]
      #other stuff
      if cmd=="#":return [0,None]
      elif cmd=="puts":print(command[1])
      elif cmd=="gets":retval=input(command[1])
      elif cmd=="lit":retval=command[1]
      elif cmd=="set":
        if command[1][0]=="_":
          self.globals[command[1]]=command[2]
        else:
          self.variables[command[1]]=command[2]
      elif cmd=="add":retval=sum([int(i) for i in command[1:]])
      elif cmd=="sub":retval=int(command[1])-int(command[2])
      elif cmd=="mul":retval=int(command[1])*int(command[2])
      elif cmd=="div":retval=int(command[1])//int(command[2])
      elif cmd=="mod":retval=int(command[1])%int(command[2])
      elif cmd=="lt":retval=(1 if int(command[1])<int(command[2]) else 0)
      elif cmd=="le":retval=(1 if int(command[1])<=int(command[2]) else 0)
      elif cmd=="gt":retval=(1 if int(command[1])>int(command[2]) else 0)
      elif cmd=="ge":retval=(1 if int(command[1])>=int(command[2]) else 0)
      elif cmd=="eq":retval=(1 if command[1]==command[2] else 0)
      elif cmd=="ne":retval=(1 if command[1]!=command[2] else 0)
      #stringies
      elif cmd=="chr":retval=chr(int(command[1]))
      elif cmd=="ord":retval=ord(command[1])
      elif cmd=="len":retval=len(command[1])
      elif cmd=="index":retval=command[1][int(command[2])]
      #floating pointies
      elif cmd=="addf":retval=sum([float(i) for i in command[1:]])
      elif cmd=="subf":retval=float(command[1])-float(command[2])
      elif cmd=="mulf":retval=float(command[1])*float(command[2])
      elif cmd=="divf":retval=float(command[1])/float(command[2])
      elif cmd=="modf":retval=float(command[1])%float(command[2])
      elif cmd=="ltf":retval=(1 if float(command[1])<float(command[2]) else 0)
      elif cmd=="lef":retval=(1 if float(command[1])<=float(command[2]) else 0)
      elif cmd=="gtf":retval=(1 if float(command[1])>float(command[2]) else 0)
      elif cmd=="gef":retval=(1 if float(command[1])>=float(command[2]) else 0)
      elif cmd=="int":retval=int(float(command[1]))
      elif cmd=="if":
        if len(command)==3:
          if _istrue((output:=self._execute(command[1]))):
            if output[0]!=0:return output
            output=self._execute(command[2])
            if output[0]!=0:return output
        elif (len(command)+1)%3!=0:raise SyntaxError("Malformed 'if' statement!") 
        else:
          flag=True
          for i in range(1,len(command)-3,3):
            if _istrue((output:=self._execute(command[i]))):
              if output[0]!=0:return output
              output=self._execute(command[i+1])
              if output[0]!=0:return output
              flag=False
              break
          if flag:
            output=self._execute(command[-1])
            if output[0]!=0:return output
      elif cmd=="break":
        return [2,""]
      elif cmd=="continue":
        return [3,""]
      elif cmd=="return":
        if len(command)==1:
          return [4,self.DEFAULT_RETVAL]
        else:
          return [4,command[1]]
      elif cmd=="while":
        while _istrue(self._execute(command[1])):
          output=self._execute(command[2])
          if output[0]==2:break
          elif output[0]==3:continue
          elif output[0]==0:pass
          else: return output
      elif cmd=="until":
        while not _istrue(self._execute(command[1])):
          output=self._execute(command[2])
          if output[0]==2:break
          elif output[0]==3:continue
          elif output[0]==0:pass
          else: return output
      elif cmd=="proc":
        self.procedures[command[1]]=(command[2],command[3])
      elif cmd in self.procedures:
        self.vstack.append(self.variables.copy())
        self.variables.clear()
        for i,j in enumerate(self.procedures[cmd][0].split()):
          self.variables[j]=command[i+1]
        output=self._execute(self.procedures[cmd][1])
        self.variables=self.vstack.pop().copy()
        if output[0]==1:return output
        if output[0]==2:raise Exception("'break' statement within procedure!")
        if output[0]==3:raise Exception("'continue' statement within procedure!")
        retval=output[1]
      else:
        raise Exception(f"Nonexistent command {cmd}!")
    return [0,str(retval)]         
  def _execute(self,S: str):
    #print(S)
    buffer_stack=[""]
    symbol_stack=[]
    command=[]
    result=self.DEFAULT_RETVAL
    curly_mode=0
    def close_brace(start,end):
      nonlocal symbol_stack,buffer_stack
      if len(symbol_stack)==0: raise SyntaxError(f'"{end}" without matching "{start}"!')
      if symbol_stack.pop()!=start: raise SyntaxError(f'Expected "{end}"!')
      return buffer_stack.pop()
    for c in S+"\n":
      assert len(symbol_stack)+1==len(buffer_stack)
      if c in "[({<":
        symbol_stack.append(c)
        buffer_stack.append("")
        if c=="{":curly_mode+=1
      elif c=="}":
        temp=close_brace("{","}")
        curly_mode-=1
        if len(symbol_stack)==0:
          buffer_stack[-1]+=temp
        else:
          buffer_stack[-1]+="{"+temp+"}"
      elif c=="]":
        temp=close_brace("[","]")
        if curly_mode==0:
          output=self._execute(temp)
          if output[0]>0: return output
          buffer_stack[-1]+=output[1]
        else:
          buffer_stack[-1]+="["+temp+"]"
      elif c==")":
        temp=close_brace("(",")")
        if len(symbol_stack)==0:
          buffer_stack[-1]+=temp
        else:
          buffer_stack[-1]+="("+temp+")"
      elif c==">":
        temp=close_brace("<",">")
        if curly_mode==0:
          if temp[0]=="_":
            buffer_stack[-1]+=self.globals[temp]
          else:
            buffer_stack[-1]+=self.variables[temp]
        else:
          buffer_stack[-1]+="<"+temp+">"
      elif len(symbol_stack)==0 and c==" ":
        if len(command)>0 or len(buffer_stack[0])>0:
          command.append(buffer_stack[0])
          buffer_stack[0]=""
      elif len(symbol_stack)==0 and c in ";\n":
        if len(command)>0 or len(buffer_stack[0])>0:
          command.append(buffer_stack[0])
          buffer_stack[0]=""
        output=self._run(command)
        if output[1] is not None:
          result=output[1]
        if output[0]>0:return output
        command=[]
      else:
        buffer_stack[-1]+=c
    return [0,result]
  def execute(self,S=""):
    result=self._execute(S)
    if result[0]==0:return str(result[1])
    elif result[0]==2:raise Exception("'break' statement within outermost script!")
    elif result[0]==3:raise Exception("'continue' statement within outermost script!")
    elif result[0]==4:raise Exception("'return' statement within outermost script!")
    return ""
