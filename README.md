# xldb
A platform to operate xlsx data in a terminal

This is a platform based on python to run commands and scripts mainly for manipulating data in xlsx files using openpyxl library.

Compositions:

  xldb.py is the platform command. You can type:

            ./xldb.py

  to start the platform's command environment.

  xldb.py relies on sys, os, glob, shlex, re, prompt_toolkit, traceback, fnmatch, io libraries.
  
  Paths.set is the setup file to designate Libraries directory, Script Directory, Initial imports, End-command and Autocomplete script. The file is written in the following form:

          LibDir=Libs
          ScriptDir=Scripts
          Imports=stdwb as wb, openpyxl as xl, multi
          EndCmd=EndCmd
          AutoComplete=AUTOCOMPLETE

In Paths.set:
  LibDir=@/Libs;
  ScriptDir=@/Scripts; # ; separate the directories that store the commands; After # is the comment, @ represents the Bin-Directory, the directory where xldb.py is
  Imports=stdwb as wb, openpyxl as xl, multi
  EndCmd=EndCmd
  AutoComplete=AUTOCOMPLETE

  LiDir designates the diretcotries of the import libraries, where @ represents the xldb.py directory; ';' separates paths; The comments are behind '#' 
  ScriptDir designates the command paths; ';' separate the directories that store the commands; After # is the comment, @ represents the xldb.py directory
  Imports: imports libraries at the initial
  EndCmd designates the command that runs after each command line is finished. It contains the prompt information.
  AutoComplete designates the autocomplete command that autocompletes the input



In command environment:

.ls : run shell command (3)

/a=$.abc: make the script environment (python environment), run python functions  (3)

=a: the variable a

abc && def : split two commands. The commands run one after another (1)

~a=abc : return value of command abc goes to variable a (2)

cmd abc def

cmd “=`.cmd2 abc`”

@~/Documents/abc -> run command abc in the designated path

abc/def: designate the path of the command, this equals: .../Script/abc/def


In script environment:

$.abc or `.abc` : run command
$.abc:print =x or `🔤🔤:abc:print =x`: run command with external variable abc

In both environments:

abc; :do not print cprint=False

args → parameters



          > A && B && C
          _GLB[‘x’] in A can not be used in B and C


built-in functions & varibles:

args: command parameters
gvars(): global dict (similar to globals())
cmd(): run command
err(): error message
cprint(): print when set is on
prompt(): set up prompt text
initsys(): reload initsys() → reinitialize system
setprint(): set print on/off
#rtn(): return value of each command, rtn() → get the return value of the last command; 
#rtn(True)/rtn(CheckTunnel=True) → get the return value of the last command when it’s on the tunnel command series, only when && exists,  like: cmd 1 && cmd 2 && cmd 3 …, otherwise #rtn() returns None
builtins.py: import builtins to use all the above built-in functions in lib
_RTN → return value of the previous command in cmd 1 && cmd 2 && cmd 3 …
                _RTN in cmd 2 is the return value of cmd 1
     
      _GLB → public variable dict that can store variables used as public variables from the top level cmd:
          A:  $. B
          B:  $. C
          C:  …
          >A → GLB[‘x’] in A  can be used throughout A, B, C

Variables in a script:
In a script:
x=5
$. print(x) # directly use outside variables

$. ~y=10
print($~y) # use the inside variable

Pipe between commands & shell commands
.print abc && .|grep a
Output: abc
The shell accepts the strings printed out by cprint

Commands:
NEW  workbooktag .FILE file path: create new workbook or sheet
NEW /workbooktag .FILE file path
NEW /workbook/sheet1 /workbook/sheet2 … .POS n: create new sheets for the first sheet (sheet1) at position n
NEW =[Sheet list] .POS n : create new sheets for the first sheet (sheet1) at position n

INSERT /w/s/c .AHEADOF .BEHIND : insert rows/cols
INSERT A: insert col at A
INSERT A B Student.C … : insert cols at the positions
INSERT =[Cols list] ...
INSERT A .NUM 10 : insert 10 cols from A
INSERT Student. Gender. … .AHEADOF id. [or BEHIND id] : insert cols ahead of id or behind id, if no .AHEADOF or .BEHIND: append cols
INSERT .NUM 10 .AHEADOF id [or BEHIND id] : insert 10 cols ahead of id or behind id
INSERT .NUM 10 .ABOVE 12 [or BELOW 12] : insert 10 rows above row 12 or below row 12, if no .ABOVE or .BELOW, append rows
The sheets are similar to cols

APPEND

DELETE: empty sheets/range/rows/cols/cells, similar to INSERT
DELETE A1:B3 : delete range
DELETE A .HEADER : delete all content of col A including header

FETCH: read / write/ convert data  sheet/range/rows/cols/cells .CONDITION: find rows that meet conditon
     FETCH  [cols] .DATA/STR/NUM/DATE/TIME/DATETIME/BOOL [data]      .FROM   workbook/sheet/range/rows/cols/cells  .TO  workbook/sheet/range/rows/cols/cells .WHERE [bool expression] {student.} or {A}: the col ref. 
                   
REMOVE: remove workbook/sheet/rows/cols, similar to INSERT
     remove =[1 3, 5, …] or =[‘1’, ‘3’, ‘5’, …] from Sheet → remove rows 1, 3, 5, …
     remove =[‘A’,  ‘C’, ‘Student.’, ‘Gender.D’…] from Sheet  → remove cols A, C, Student., Gender.D, …
     remove A:C from Sheet → remove cols from A to C
     remove 1:5 from Sheet → remove rows from 1 to 5
     remove 10 from Sheet/Student.A → remove 10 cols from Student.A
     remove 10 from Sheet/5 → remove 10 rows from row 5


SAVE worbooktag .FILE file path: save workbook, .FILE: save to some different file, the path is rewritten as the new file

RENAME /w1 /w2: rename workbook/sheet/col
RENAME /w1/s1 /w1/s2
RENAME /w1/s1/c1 /w1/s1/c2

repath worktag .FILE new path: repath workbook
LW: list workbook/sheet/cols
LW
LW abc
LW /abc
LW a*
…


CW: change/goto workbook/sheet
CW abc
CW /abc
CW abc/def
…


OPEN file paths .AS worktag: open workbooks

CLOSE worktags: close workbooks

PRINT abc/=x: print on the screen
SETP ON/OFF: set print outline
ECHO =variable: pass data

style a/Sheet1/A2 .font .size .fcolor .bcolor .boder … : change styles of cell

shsize .row abc/sheet1 → total rows of sheet1
       .col abc/sheet1 → total cols of sheet1 (.num, 7; otherwise G)

rcmd → run command commonly used for echo “.ls abc” && rcmd
shellvar → set up/read shell environment variables

Reserved commands:
EndCmd: update current working directory
AUTOCOMPLETE: support autocomplete for workbook/sheet
BACKRUN: accept cmd from the file to run and output the results to the file on server
REIMPORT: reload libraries


Syntax:
       !External:Begin
       …
       …
       !External:End
       Script between the External stuff is executed in the module level and the others are executed in the functional level __Command_of_..._(Args)       


