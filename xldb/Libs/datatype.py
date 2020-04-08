import datetime, re

# data -> int/float
# if not, return str
def num(data):
  try: 
    f=float(data)
    i=int(f)
    if f-i==0: return i
    else: return f
  except: return data 

# convert data to string
# deal with None/''
# including data2str()
def cstr(data, NoneAs=None, EmptyAs=''):
  if data is None: return NoneAs
  elif data=='': return EmptyAs
  else: return str(data)

# str -> date
# Date: 2001-12-11
# Time: 12:11:55
# Date&Time: 2001-12-11 12:11:55
# Date&Time.ms: 2001-12-11 12:11:55.123
def date(Str):
  dt=Str.split()
  if len(dt)==1: 
    if re.match('^\d{4}-\d{2}-\d{2}$', Str): return datetime.datetime.strptime(Str, '%Y-%m-%d')
    elif re.match('^\d{2}\:\d{2}\:\d{2}$', Str): return datetime.datetime.strptime(Str, '%H:%M:%S')
  else: 
    if '.' in Str: 
      if ' ' in Str: return datetime.datetime.strptime(Str, '%Y-%m-%d %H:%M:%S.%f')
      else: return datetime.datetime.strptime(Str, '%Y-%m-%d_%H:%M:%S.%f')
    else: 
      if ' ' in Str: return datetime.datetime.strptime(Str, '%Y-%m-%d %H:%M:%S')
      else: return datetime.datetime.strptime(Str, '%Y-%m-%d_%H:%M:%S')

'''
# 1985 -> 1985-01-01 00:00:00.00
# 12-11 -> now, 12-11 mm-dd
# 1985-12-11 -> 1985-12-11 00:00:00.00
# 55. -> now  55 sec
# :01:55 -> now :01:55 min:sec
# 08:30 -> now 08:30:00.00 hour:min
# 08:30:55 -> now 08:30:55.00 hour:min:sec
# .20 -> now .20 ms
# 55.20 -> now :55.20 55s 20ms
def transdate(Str):
  if re.match('^\d{4}-\d{2}-\d{2}$', Str): return datetime.datetime.strptime(Str, '%Y-%m-%d') # 1985-12-11
  elif re.match('^\d{2}-\d{2}$', Str): return datetime.datetime.strptime(Str, '%m-%d') # 12-11
  elif re.match('^\d{4}y$', Str): return datetime.datetime.strptime(Str, '%Yy') # 1985y
  elif re.match('^\d{2}m$', Str): return datetime.datetime.strptime(Str, '%mm') # 12m December
  elif re.match('^\d{2}d$', Str): return datetime.datetime.strptime(Str, '%dd') # 12d day
  elif re.match('^\d{2}"$', Str): return datetime.datetime.strptime(Str, '%S"') # 55"
  elif re.match('^\:\d{2}$', Str): return datetime.datetime.strptime(Str, '%:M') # :01 min
  elif re.match('^\\d{2}\:$', Str): return datetime.datetime.strptime(Str, '%:M') # 01: hr
  elif re.match('^\:\d{2}\:\d{2}$', Str): return datetime.datetime.strptime(Str, '%:M:%S') # :01:55 min:sec
  elif re.match('^\d{2}\:\d{2}$', Str): return datetime.datetime.strptime(Str, '%H:%M') # 08:30 hr:min
  elif re.match('^\d{2}\:\d{2}\:\d{2}$', Str): return datetime.datetime.strptime(Str, '%M:%S:%S') # 08:30:25
  elif re.match('^\d{2}\"(\d+)$', Str): return datetime.datetime.strptime(Str, '%S"%f') # 55"20 
  elif re.match('^\"(\d+)$', Str): return datetime.datetime.strptime(Str, '"%f') # 20 "20 20ms
'''  

# try to convert to date format
def try_date(Str):
  try: 
    dt=date(Str)
    if dt: return dt
    else: return Str
  except: return Str

# date -> str
#   Standard: 2019-10-02_12:35:06
#   Date: 2019-10-02
#   Time: 12:35:06
def strdate(Date, Type='Standard'):
  if Type=='Date': return Date.strftime('%Y-%m-%d')
  elif Type=='Time': return Date.strftime('%H:%M:%S')
  else: return Date.strftime('%Y-%m-%d_%H:%M:%S')

# str to typed data
def str2data(Str):
  data=num(Str)
  if type(data) is str:
    data=try_date(data)
    if type(data) is str:
      if data=='True': return True # bool True
      elif data=='False': return False # bool False
      else: return data # str
    else: return data # datetime
  else: return data # num

# sum up iterals
def sum(IterObj):
  n=0
  for i in IterObj:
    if n==0: r=i
    else: r+=i
    n+=1
  return r




