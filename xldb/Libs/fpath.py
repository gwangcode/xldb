import glob, os
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
class fpath: # parse a relative path
  path='' # original string of file path
  
  def __init__(self, path): self.path=path

  def full(self): return os.path.abspath(os.path.expanduser(self.path))

  def directory(self):
    f=self.full()
    return os.path.dirname(f)

  def __split_file(self):
    f=self.full()
    b=os.path.basename(f)
    return os.path.splitext(b)
  
  def base(self):
    sf=self.__split_file()
    return sf[0]
      
  def extension(self):
    sf=self.__split_file()
    return sf[1]

  def split_dir(self):
    d=self.directory()
    return d.split('/')
 
  def is_file(self):
    f=self.full()
    return os.path.isfile(f)

  def is_dir(self):
    f=self.full()
    return os.path.isdir(f)

  def glob(self):
    f=self.full()
    return glob.glob(f, recursive=True)

  def walk(self):
    f=self.full()
    return os.walk(f)