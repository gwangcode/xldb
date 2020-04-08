# check if List is DList
def is_dlist(List):
  L=None
  if type(List) in (tuple, list):
    if List:
      for i in List:
        if type(i) in (tuple, list):
          if L is None: L=len(i)
          elif len(i)!=L: return False
        else: return False
      return True
    else: return False
  else: return False

# it allows different lengths of rows
def is_dlist_alike(List):
  L=None
  if type(List) in (tuple, list):
    if List:
      for i in List:
        if type(i) not in (tuple, list): return False
    else: return False
    return True
  else: return False


# make a list/variable into a DList
def complete(List):
  L=[]
  if type(List) in (tuple, list):
    for i in range(len(List)): 
      if type(List[i]) not in (tuple, list): 
        List[i]=[List[i]]
      L.append(len(List[i]))
    Row=max(L)
    for i in range(len(List)):
      diff=Row-len(List[i])
      if diff>0: List[i]+=[None]*diff
    return List    
  else: return [[List]]


# return NRows*NCols
def dimension(DList): return len(DList), len(DList[0])

# transpose a DList
def transpose(DList): return list(map(list, zip(*DList)))

# [None, None, ..., None] -> True
def is_None_list(List): return all([e is None for e in List])

# remove excessive Nones
# Data is a dlist/list
def purge(Data):
  if is_dlist(Data): # dlist
    while is_None_list(Data[-1]): Data.pop()
    Data=transpose(Data)
    while is_None_list(Data[-1]): Data.pop()
    return transpose(Data)
    
  else: # list
    while Data[-1] is None: Data.pop()