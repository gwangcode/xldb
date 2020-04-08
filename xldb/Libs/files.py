import os, glob, re, string, pickle

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

def walk(Path): return [i.Full for i in Glob_Parser(Path).Paths]

def fdir(Path): 
  '''
  return dir of a path
  >>> fdir('~/Document/abc') -> ~/Documents
  '''
  return File_Path_Parser(Path).Path

# find files
# ~/Documents/**/* -> [List of found files]
def findfiles(Path): return [i.Full for i in Glob_Parser(Path).Paths]

def fopen(File, mode='r'):
  '''
  open a file
  >>> open(~/Documents/abc)
  '''
  return open(fpath(File), mode)

def exists(Path, Dir=False):
  '''
  check path exists
  >>> exists('~/Documents/abc', True)
  check ~/Documents/ exists
  
  >>> exists('~/Documents/abc')
  check ~/Documents/abc exists
  '''
  return File_Path_Parser(Path).exists(not Dir)

def fread(Path):
  f=fopen(Path)
  r=f.readlines()
  f.close()
  return [i[:-1] if i[-1]=='\n' else i for i in r]

def fwrite(Path, TextList):
  f=fopen(Path, 'w')
  f.write('\n'.join(TextList))
  f.close()

def remove(File):
  '''
  remove a file
  >>> remove(~/Documents/abc)
  '''
  os.remove(fpath(File))

def dump(Obj, File):
  '''
  dump an object (Obj) to a file
  >>> dump(a, '~/Documents/abc')
  '''
  f=fopen(File,'wb')
  pickle.dump(Obj, f)
  f.close()

def load_dump(File):
  '''
  load an object dumpfile
  >>> obj=load_dump('~/Documents/abc')
  '''
  f=fopen(File, 'rb')
  obj=pickle.load(f)
  f.close()
  return obj
  
