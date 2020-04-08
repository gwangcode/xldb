#! /Library/Frameworks/Python.framework/Versions/3.6/bin/python3
import re, curses as cur, datatype as dt

def get_chr_width(chr):
  """Return the screen column width for unicode ordinal o."""
  widths = (
  (126,    1), (159,    0), (687,     1), (710,   0), (711,   1), 
  (727,    0), (733,    1), (879,     0), (1154,  1), (1161,  0), 
  (4347,   1), (4447,   2), (7467,    1), (7521,  0), (8369,  1), 
  (8426,   0), (9000,   1), (9002,    2), (11021, 1), (12350, 2), 
  (12351,  1), (12438,  2), (12442,   0), (19893, 2), (19967, 1),
  (55203,  2), (63743,  1), (64106,   2), (65039, 1), (65059, 0),
  (65131,  2), (65279,  1), (65376,   2), (65500, 1), (65510, 2),
  (120831, 1), (262141, 2), (1114109, 1),)
  x=ord(chr)
  if x == 0xe or x == 0xf:
      return 0
  for num, wid in widths:
      if x <= num:
          return wid
  return 1

def split_by_width_once(Str, Width, SpaceSupplement=False):
  s=''
  if str_width(Str)<=Width:
    if SpaceSupplement: return Str+(Width-str_width(Str))*' '
    else: return Str
  else:
    for i in range(1,len(Str)+1):
      s=[Str[:i], Str[1:]]
      if str_width(s[0])>Width:
        s=[Str[:i-1],Str[i-1:]]
        if str_width(s[0])<=Width: 
          if SpaceSupplement: s[0]+=(Width-str_width(s[0]))*' '  
        return s

def split_by_width(Str, Width, SpaceSupplement=False):
  r=[]
  s=split_by_width_once(Str,Width,SpaceSupplement)
  if type(s) is type(''): return [s]
  else:
    while True:
      r.append(s[0])
      rest=s[1]
      s=split_by_width_once(rest,Width,SpaceSupplement)
      if type(s) is type(''):
        r.append(s)
        return r

def str_width(Str):
  n=0
  if Str:
    for i in Str: n+=get_chr_width(i)
  return n


def str_mode(Mode):
  if Mode=='altcharset': return cur.A_ALTCHARSET #
  elif Mode=='blink': return cur.A_BLINK
  elif Mode=='bold': return cur.A_BOLD ##
  elif Mode=='dim': return cur.A_DIM 
  elif Mode=='invis': return cur.A_INVIS #
  elif Mode=='normal': return cur.A_NORMAL ##
  elif Mode=='protect': return cur.A_PROTECT #
  elif Mode=='reverse': return cur.A_REVERSE
  elif Mode=='standout': return cur.A_STANDOUT
  elif Mode=='underline': return cur.A_UNDERLINE ##
  elif Mode=='horizontal': return cur.A_HORIZONTAL #
  elif Mode=='left': return cur.A_LEFT #
  elif Mode=='low': return cur.A_LOW #
  elif Mode=='right': return cur.A_RIGHT #
  elif Mode=='top': return cur.A_TOP #
  elif Mode=='vertical': return cur.A_VERTICAL #
  elif Mode=='chartext': return cur.A_CHARTEXT #
  else: return cur.A_NORMAL

# grab property value from s=<textbox id=3 leftx=5>
# grab_property('id', s) => '3'
# returns None when no such property found
def grab_property(property, s):
  p=re.search('('+property+'){1}([ ]*)(\=){1}([ ]*)([A-Za-z\/\d\.\+\-]+)',s)
  if p: return p.groups()[4]

# '<mode=3 line=-0.5 col=4|hello world>' => ['<mode=3 line=-0.5 col=4', 'hello world>']
# '<mode=3 line=-0.5 col=4>' => ['<mode=3 line=-0.5 col=4>']
def split_text_bracket(s): return re.split('(?<!\\\\)\|{1}', s)

# s='<mode=3 line=-0.5 col=4|hello world>', grab_property_str(s) => 'mode=3 line=-0.5 col=4'
# # s='<mode=3 line=-0.5 col=4>', grab_property_str(s) => mode=3 line=-0.5 col=4
def grab_property_str(s):
  p=split_text_bracket(s)
  if len(p)==1: return p[0][1:-1].strip()
  else: return p[0][1:].strip()

# change/add property
# s='<mode=3 line=-0.5 col=4|hello world>', write_property('forecolor', 5, s) => '<mode=3 line=-0.5 col=4 forecolor=5|hello world>'
# s='<mode=3 line=-0.5 col=4>', write_property('forecolor', 5, s) => '<mode=3 line=-0.5 col=4 forecolor=5>'
def write_property(property, pvalue,s):
  p=split_text_bracket(s)
  if len(p)==1: # <mode=3 line=-0.5 col=4>
    prop=p[0][1:-1]
    text=None
  else:  # <mode=3 line=-0.5 col=4|hello world>
    prop=p[0][1:]
    text=p[1][:-1]

  pv=grab_property(property, prop)
  if pv: 
    r=''
    for i in prop.split():
      if i.split('=')[0].strip()==property.strip(): r+=' '+property.strip()+'='+str(pvalue).strip()
      else: r+=' '+i.strip()
    prop=r

  else: prop+=' '+property+'='+str(pvalue) # property doesn't exist

  if text is not None: return '<'+prop.strip()+'|'+text+'>'
  else: return '<'+prop.strip()+'>'

# remove property
# s='<mode=3 line=-0.5 col=4|hello world>', _remove_property('col', s) => '<mode=3 line=-0.5|hello world>'
def remove_property(property, s):
  p=split_text_bracket(s)
  if len(p)==1: # <mode=3 line=-0.5 col=4>
    prop=p[0][1:-1]
    text=None

  else:  # <mode=3 line=-0.5 col=4|hello world>
    prop=p[0][1:]
    text=p[1][:-1]

  pv=grab_property(property, prop)
  if pv: 
    r=''
    for i in prop.split():
      if i.split('=')[0].strip()!=property.strip(): r+=' '+i.strip()
    prop=r

  if text: return '<'+prop.strip()+'|'+text+'>'
  else: return '<'+prop.strip()+'>'

# grab text to bracket
# s='<mode=3 line=-0.5 col=4|hello world\|>', _grab_text(s) => 'hello world|'
def grab_text(s):
  p=split_text_bracket(s)
  if len(p)==2: return re.sub('(\\\\{1})','',p[1][:-1])
  else: return ''

def grab_text_width(s):
  t=grab_text(s)
  return str_width(t)

# change text to bracket
# s='<mode=3 line=-0.5 col=4|hello world>',  _write_text('I love you',s) => '<mode=3 line=-0.5 col=4|I love you>'
def write_text(text, s):
  p=split_text_bracket(s)
  if len(p)==2: 
    text=re.sub('(\>{1})','\\\\>',text)
    text=re.sub('(\<{1})','\\\\<',text)
    text=re.sub('(\|{1})','\\\\|',text)
    return p[0]+'|'+text+'>'

# s='<mode=3 line=-0.5 col=4|hello world! I love you so much!>', _split_bracket_by_width(10, s) => ['<mode=3 line=-0.5 col=4|hello worl>', '<mode=3 line=-0.5 col=4|d! I love >', '<mode=3 line=-0.5 col=4|you so muc>', '<mode=3 line=-0.5 col=4|h!>']
def split_bracket_by_width(width, s, SpaceSupplement=False, Once=False):
  p=grab_property_str(s)
  t=grab_text(s)
  r=[]
  pre_col=None
  if Once: tList=split_by_width_once(t, width, SpaceSupplement)
  else: tList=split_by_width(t,width,SpaceSupplement)
  if type(tList) is str: tList=[tList]
  for i in tList:
    br='<'+p+'|>'
    br=write_text(i,br)
    col=grab_property('col',br)
    if col is not None: 
      col=dt.num(col)
      if type(col) is int: 
        if pre_col is None: 
          br=write_property('col', col, br)
          pre_col=col
        else: br=write_property('col', pre_col,br )
        pre_col+=str_width(i)
        
      elif type(col) is float: 
        if pre_col is None: 
          br=write_property('col', col, br)
          pre_col=0.1
        else: br=write_property('col', 0.1, br)
    r.append(br)

  return r
  
# int or float a string, returns None if failed 
def num_str(s):
  try: 
    f=float(s)
    i=int(f)
    if i==f: return i
    else: return f
  except:
    return None

# true => True, false => False
# else retunrs None
def bool_str(s):
  if s=='True': return True
  elif s=='False': return False
  else: return None

# 'None' => None
def none_str(s):
  if s=='None': return None
  else: return s


# input:
# <cury=1 curx=2 curvisible=true>
# <line=0 col=0 forecolor=2 backcolor=5 mode=UNDERLINE|Hello world!>
# <line=1 col=0 forecolor=2 backcolor=5 mode=BOLD|I love you>
# 
# output: print on screen

class styledtext:
  __InList=[] # input
  __screen=None # screen object
  __ColorPair=[0]

  
  def __init__(self, Screen): self.__screen=Screen # List=['<textbox>', '<|hellow how are you>', "<|I don't know what to do>", '</textbox>']
    
  def __compile_str_text(self, Text): self.__InList=re.findall('((?<!\\\\)<{1}.*?(?<!\\\\)\>{1})', Text) # find out <|>, <|> ..., ignore plain 'abc' ...

  # <line col forecolor backcolor mode>
  #<|Hello World> => <line=1 col=2 forecolor=-1 backcolor=2 mode=UNDERLINE|Hello World>
  def __complete_text(self):
    line='0'
    col='0'
    forecolor='-1'
    backcolor='-1'
    mode='NORMAL'
    text_width=0

    if len(self.__InList)>=2:
      pLine=grab_property('line',self.__InList[1])
      if not pLine: self.__InList[1]=write_property('line', line,self.__InList[1])
      
      pCol=grab_property('col', self.__InList[1])
      if not pCol: self.__InList[1]=write_property('col', col, self.__InList[1])
      
      pForecolor=grab_property('forecolor', self.__InList[1])
      if pForecolor: forecolor=pForecolor
      else: self.__InList[1]=write_property('forecolor', forecolor, self.__InList[1])

      pBackcolor=grab_property('backcolor', self.__InList[1])
      if pBackcolor: backcolor=pBackcolor
      else: self.__InList[1]=write_property('backcolor', backcolor, self.__InList[1])

      pMode=grab_property('mode', self.__InList[1])
      if pMode: mode=pMode
      else: self.__InList[1]=write_property('mode', mode, self.__InList[1])

      text_width=str_width(grab_text(self.__InList[1]))

    if len(self.__InList)>=3:
      for i in range(2, len(self.__InList)):
        preline=line
        pLine=grab_property('line',self.__InList[i])
        if pLine:
          l=num_str(pLine)
          if type(l) is float: line=str(int(line)+int(l))
          else: line=str(l)
        self.__InList[i]=write_property('line', line, self.__InList[i])
        
        pCol=grab_property('col', self.__InList[i])
        if pCol: 
          l=num_str(pCol)
          if type(l) is float: 
            if preline==line: col=str(int(col)+text_width+int(l))
            else: col=str(int(l))
          else: col=str(l)
        else:
          if preline==line: col=str(int(col)+text_width)
          else: col='0'
        self.__InList[i]=write_property('col', col, self.__InList[i])
        
        pForecolor=grab_property('forecolor', self.__InList[i])
        if pForecolor: forecolor=pForecolor
        else: self.__InList[i]=write_property('forecolor', forecolor, self.__InList[i])

        pBackcolor=grab_property('backcolor', self.__InList[i])
        if pBackcolor: backcolor=pBackcolor
        else: self.__InList[i]=write_property('backcolor', backcolor, self.__InList[i])

        pMode=grab_property('mode', self.__InList[i])
        if pMode: mode=pMode
        else: self.__InList[i]=write_property('mode', mode, self.__InList[i])

        text_width=str_width(grab_text(self.__InList[i]))

  # set color pair
  def __set_color_pair(self, ForeColor, BackColor): # if color pairs >256 (255 is the maxt color number), the color pair is ineffective 
    CurColor=(ForeColor, BackColor)
    if CurColor[0]<0: return 0
    if CurColor in self.__ColorPair: return self.__ColorPair.index(CurColor)
    else:
      if len(self.__ColorPair)<=256: 
        self.__ColorPair.append(CurColor)
        return len(self.__ColorPair)-1

  # return attribute for addstr    
  def __set_attr(self, StrMode, ForeColor, BackColor):
    self.__CurStrMode=StrMode
    if ForeColor<0: return StrMode+cur.color_pair(0)
    else:
      CurColor=self.__set_color_pair(ForeColor,BackColor)
      ForeColor, BackColor=self.__ColorPair[CurColor]
      cur.init_pair(CurColor,ForeColor,BackColor)  
      return StrMode+cur.color_pair(CurColor)
  
  
  def __addtext(self, text):
    winSize=self.win_size()
    if winSize: 
      height, width=winSize # window size
      y=num_str(grab_property('line',text))
      if y<height:
        x=num_str(grab_property('col',text))
        Txt=grab_text(text)
        dx=width-x
        if dx>0:
          s=split_by_width_once(Txt, dx, SpaceSupplement=True)
          if type(s) is str: pTxt=Txt
          else: pTxt=s[0]
          StrMode=0
          for m in grab_property('mode',text).split('+'):
            if m: StrMode+=str_mode(m)
          ForeColor=num_str(grab_property('forecolor',text))
          BackColor=num_str(grab_property('backcolor',text))
          try: 
            self.__screen.addstr(y, x, pTxt, self.__set_attr(StrMode, ForeColor, BackColor))
            #YY, XX=self.__screen.getyx()
            #self.__screen.addstr(str(YY)+' '+str(XX))
          except:
            CursorY, CursorX=self.__screen.getyx()
            #print('dx: '+str(dx)+' '+'wid: '+str(width))
            self.__screen.move(CursorY, width-1)
            
    
  def __set_cursor_pos(self):
    lines, cols=self.win_size()
    if bool_str(grab_property('curvisible', self.__InList[0])): # cursor visible
      cur.curs_set(1)
      y, x=self.__screen.getyx()
      xset=num_str(grab_property('curx', self.__InList[0]))
      yset=num_str(grab_property('cury', self.__InList[0]))
      if xset: x=xset
      if yset: y=yset
      y=min(y, lines-1)
      x=min(x, cols-1)
      self.__screen.move(y, x)

    else: cur.curs_set(0) # cursor invisible
    return self.__screen.getyx()

  # return lines, cols
  def win_size(self): return self.__screen.getmaxyx()

  # return cursor position y,x
  def cursor_pos(self): self.__screen.getyx()


  def complete_text(self, Text, AsList=False):
    self.__compile_str_text(Text)
    self.__complete_text()
    if AsList: return self.__InList
    else: return ''.join(self.__InList)
    
  def print(self, Text): # generate the output text
    self.__compile_str_text(Text)
    self.__complete_text()
    #print(self.__InList)
    self.__screen.clear()
    self.__ColorPair=[0]
    for i in self.__InList[1:]: self.__addtext(i)
    #cur.curs_set(1)
    self.__set_cursor_pos()


class loop:
  scr=None
  quit=False

  def __init__(self, scr=None): 
    if scr: self.scr=scr
    else: self.scr=cur.initscr()
  
  def run(self, BeginFunc=None, Func=None, EndFunc=None):
    # Initiate Screen
    #stdscr = cur.initscr()
    cur.start_color()
    cur.use_default_colors()
    cur.noecho()
    cur.cbreak()
    self.scr.keypad(True)
    self.scr.clrtoeol()
  
    self.scr.nodelay(True)
    
    KeyInput=-1
    
    if BeginFunc: BeginFunc()
      
    while not self.quit:
      
      try: 
        KeyInput=self.scr.get_wch()
        self.scr.nodelay(True)
      except: 
        KeyInput=-1
        self.scr.nodelay(False)

      if Func: Func(KeyInput)
        
    if EndFunc: EndFunc()
      
    # Quit Screen
    cur.nocbreak()
    self.scr.keypad(False)
    cur.echo()
    cur.endwin() 




def key_code():
  text=['<curvisible=True>']
  l=loop()
  t=styledtext(l.scr)
  def _key_code(key=''):
    if type(key) is type(0): 
      if key>=0: return str(key)
    else: return str(ord(key))
    
  def handle_key(Key):
    
    if type(Key) is int:
      if Key>=0: text[0]='<curvisible=True><|'+str(str(Key))+'>'
    else:
      if Key=='\n': l.quit=True
      else: text[0]='<curvisible=True><|'+str(ord(Key))+'>'
    t.print(text[0])
    
  l.run(Func=handle_key)
  


def color_table():
  text=['<>']
  n=255
  for i in range(16): 
    for j in range(16):
      if n==1: text[0]+='<line='+str(i)+' forecolor=0 backcolor='+str(n)+'| '+str(n)+' >'
      else: text[0]+='<line='+str(i)+' forecolor=1 backcolor='+str(n)+'| '+str(n)+' >'
      n-=1
  text[0]+='<line=2.1 forecolor=-1|Press Enter to quit...>'
  

  l=loop()
  t=styledtext(l.scr)
  
  def handle_key(Key):
    t.print(text[0])
    if Key=='\n': l.quit=True
    
  l.run(Func=handle_key)
'''

lp=loop()
#sample='<|><forecolor=40 backcolor=50|我想说这间香港的茶餐厅是火了，原因你们可以在画面中看到，茶餐厅的正面高高悬挂了一面国旗，旁边还有一些小国旗。><line=2.1 |之前这间茶餐厅的生意是没有那么火爆的，就是在公开撑警之后才有的那么好生意。><line=1.1|差不多开了五十一年了，老板说了，五十一年来生意最好的时候就是现在，就是自己撑警之后这生意就是五十一年来最好的一次。>  <line=2.1|其实这不是生意不生意的事儿，这是底线，这是爱国的问题。为什么生意突然变得那么好？因为人家老板是一个爱国的人，身为爱国的人那做出来的东西能差到哪去？再说了，人家也都已经公开撑警了，所以顾客肯定要减少一些，因为其中有顾客肯定是港乱分子。><line=1.1|在这种情况下如果说那些爱国的人士在不去支持一下人家的生意，那就真的别干了。所以啊，去的 也都是一些爱国的人。 ><line=1.2 col=1 mode=BOLD UNDERLINE forecolor=80 backcolor=255 |Hello World what do you want><mode=NORMAL forecolor=-1|I love you so much><line=2.2 col=6.1 |I like you so much>'
#sample2='<|While the news channel has numerous affiliates, CNN primarily broadcasts from 30 Hudson Yards in New York City, and studios in Washington, D.C. and Los Angeles. Its headquarters at the CNN Center in Atlanta is only used for weekend programming. CNN is sometimes referred to as CNN/U.S. (or CNN Domestic)[5] to distinguish the U.S. channel from its international sister network, CNN International.> <line=1.1|The network is known for its dramatic live coverage of breaking news, some of which has drawn criticism as overly sensationalistic, and for its efforts to be nonpartisan, which have led to accusations of false balance.[6][7][8][9]> <line=1.1|As of September 2018, CNN has 90.1 million television households as subscribers (97.7% of households with cable) in the United States.[10]>'
#sample3='<|本 HOWTO 没有涵盖一些高级主题，例如 screen-scraping 或从 xterm 实例捕获鼠标 events。但是 curses 模块的 Python library 页面现在非常完整。你应该浏览它。> <line=1.1|如果你对任何 ncurses 入口点的详细行为有疑问，请查阅 curses implementation 的手册页，无论是 ncurses 还是专有的 Unix 供应商。手册页将记录任何怪癖，并提供所有可用的功能，属性和ACS_*字符的完整列表。> <line=1.1|因为 curses API 太大了，所以 Python 接口不支持某些函数，不是因为它们难以实现，而是因为还没有人需要它们。随意添加它们，然后提交补丁。另外，我们还没有支持与 ncurses 相关的菜单 library;随意添加。>'
#sample4='<|我想说这间香港的茶餐厅是火了，原因你们可以在画面中看到，茶餐厅的正面高高悬挂了一面国旗，旁边还有一些小国旗。>'
t=styledtext(lp.scr)


def bf():
  t.print(sample)
 
def handle_key(Key):
  bf()
  if Key=='q':
    lp.quit=True

lp.run(Func=handle_key)

'''




