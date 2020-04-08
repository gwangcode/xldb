import stdwb as wb, fnmatch, datatype

def wkbk(Path):
  '''
  Path='/w/s/c'
  c=Student.A, Student., A, Student.A:Gender.C, ...
  wkbk(Path) -> w 
  '''

  return wb.split_wbname(Path)[0]

def sheet(Path):
  '''
  Path='/w/s/c'
  c=Student.A, Student., A, Student.A:Gender.C, ...
  sheet(Path) -> s 
  '''

  return wb.split_wbname(Path)[1]

def cellpart(Path):
  '''
  Path='/w/s/c'
  c=Student.A, Student., A, Student.A:Gender.C, ...
  cellpart(Path) -> c
  '''

  return wb.split_wbname(Path)[2]

def is_range(Path):
  '''
  Path='/w/s/c'
  c='A:C' -> True
  c='A' -> False
  '''

  return ':' in cellpart(Path)

def _str_name(Name):
  if Name is None: return ''
  else: return Name

def complete_path(Path, Array=False, WithRow=False):
  '''
  Complete Path to /w/s/A:C, /w/s/A, ...
  if sheet does not exist, returns None
  A       B      C
  Student Gender Grade
  ...     ...    ...
  /w/s/Student. -> /w/s/A
  /w/s/Student.B:Grade.C -> /w/s/B:C
  /w/s/B:C (Array) -> [w, s, Gender, B, 1, Grade, C, 100]
  /w/s/B:C (WithRow) -> /w/s/B1:C100
  etc.
  '''
  
  w, s, c=wb.split_wbname(Path)
  if wb.wb_exists(w):
    if s in wb.shlist(w):
      if is_range(wb.compose(w, s, c)): # /w/s/A:C
        BeginPart, EndPart=c.split(':')
        BeginName, BeginCol, BeginRow=wb.cellname(wb.compose(w, s, BeginPart))[:3]
        EndName, EndCol, EndRow=wb.cellname(wb.compose(w, s, EndPart))[:3]
        if (BeginCol and not BeginRow and not EndCol and not EndRow) and not WithRow: # A:
          if not EndName:
            EndCol=wb.num2col(wb.maxcol(wb.compose(w, s)))
            #EndRow=str(wb.maxrow(wb.compose(w, s)))
            Range=[BeginName, BeginCol, None]+list(wb.cellname(wb.compose(w, s, EndCol)))[:3]
            if not Array: Range=Range[1]+':'+Range[4]
          else: return None
        elif (not BeginCol and not BeginRow and EndCol and not EndRow) and not WithRow: # :B
          if not BeginName:
            BeginCol='A'
            #BeginRow='1'
            Range=list(wb.cellname(wb.compose(w, s, BeginCol)))[:3]+[EndName, EndCol, None]
            if not Array: Range=_str_name(Range[1])+':'+_str_name(Range[4])
          else: return None
        elif (not BeginCol and BeginRow and not EndCol and not EndRow) and not WithRow: # 1:
          if not BeginName and not EndName:
            #BeginCol='A'
            #BeginRow='1'
            EndRow=str(wb.maxrow(wb.compose(w, s,)))
            Range=[None, None, str(BeginRow)]+[None, None, EndRow]
            if not Array: Range=Range[2]+':'+Range[5]
          else: return None
        elif (not BeginCol and not BeginRow and not EndCol and EndRow) and not WithRow: # :10
          if not BeginName and not EndName:
            #BeginCol='A'
            BeginRow='1'
            Range=[None, None, BeginRow]+[None, None, str(EndRow)]
            if not Array: Range=Range[2]+':'+Range[5]
          else: return None
        elif (not BeginCol and BeginRow and not EndCol and EndRow) and not WithRow: # 1:10
          if not BeginName and not EndName:
            #BeginCol='A'
            #BeginRow='1'
            Range=[None, None, str(BeginRow)]+[None, None, str(EndRow)]
            if not Array: Range=Range[2]+':'+Range[5]
          else: return None

        elif (BeginCol and not BeginRow and EndCol and not EndRow) and not WithRow: # A:B
          Range=[BeginName, BeginCol, None]+[EndName, EndCol, None]
          if not Array: Range=Range[1]+':'+Range[4]
          
        else: # other situations such as A:10, A10:B50 etc.
          if not BeginCol: 
            if not BeginName: BeginCol='A'
            else: return None
          if not BeginRow: 
            if not BeginName: BeginRow='1'
            else: return None
          if not EndCol: 
            if not EndName: EndCol=wb.num2col(wb.maxcol(wb.compose(w, s)))
            else: return None
          if not EndRow: 
            if not EndName: EndRow=str(wb.maxrow(wb.compose(w, s)))
            else: return None
          BeginRange=wb.cellname(wb.compose(w, s, BeginCol+BeginRow))[:3]
          EndRange=wb.cellname(wb.compose(w, s, EndCol+EndRow))[:3]
          Range=list(BeginRange)+list(EndRange)
          if not Array: Range=_str_name(Range[1])+_str_name(Range[2])+':'+_str_name(Range[4])+_str_name(Range[5])

      else: # /w/s/A  
        Name, Col, Row=wb.cellname(wb.compose(w,s,c))[:3]
        if Array: Range=[Name, Col, Row]
        elif Col: 
          if WithRow and not Row: Range=Col+'1'+':'+Col+str(wb.maxrow(Path)) # /w/s/A
          else: Range=_str_name(Col)+_str_name(Row)
        elif Row and not Name: 
          if WithRow and not Col: Range='A'+str(Row)+':'+wb.num2col(wb.maxcol(Path))+str(Row) # /w/s/5
          else: Range=str(Row)
        else: return None
        
      if Array: return [w, s]+list(Range)
      elif Range: return wb.compose(w, s, Range)

def col(Path):
  '''
  /w/s/Student. -> A
  '''
  return complete_path(Path, Array=True)[3]

def col_name(Path):
  '''
  /w/s/Student. -> Student
  '''
  return complete_path(Path, Array=True)[2]

def locate(Path, WithRow=False, Array=False):
  '''
  /w/s/Student. -> /w/s/A
  /w/s/Student.5:Gender -> /w/s/A1:C10
  /w/s/Student.5:Gender(array) -> (w, s, A, 1, C, 10)
  '''
  if Array: 
    p=complete_path(Path, WithRow=WithRow, Array=True)
    w=p[0]
    s=p[1]
    Col1=p[3]
    Row1=p[4]
    Col2=Row2=None
    if len(p)==8: 
      Col2=p[6]
      Row2=p[7]
  
    return (w, s, Col1, Row1, Col2, Row2)
  else: return complete_path(Path, WithRow=WithRow)

class iterate:
  Level='c'
  nWb=nSh=nCl=nCol=nRow=0
  w=s=c=None
  ContainColName=False

  def __init__(self, MatchExpr):
    self.w, self.s, self.c=wb.split_wbname(MatchExpr)
    if self.c is None and self.s is None and self.w is not None: self.Level='w'
    elif self.c is None and self.s is not None and self.w is not None: self.Level='s'
      
  def __iter__(self):
    self.WbList=wb.wblist()
    self.nWb=0
    self.nSh=0
    self.nCl=0
    self.nCol=1
    self.nRow=1
    if self.Level=='c':
      if '.' in self.c: self.ContainColName=True
    return self

  def __next__(self):
    if self.Level=='w':
      while True:
        WbList=tuple(wb.wblist())
        if self.nWb<len(WbList):
          r=WbList[self.nWb]
          self.nWb+=1
          r='/'+r
          if fnmatch.fnmatch(r, self.w): return r
          else: continue
        else: raise StopIteration
    elif self.Level=='s':
      while True:
        WbList=tuple(wb.wblist())
        if self.nWb<len(WbList):
          Wkbk=WbList[self.nWb]
          ShList=wb.shlist(Wkbk)
          if self.nSh<len(ShList):
            Sh=ShList[self.nSh]
            self.nSh+=1
            r=wb.compose(Wkbk, Sh)
            if fnmatch.fnmatch(r, wb.compose(self.w, self.s)): return r
            else: continue
          else:
            self.nWb+=1
            self.nSh=0
            continue
        else: raise StopIteration
    else:
      while True:
        WbList=tuple(wb.wblist())
        if self.nWb<len(WbList):
          Wkbk=WbList[self.nWb]
          ShList=wb.shlist(Wkbk)
          if self.nSh<len(ShList):
            Sh=ShList[self.nSh]
            Ncol=wb.maxcol(wb.compose(Wkbk, Sh))
            Nrow=wb.maxrow(wb.compose(Wkbk, Sh))
            if self.nRow<=Nrow:
              if self.nCol<=Ncol: 
                _nCol=self.nCol
                self.nCol+=1
                r=wb.compose(Wkbk, Sh, wb.num2col(_nCol)+str(self.nRow))
                if self.ContainColName: r=wb.compose(Wkbk, Sh, datatype.cstr(col_name(r), NoneAs='')+'.'+wb.num2col(_nCol)+str(self.nRow))
                if fnmatch.fnmatch(r, wb.compose(self.w, self.s, self.c)): return r
                else: continue
              else: 
                self.nRow+=1
                self.nCol=1
                continue
            else:
              self.nCol=1
              self.nRow=1
              self.nSh+=1
              continue
          else:
            self.nWb+=1
            self.nCol=1
            self.nRow=1
            self.nSh+=1
            continue
        else: raise StopIteration




