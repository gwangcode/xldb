#! /usr/bin/env python3
import sys, os, glob, shlex, re, prompt_toolkit, traceback, fnmatch, io, gc, subprocess

_PrintOut=True
GC_Status=True
Prompt=''
StdOut=sys.stdout

PipeInput=None
ToPipe=False

Quit=False

glbs={} # global var dict
AutoComplete=''
ImportLibs=''
BeginCmd=''
EndCmd=''
FuncLib=[] # Python Function Libraries: .py libraries Dir
ScriptDir=[] # Script Directories: Command Dir
BinPath=os.path.dirname(os.path.realpath(__file__))
PathsSetFilePath=BinPath+'/Paths.set' # Path of Paths.set
      
class fpath: # parse a relative path
  path='' # original string of file path
  
  def __init__(self, path): self.path=path

  def full(self): return os.path.abspath(os.path.expanduser(self.path))

  def __split_file(self):
    f=self.full()
    b=os.path.basename(f)
    return os.path.splitext(b)
  
  def base(self):
    sf=self.__split_file()
    return sf[0]
      
# initialize finished ===========================================================
#class _xldb_sys_void: pass

class _ErrInfo(Exception): pass 
# print out error information for functions & commands
def err(ErrInfo):
  cprint(ErrInfo)
  raise _ErrInfo

def _read_paths_set_file(Path): # read Paths.set into FuncLib and ScriptDir
  global FuncLib, ScriptDir, ImportLibs, BeginCmd, EndCmd, AutoComplete
  P=fpath(Path).full()
  f=open(P)
  L=f.readlines()
  if L:
    for i in L:
      if i:
        i=i.split('#')[0]
        Li=i.split('=')
        if Li[0].strip() == 'LibDir': 
          for i in Li[1].split(';'):
            if i:
              i=i.strip()
              j=i.split('/')
              if j[0]=='@': FuncLib.append(BinPath+'/'+'/'.join(j[1:]))
              else: FuncLib.append(fpath(i).full())

        elif Li[0].strip() == 'ScriptDir': 
          for i in Li[1].split(';'):
            if i:
              i=i.strip()
              j=i.split('/')
              if j[0]=='@': ScriptDir.append(BinPath+'/'+'/'.join(j[1:]))
              else: ScriptDir.append(fpath(i).full())
              
        elif Li[0].strip() == 'Imports': ImportLibs=Li[1].strip()
        elif Li[0].strip() == 'BeginCmd': BeginCmd=Li[1].strip()
        elif Li[0].strip() == 'EndCmd': EndCmd=Li[1].strip()
        elif Li[0].strip() == 'AutoComplete': AutoComplete=Li[1].strip()
      
def _find_file_in_paths(FileName, AbsPath=False): # IsCmd: Search in ScriptDir, not IsCmd: Search in FuncLib
  global ScriptDir
  if AbsPath: 
    try: 
      r=fpath(FileName).full()
      if os.path.isfile(r): return r
    except: return None
  else:
    for Dir in ScriptDir:
      try: r=glob.glob(Dir+'/'+FileName, recursive=True)
      except: r=None
      if r: return r[0]
      else: 
        try:
          r=glob.glob(Dir+'/**/'+FileName, recursive=True)
        except: r=None
        if r: return r[0]

# _PrintOut=True: print objects to screen, print OffObj to $%0 (OffOutVar=0)
# _PrintOut=False: print OffObj to $%0 (OffOutVar=0)
# If OffObj==None: OffObj=objects
# USED
def cprint(*Obj, sep=' ', end='\n', flush=False, PrintIfNotNone=False):
  global _PrintOut, PipeInput, ToPipe
  Print=False
  if PrintIfNotNone:
    if len(Obj)>0:
      if Obj[0] is not None: Print=True
  else: Print=True
  if Print:
    if _PrintOut: 
      if ToPipe: print(*Obj, sep=sep, end=end, flush=flush, file=PipeInput)
      else: print(*Obj, sep=sep, end=end, flush=flush)

class line_parser:
  __String=''
  def __init__(self, String):
    if String[-1] != '\n': String+='\n'
    self.__String=String

  def __quotation_strings(self):
    QuotationPattern='''(?<!\\\\)'.*?(?<!\\\\)'|(?<!\\\\)".*?(?<!\\\\)"''' # '...' or "...", ... means anything between quotations
    p=re.compile(QuotationPattern)
    return [(i.group(),i.span()[0],i.span()[1]) for i in p.finditer(self.__String)]

  def is_inside_quotation(self, MatchObj):
    for i in self.__quotation_strings():
      c, s, e=i
      StartPos=MatchObj.span()[0]
      if StartPos>=s and StartPos<e: return True
    else: return False
  
  def match_all(self, Pattern):
    p=re.compile(Pattern)
    return [(i.group(),i.span()[0],i.span()[1], self.is_inside_quotation(i)) for i in p.finditer(self.__String)] # (content, start_pos, end_pos, is_inside_quotation)

  def sub(self, Pattern, Repl):
    p=re.compile(Pattern)
    self.__String=p.sub(Repl,self.__String)

  def string(self):
    return self.__String

def _parse_script_line(Str):
  L=line_parser(Str)

  def sub_var(m): # $~
    if not L.is_inside_quotation(m): return 'locals()["""'+m.groups()[1]+'"""]'
    else: return m.group()
  L.sub('((?<!\\\\)\${1}\~{1})(\w+?)',sub_var)
  
  def sub_cmd(m): # `. ...`
    if not L.is_inside_quotation(m): return 'cmd(""" '+m.group()[2:-1]+' """, Glbs=locals(), External=_GLB)'
    else: return m.group()
  L.sub('(?<!\\\\)`\.{1}.*?(?<!\\\\)`',sub_cmd)

  def sub_endline_cmd(m): # $. ...
    if not L.is_inside_quotation(m): return 'cmd(""" '+m.group()[2:]+' """, Glbs=locals(), External=_GLB)'
    else: return m.group()
  L.sub('(?<!\\\\)\${1}\.{1}.*?$',sub_endline_cmd)
  
  return L.string()

def _exec_script(FilePathName, Arg, RVar='',Glbs={}): # run cmd script
  
  try: f=open(FilePathName)
  except: cprint('Command '+FilePathName+' not found!')
    
  CmdName=eval(Arg+'[0]', Glbs)
  CmdName=CmdName.split('/')[-1]
  _CmdName=''
  for i in CmdName:
    if re.match('[A-Za-z0-9_]', i): _CmdName+=i
    else: _CmdName+='_'
  CmdName=_CmdName
  
  s=['def __Command_of_'+CmdName+'__(args):\n'] # define __on_run__ function & put in global variables
  raw=f.readlines() # read CMD to raw
  if raw:
    s_external=[]
    InExternal=False
    for i in raw:
      iTemp=i.strip()
      iTemp=iTemp.replace(' ', '')
      
      if iTemp=='!External:Begin': 
        InExternal=True
        continue
      elif iTemp=='!External:End': 
        InExternal=False
        continue
      p=_parse_script_line(i)
      if InExternal: s_external.append(p)
      else: 
        p='  '+p # add indent of 2 spaces
        s.append(p)

    if s[-1][-1] != '\n': s[-1]+='\n'  
    
    try:
      exec(''.join(s_external), Glbs)
      exec(''.join(s), Glbs)
      r=eval('__Command_of_'+CmdName+'__(args)', Glbs)
      exec('del __Command_of_'+CmdName+'__', Glbs)
      
      if RVar: Glbs[RVar]=r
      return r

    except _ErrInfo: pass
    except: 
      etype, value, tb=sys.exc_info()
      e=traceback.format_exception(etype,value, tb)
      prt=False
      for i in e:
        if '<string>' in i: 
          prt=True
          print('Command <'+CmdName+'> error: line '+str(int(i.split(',')[1].split()[1])-1)+' ')
          continue
        if prt: print(i, end='')
   
def _parse_parameter(Parameter, Glbs): # parse cmd line parameters
  
  # = ...
  # == ...
  # other
  if Parameter:
    if Parameter[0] == '=':
      if len(Parameter)>=2:
        if Parameter[1] =='=': # ==...
          if len(Parameter)>2: return Parameter[1:].strip()
          else: return ''
        else: # =...
          if len(Parameter)>1:
            p=_parse_script_line(Parameter[1:])
            try: return eval(p.strip(), Glbs)
            except:
              etype, value, tb=sys.exc_info()
              e=traceback.format_exception(etype,value, tb)
              prt=False
              for i in e:
                if '<string>' in i: 
                  prt=True
                  print('Parameter error: ('+p.strip()+') ', end='')
                  continue
                if prt: print(i, end='')
          else: return ''
      else: return ''
    else: # other
      return Parameter.strip()
  else: return ''

def _remove_double_quotation(Str):
  if Str[0]=='"' and Str[-1]=='"': return Str[1:-1]
  else: return Str

def _run_shell_cmd(CMD, RVar='', Glbs={}):
  global PipeInput, ToPipe
  if PipeInput is not None:
    p = subprocess.Popen(shlex.split(CMD, posix=False), stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)    
    PInput=PipeInput.getvalue()
    stdout = p.communicate(input=PInput.encode())[0]
    PipeInput=None
    r=stdout.decode()
    
  else:
    o=os.popen(CMD)
    r=o.read()

  if RVar: Glbs[RVar]=r
  else: cprint(r, end='')
  return r

def _run_one_line_pycmd(OneLine, Glbs): 
  run_exec=False
  while True: 
    try:
      if run_exec: 
        exec(_parse_script_line(OneLine), Glbs)
        run_exec=False
        break
      else:
        r=eval(_parse_script_line(OneLine), Glbs) 
        cprint(r, PrintIfNotNone=True)
        return r
        
    except _ErrInfo: pass
    except: 
      if run_exec:
        etype, value, tb=sys.exc_info()
        e=traceback.format_exception(etype,value, tb)
        prt=False
        for i in e:
          if '<string>' in i: 
            prt=True
            print('Function error: '+i.split(',')[1], end=' ')
            continue
          if prt: print(i, end='')
        break

      else: 
        run_exec=True
        continue

def split_by_str_out_of_quotation(Str, ByStr=' '):
  L=line_parser(Str)
  s=L.string()
  r=[]
  StartPos=0
  EndPos=len(s)
  for m in re.finditer(ByStr, s):
    if not L.is_inside_quotation(m): 
      EndPos=m.span()[0]
      r.append(s[StartPos:EndPos])
      StartPos=m.span()[1]
  r.append(s[StartPos:])
  return r

# if NoExit=True: ignore EXIT
# The return value is the last command's return value
def cmd(CMD, NoExit=False, Glbs={}, AutoComplete=False, IsTop=False, External={}):
  global glbs, ToPipe, PipeInput, _PrintOut
  RValue=None
  TempPrintOut=_PrintOut
  Glbs.update(glbs)

  if AutoComplete: 
    rvar=None
    return _run_one_cmd(CMD, rvar, NoExit, Glbs=Glbs, AutoComplete=True)
  else:
    
    CmdList=split_by_str_out_of_quotation(CMD, '&&')
    
    LCmdList=len(CmdList)
    Next=0

    for cmd in CmdList:
      Next+=1
      cmd=split_by_str_out_of_quotation(cmd, '#')[0]
      cmd=cmd.strip()
      
      if cmd:
        
        if Next<LCmdList:
          NextCmd=CmdList[Next].strip()
          if len(NextCmd)>2: 
            if NextCmd[:2]=='.|': 
              ToPipe=True
              PipeInput=io.StringIO()

        if cmd[-1]==';':
          TempPrintOut=_PrintOut
          _PrintOut=False
          cmd=cmd[:-1]
          
        if IsTop: Glbs['_GLB']={}
        else: 
          Glbs['_GLB']={}
          Glbs['_GLB'].update(External)
        Glbs['_RTN']=RValue
        
        
        if cmd[0]=='~': 
          rvar, cmd=cmd[1:].split('=',1)
          rvar=rvar.strip()
          cmd=cmd.strip()
        else: rvar=''

        if cmd[0]=='/': RValue=_run_one_line_pycmd(cmd[1:], Glbs=Glbs) # /f=3+5: python one line script
        elif cmd[0]=='.': 
          if cmd[1]=='|': 
            RValue=_run_shell_cmd(cmd[2:], rvar, Glbs=Glbs) # pipe
            PipeInput=None
          else: RValue=_run_shell_cmd(cmd[1:], rvar, Glbs=Glbs)
        else: 
          if cmd[0]=='@': # run a command at a designated path
            AbsPath=True 
            cmd=cmd[1:]
          else: AbsPath=False
        
          RValue=_run_one_cmd(cmd, rvar, NoExit, Glbs=Glbs, AbsPath=AbsPath)
        
        _PrintOut=TempPrintOut

    return RValue
    
def _run_one_cmd(CMD, RVar='', NoExit=False, Glbs={}, AutoComplete=False, AbsPath=False): # parse command line and pass command to run_script
  global _PrintOut, Quit, StdOut
  
  RawArg=[]
  CMD=CMD.strip()
  
  if CMD=='EXIT' and not NoExit: Quit=True
  else:
    RawArg=shlex.split(CMD, posix=False)
    RawArg=list(map(_remove_double_quotation,RawArg)) # if "...": remove quotations to become ..., if '...', do not remove quotations to be '...'
    if AutoComplete: args=RawArg
    else: args=[_parse_parameter(i, Glbs) for i in RawArg]
    Glbs['args']=args
    CmdPath=_find_file_in_paths(args[0], AbsPath=AbsPath) 
    if CmdPath: return _exec_script(CmdPath, 'args',RVar, Glbs=Glbs) # return None if successfully run cmd
    else: cprint('Command '+args[0]+' not found!')
      

def gvars():
  global glbs
  return glbs

def setprint(PrintOut=True):
  global _PrintOut
  _PrintOut=PrintOut

def setgc(GC=True):
  global GC_Status
  GC_Status=GC
  return GC

# set up prompt
# default: >
# prompt('abc')-> Prompt='abc' -> Prompt becomes abc>
def prompt(Str, CWD=True):
  global Prompt
  F=''
  if CWD: F='{'+fpath(os.getcwd()).base()+'}'
  Prompt=F+Str

def bindir():
  global BinPath
  return BinPath

def initsys(): # initialize the system
  global PathsSetFilePath, FuncLib, glbs, ImportLibs
  _read_paths_set_file(PathsSetFilePath) # read paths.set
  for i in FuncLib: sys.path.append(i) # add function library directories from FuncLib
  import builtins
  builtins.cprint=glbs['cprint']=globals()['cprint']
  builtins.cmd=glbs['cmd']=globals()['cmd']
  builtins.gvars=glbs['gvars']=globals()['gvars']
  builtins.err=glbs['err']=globals()['err']
  builtins.prompt=glbs['prompt']=globals()['prompt']
  builtins.setprint=glbs['setprint']=globals()['setprint']
  builtins.setgc=glbs['setgc']=globals()['setgc']
  #builtins.GLB=globals()['GLB']
  builtins.bindir=globals()['bindir']
  exec('import '+ImportLibs, glbs)
  prompt('')
  return ImportLibs

class XldbCompleter(prompt_toolkit.completion.Completer):
  Dir=''
  # [n, (sub, display), (sub, display), ...]
  def __cmd_autocomplete(self, word): # /abc/de
    global AutoComplete
    if AutoComplete: 
      try: r=cmd(AutoComplete+' '+word, AutoComplete=True)
      except:
        try: r=cmd(AutoComplete+' '+word+"'", AutoComplete=True)
        except: 
          try: r=cmd(AutoComplete+' '+word+'"', AutoComplete=True)
          except: return [], 0
      return r[1:], r[0]
    else: return [], 0

  def __match_paths(self,word):
    cwd=os.getcwd()
    if word[-1]=="'" or word[-1]=='"': word=word[:-1]
    if word.strip():
      try: raw=shlex.split(word, posix=False)[-1]
      except: 
        try: raw=shlex.split(word+"'", posix=False)[-1]
        except: raw=shlex.split(word+'"', posix=False)[-1]

      if raw[0]=="'" or raw[0]=='"': raw=raw[1:-1]
      
      FirstSlash=False
      if raw.startswith('/'): FirstSlash=True
      wordlist=raw.split('/')
      BasePath='/'.join(wordlist[:-1])
      if FirstSlash: BasePath='/'+BasePath
      ResidueWord=wordlist[-1]
      self.Dir=fpath(BasePath).full()
      if os.path.isdir(self.Dir): os.chdir(self.Dir)
      r=[]
      try:
        rule = re.compile(fnmatch.translate(ResidueWord+'*'), re.IGNORECASE)
      except:
        rule = re.compile(fnmatch.translate('*'), re.IGNORECASE)
      try: Names=[name for name in os.listdir(self.Dir) if rule.match(name)]
      except: Names=[]
      for i in Names: r.append(i)
      os.chdir(cwd)
      if ResidueWord: return (r,len(ResidueWord))
      else: return (r, 0)
    else: return ([], 0)
    
  def get_completions(self, document, complete_event):
    if document.text:
      r1, n1=self.__cmd_autocomplete(document.text_before_cursor)
      r,n=self.__match_paths(document.text_before_cursor)

      for i in tuple(r1): 
        if type(i) is tuple or type(i) is list: 
          if i[0]: yield prompt_toolkit.completion.Completion(i[0], start_position=-n1, display=i[1])
        else: yield prompt_toolkit.completion.Completion(i, start_position=-n1)
      for i in tuple(r): yield prompt_toolkit.completion.Completion(i, start_position=-n)

def main_loop():
  global Quit, Prompt, BeginCmd, EndCmd, glbs, GC_Status
  Glbs={**glbs}
  historyText=prompt_toolkit.history.InMemoryHistory()
  while not Quit:
    Session=prompt_toolkit.PromptSession(history=historyText,completer=XldbCompleter())
    while True:
      try:
        CMD=Session.prompt(Prompt+'>', auto_suggest=prompt_toolkit.auto_suggest.AutoSuggestFromHistory())
      except KeyboardInterrupt:
        continue
      except EOFError:
        break
      else:
        break
    if CMD:
      try: 
        if BeginCmd: cmd(BeginCmd, Glbs=Glbs, IsTop=True)
        cmd(CMD, Glbs=Glbs, IsTop=True)
        if EndCmd: cmd(EndCmd, Glbs=Glbs, IsTop=True)
        if GC_Status: gc.collect()
      except Exception: 
        try: 
          if EndCmd: cmd(EndCmd, Glbs=Glbs)    
        except: traceback.print_exc()

        traceback.print_exc()

def main():
  initsys()
  if not sys.stdin.isatty():
      tunnel_read=sys.stdin.read()
      cmd(tunnel_read)
  else: main_loop()

if __name__ == '__main__': main()

