#! /Library/Frameworks/Python.framework/Versions/3.6/bin/python3
import styledtext as st
class textbox:
  Text=''
  CurVisible=True
  TopX=0
  TopY=0
  Width=None 
  Height=None 
  TextColor=0
  BgColor=231

  CursorX=None
  CursorY=None 


  def __init__(self, Text='', CurVisible=True, TopX=0, TopY=0, Width=None, Height=None, TextColor=0, BgColor=231):
    self.CurVisible=CurVisible
    self.TopX=TopX
    self.TopY=TopY
    self.Width=Width
    self.Height=Height
    self.TextColor=textbox
    self.BgColor=BgColor
    self.Text=Text

  def output(self):
    r='<curvisible='+str(self.CurVisible)+'>'
    if self.CursorX: r=st.write_property('curx', self.CursorX, r)
    if self.CursorY: r=st.write_property('cury', self.CursorY, r)

    TL=Text.split('\n')
    for line, ln in zip(TL[BeginRow:BeginRow+self.Height], len(TL[BeginRow:BeginRow+self.Height])):
      s='<forecolor='+str(self.TextColor)+' backcolor='+str(self.BgColor)+' line='+str(self.TopY+ln)+' col='+str(self.TopX+ln)+'|>'
      r+=s
    
    return r
      


  



