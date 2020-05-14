import os, glob, re, string, openpyxl as xl, copy

# store wb objects
wbset={}
active=''

class wb:
  p=None # path
  o=None # wb object/readonly object
  d=None # write only object

  def __init__(self, obj, path='.'):
    self.o=obj
    self.p=path
  
  def is_writeonly(self): return bool(self.d)

'''
Parse a relative path: ~/Documents/abc.xyz, if abc.xyz is not a directory
.Full='/Users/Darius/Documents/abc.xyz'
.Path='/Users/Darius/Documents'
.File='abc'
.Extension='.xyz'
IsDir=False

Parse a relative path: ~/Documents/abc, if abc is a directory
.Full='/Users/Darius/Documents/abc'
.Path='/Users/Darius/Documents'
.File='abc'
.Extension=''
.IsDir=True
'''
class File_Path_Parser: # parse a relative path
  Full='' # full absolute path
  Path='' # full absolute path up until the directory
  File='' # file base name
  Extension='' # file extension name
  Parts=[] # parts of the Path e.g. Path='abc/def/ghi' => ['abc', 'def', 'ghi']
  IsDir=False # whether the file is a directory
  def __init__(self, Path):
    self.Full=os.path.abspath(os.path.expanduser(Path))
    self.Path=os.path.dirname(self.Full)
    Base=os.path.basename(self.Full)
    self.File, self.Extension=os.path.splitext(Base)
    self.IsDir=os.path.isdir(self.Full)
    self.Parts=Path.split('/')

  def exists(self, Full=True): # check if the Full/Path exists
    if Full: return os.path.exists(self.Full) # Is Full existing
    else: return os.path.exists(self.Path) # Is the path directory existing

'''
/Users/Darius/Documents/ consists of 2 files: abc.xyz, ghi.txt
x=Glob_Parser('~/Documents/*') will return
x.Paths=[File_Path_Parser Object 1, File_Path_Parser Object 2]
x.Paths[0].Full='/Users/Darius/Documents/abc.xyz'
x.Paths[0].Path='/Users/Darius/Documents'
x.Paths[0].File='abc'
x.Paths[0].Extension='.xyz'
x.Paths[0].IsDir=False

x.Paths[1].Full='/Users/Darius/Documents/ghi.txt'
x.Paths[1].Path='/Users/Darius/Documents'
x.Paths[1].File='ghi'
x.Paths[1].Extension='.txt'
x.Paths[1].IsDir=False
'''
# Parse a path with *
class Glob_Parser:
  Paths=[]
  def __init__(self, Path):
    self.Paths=[]
    P=File_Path_Parser(Path)
    for i in glob.glob(P.Full, recursive=True): self.Paths.append(File_Path_Parser(i))

# ~/Documents -> full path
def fpath(Path): return File_Path_Parser(Path).Full

# find files
# ~/Documents/**/* -> [List of found files]
def findfiles(Path): return [i.Full for i in Glob_Parser(Path).Paths]

#CMD abc def .KEYW1 .KEYW2 usd efu
#abc, def, efu: free parameters
#.KEYW1: key word w/o a parameter
#.KEYW2: key word w/ a parameter
#input: ['abc', 'def', '.KEYW1', '.KEYW2', 'usd', 'efu']
#output: opts=[['KEYW1'], ['KEYW2', 'usd']], free=['abc', 'def', 'efu']
#pkey: key word list for key words w/ a parameter, e.g. pkey=['KEYW2']
#nkey: key word list for key words w/o a parameter, e.g. nkey=['KEYW1']
def parameter_parse(ArgList, pkey=[], nkey=[]):
  opts=[]
  free=[]
  L=len(ArgList)
  n=0
  while n<L:
    para=ArgList[n]
    if n+1<L: wpara=ArgList[n+1]
    else: wpara=''
    if type(para) is str:
      if para.startswith('.'): # possible a key word
        para=para[1:]
        if para in pkey: # para is a key word with a parameter
          opts.append((para, wpara))
          n+=1
        elif para in nkey: opts.append(tuple([para])) # para is a key word w/o a parameter
        else: free.append(para) # not a key word, goes to free    
      else: free.append(para) # not a key word, goes to free
    else: free.append(para) # not a str, goes to free
    n+=1
  
  return opts, free

# parse ?: any one char, *: any number of chars
# abc* -> ^abc.+$
# a?c -> ^a.{1}c$
def name_wildcard(Str):
  Str=Str.replace('?', '.{1}')
  Str=Str.replace('*', '.+?')
  return '^'+Str+'$'

# open workbook list:
def wblist():
  global wbset
  return wbset.keys()

# list sheet names in wb
def shlist(WbTag):
  wkbk=split_wbname(WbTag)[0]
  if wkbk in wblist(): return wbo(wkbk).sheetnames

# workbook class
def wbcls(WbTag): 
  global wbset
  wkbk=split_wbname(WbTag)[0]
  if wkbk in wblist(): return wbset[wkbk]

# workbook object
def wbo(WbTag): 
  global wbset
  wb=split_wbname(WbTag)[0]
  if wb in wblist(): return wbset[wb].o
  
# workbook path
def wbp(WbTag):
  global wbset
  wb=split_wbname(WbTag)[0]
  if wb in wblist(): return wbset[wb].p

# workbook names

def col2num(col): # column_name: A,B,C,...,Z,AA,AB,...
    num = 0
    for c in col:
        if c in string.ascii_letters:
            num = num * 26 + (ord(c.upper()) - ord('A')) + 1
    return num

def num2col(n):
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string


# Workbook/Sheet/Col -> [Wrokbook, Sheet, Col]
# /wb/sheet/col
# / -> the root >
# /. -> the current wb
# /./. -> the current sheet: /wb/sheet

def split_wbname(Str):
  global active
  wa, sa=_split_wbname(active)[:2]
  if Str.strip()=='/': return (None, None, None)
  else:
    if Str.startswith('/'): 
      a, b, c=_split_wbname(Str[1:])
      if a=='.': a=wa
      if b=='.': b=sa
      return (a, b, c)
    else:
      a, b, c=_split_wbname(Str)
      if not wa: return (a, b, c) #>
      else:
        if not sa: return (wa, a, b) # wa>
        else: return (wa, sa, a) # wa/sa

def _split_wbname(Str): 
  r=list(Str.split('/'))+[None, None]
  return r[:3]

# w -> /w
# w, s -> /w/s
# w, s, c -> /w/s/c
def compose(w, s=None, c=None):
  if c is not None: return '/'+w+'/'+s+'/'+c
  elif s is not None: return '/'+w+'/'+s
  else: return '/'+w

# (Name, Col, Row)
def _single_cell_name(Str):
  cm=Str.strip().split('.')
  lcm=len(cm)
  Name=None 
  Col=None 
  Row=None 
  if lcm==1: # no .
    m=re.match('^(-[A-Za-z]+|[A-Za-z]*)(-[0-9]+|[0-9]*)$',cm[0])
    if m: Col, Row=m.groups()
  elif lcm==2: # Student.A2
    if cm[0]: Name=cm[0]
    m=re.match('^(-[A-Za-z]+|[A-Za-z]*)(-[0-9]+|[0-9]*)$',cm[1])
    if m: Col, Row=m.groups()
  return Name, Col, Row

def exheader_col(Workbook, Sheet, Header=None, Col=None):
  L=headerlist(compose(Workbook, Sheet))

  if Header or Col:
    if Header in (None, ''): # Col to header
      if Col.startswith('-'):
        MCol=maxcol(compose(Workbook, Sheet))
        Col=col2num(Col[1:])
        Col=num2col(max(1, MCol+1-Col))

      for i in L:
        iL=i.split('.')
        if len(iL)==1: 
          col=iL[0]
          name=None #############
        else: name, col=iL[:2]
        if Col.strip()==col.strip(): return name, col
      return None, Col

    elif Col in (None, ''): # Header to Col
      
      for i in L:
        iL=i.split('.')
        if len(iL)==1: 
          col=iL[0]
          name=''
        else: name, col=iL
        if Header.strip()==name.strip(): return name, col
      return Header, None

    else: return Header, Col # neither is None
  
  else: return None, None


# Str: /abc/def/Student1 ...
# Output: (Student, A, 1, Gender, C, 8)
def cellname(Str):
  Str=Str.strip()
  w, s, c=split_wbname(Str)
  n1=c1=Row1=n2=c2=Row2=None
  if c: 
    cL=c.split(':')
    lcL=len(cL)
    if lcL>=1 and cL[0]: # No :
      Name1, Col1, Row1=_single_cell_name(cL[0])
      n1, c1 =exheader_col(w, s, Name1, Col1)
      
    if lcL==2: # w/ :
      #Name1, Col1, Row1=_single_cell_name(cL[0])
      if cL[1]: Name2, Col2, Row2=_single_cell_name(cL[1])
      else: Name2, Col2, Row2=_single_cell_name(num2col(maxcol(compose(w,s)))+str(maxrow(compose(w,s))))
      #n1, c1 =exheader_col(w, s, Name1, Col1)
      n2, c2 =exheader_col(w, s, Name2, Col2)

  return n1, c1, Row1, n2, c2, Row2

# check if name is legal: begin with _A-Za-z and containing only _A-Za-z0-9
def legal_name(Str): return(bool(re.match('^[A-Za-z_]{1}\w*$', Str)))

# Student. -> Student
# Student -> None
def colname(Str):
  r=Str.split('.')[0]
  if legal_name(r): return r
  else: return None

# workbook functions:

# open workbook exists
def wb_exists(WbTag):
  wb=split_wbname(WbTag)[0]
  return wb in wblist()

# sheet obj
def shto(SheetPath):
  wkbk, sheet, cell=split_wbname(SheetPath)
  return wbo(wkbk)[sheet]

# cell obj
def cello(CellPath):
  wb, sheet, cell=split_wbname(CellPath)
  return wbo(wb)[sheet][cell]

# new sheet
def new_sheet(Sheet, Position=None):
  wkbk, sheet=split_wbname(Sheet)[:2]
  if sheet not in shlist(Sheet):
    wbo(wkbk).create_sheet(sheet, Position)
    return  Sheet

# remove sheet
# remove_sheet('w/s')
def remove_sheet(Path):
  w, s, c=split_wbname(Path)
  if w in wblist(): 
    if s in shlist(w): del wbo(w)[s]

# read data
# read('wb/sheet/A'): read col A
# read('wb/sheet/1'): read row 1
# read('wb/sheet/A1'): read cell A1
# read('wb/sheet/A1:B2'): read range from A1 to B2
# read('wb/sheet/A:B'): read cols A & B
# read('wb/sheet/1:2'): read rows 1 & 2
def read(CellPath, ValueOnly=True):
  wkbk, sheet, cell=split_wbname(CellPath.strip())
  data=shto(CellPath)[cell]
  if ValueOnly:
    if type(data) is tuple:
      r=[]
      for row in data:
        if type(row) is tuple: r.append(tuple([i.value for i in row]))
        else: r.append(row.value)
      return tuple(r)
    else: return data.value
  else: return data

# A1 -> [A, 1]
def split_cell_str(Str): return re.search('([A-Za-z\.]*)([0-9]*)',Str).groups()

# max col
def maxcol(SheetPath):
  wb, sheet, c=split_wbname(SheetPath)
  return wbo(SheetPath)[sheet].max_column

# max row
def maxrow(SheetPath):
  wb, sheet, c=split_wbname(SheetPath)
  return wbo(SheetPath)[sheet].max_row

# add cell
# add_cell('A', col=1)='B'
# add_cell('A1', row=1)='A2'
def add_cell(CellName, row=0, col=0):
  Col, Row=split_cell_str(CellName)
  if Row: Row=str(int(Row)+row)
  else: Row=''
  if Col: Col=num2col(col2num(Col)+col)
  else: Col=''
  return Col+Row

def copy_cell(srcCellObj, targetCellObj): ########
  targetCellObj.value=srcCellObj.value
  targetCellObj.data_type=srcCellObj.data_type
  if srcCellObj.has_style: 
    targetCellObj.font = copy.deepcopy(srcCellObj.font)
    targetCellObj.border = copy.deepcopy(srcCellObj.border)
    targetCellObj.fill = copy.deepcopy(srcCellObj.fill)
    targetCellObj.number_format = copy.deepcopy(srcCellObj.number_format)
    targetCellObj.protection = copy.deepcopy(srcCellObj.protection)
    targetCellObj.alignment = copy.deepcopy(srcCellObj.alignment)
    #targetCellObj.style=copy.deepcopy(srcCellObj.style)
  if srcCellObj.hyperlink: targetCellObj.hyperlink=copy.deepcopy(srcCellObj.hyperlink)
  if srcCellObj.comment: targetCellObj=copy.deepcopy(srcCellObj.comment)

# write data
# write('wb/sheet/A1', (1,2,3)) => write row from A1 : A1, A2, A3
# write('wb/sheet/A1:', (1,2,3)) => write col from A1 : A1, B1, C1
# write('wb/sheet/A1', 1) => write cell A1 : A1=1
# write('wb/sheet/A1', ((1,2,3),(4,5,6))) => write row (1, 2, 3) from A1 and row (4, 5, 6) from B1
# WriteOnly=True: write('wb/sheet', DLIST/LIST)
def write(CellPath, Data=None):
  wkbk, sheet, cell=split_wbname(CellPath)
  if wb(wkbk).is_writeonly():
    if type(Data) in (tuple, list):
      for row in Data: 
        wbcls(wkbk).d[sheet].append([None if i=='' else i for i in row])
  else:
    if type(Data) in (tuple, list):
      if type(Data[0]) in (tuple, list): # DLIST
        for row, irow in zip(Data, range(len(Data))):
          for i, j in zip(row, range(len(row))):
            if i=='': i=None
            ci=add_cell(cell, col=j, row=irow)
            
            if type(i) is xl.cell.cell.Cell: copy_cell(i, shto(compose(wkbk,sheet))[ci]) # i
            else: shto(compose(wkbk,sheet))[ci]=i

      else: # LIST
        for i in Data:
          if i=='': i=None
          if cell[-1]==':': # write col
            cell=cell[:-1]
            
            if type(i) is xl.cell.cell.Cell: copy_cell(i, shto(CellPath)[cell]) #i
            else: shto(CellPath)[cell]=i
            cell=add_cell(cell, row=1)
          else: # write row
            
            if type(i) is xl.cell.cell.Cell: copy_cell(i, shto(CellPath)[cell]) #i
            else: shto(CellPath)[cell]=i
            cell=add_cell(cell, col=1)

    else: 
      if Data=='': Data=None
      if type(Data) is xl.cell.cell.Cell: copy_cell(Data, shto(CellPath)[cell]) # Data
      else: shto(CellPath)[cell]=Data
      
  
# remove rows / cols
# row = remove # of rows
# col = remove # of cols
def remove(Path, row=0, col=0):
  cell=split_wbname(Path)[2]
  Col, Row=split_cell_str(cell)
  if row>0: 
    shto(Path).delete_rows(int(Row), row)
    return row
  if col>0:
    shto(Path).delete_cols(col2num(Col), col)
    return col

# insert rows / cols
# row = insert # of rows
# col = insert # of cols
def insert(Cell, row=0, col=0):
  Col, Row=split_cell_str(split_wbname(Cell)[2])
  if row>0: 
    shto(Cell).insert_rows(int(Row), row)
    return row
  if col>0:
    shto(Cell).insert_cols(col2num(Col), col)


def headerlist(SheetPath, Uniform=False):
  '''
  list headers of cols (the first row) -> [Name.A, Gender.B, Age.C, ... Name.Col, ...] 
  SheetPath=wb/sheet
  Uniform: True: [Student.A .B Gender.C]
           False: [Student.A B Gender.C]
  '''
  wkbk, sheet, cell=split_wbname(SheetPath)
  r=[]
  n=0
  for i in wbo(wkbk)[sheet][1]:
    n+=1
    if i.value is None: 
      if Uniform: r.append('.'+num2col(n))
      else: r.append(num2col(n))
    else: r.append(str(i.value).strip()+'.'+num2col(n))
  return r

# comment on a cell
def comment(Cell, Comment='', Author=''):
  if Comment:
    cello(Cell).comment=xl.comment.Comment(Comment, Author)
    cprint(Author+': '+Comment)
    return (Aurthor, Comment)
  else:
    r=(cello(Cell).comment.author, cello(Cell).comment.text)
    cprint(r[0]+': '+r[1])
    return r

# purge sheet
def _purge_sheet(Sheet):
  wkbk, sheet, cell=split_wbname(Sheet)
  Sheet=compose(wkbk, sheet)
  MaxCol=maxcol(Sheet)
  MaxRow=maxrow(Sheet)
  n=0
  L=list(range(1, MaxCol+1))
  L.reverse()
  for col in L:
    col=num2col(col)
    if all([x in (None, '') for x in read(compose(wkbk, sheet, col))]): n+=1
    else: break
    
  if n>0: remove(compose(wkbk, sheet, col), col=n)
  
  m=n
  n=0
  L=list(range(1, MaxRow+1))
  L.reverse()
  for row in L:
    row=str(row)
    if all([x in (None, '') for x in read(compose(wkbk, sheet, row))]): n+=1
    else: break
    
  if n>0: remove(compose(wkbk, sheet, row), row=n)
  
  return (m, n)

def purge(Sheet):
  wkbk, sheet, cell=split_wbname(Sheet)
  
  if sheet is None: # workbook
    for sheet in shlist(wkbk): _purge_sheet(compose(wkbk, sheet))
  else: _purge_sheet(compose(wkbk, sheet)) # sheet
    