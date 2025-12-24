import sys,os,webbrowser
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import tkr as tk
from function.manyfunction import *
from ..widgets import __Widget__ as wi
from font.font import *
class Link(tk.Label):
 def __init__(self,master,kwargs):
  self.fg=parsecolor(kwargs.get("fg"),THEMES["link"])
  self.back_bg=kwargs.get("back_bg")
  self.bg=parsecolor(kwargs.get("bg"),self.back_bg or THEMES["bg1"])
  self.underline=True if kwargs.get("underline","normal")=="normal" else False
  self.weight=kwargs.get("weight") if kwargs.get("weight") in ["normal","bold"] else "normal"
  self.slant=kwargs.get("slant") if kwargs.get("slant") in ["roman","italic"] else "roman"
  self.overstrike=False if kwargs.get("overstrike","normal")=="normal" else True
  self.font_family=kwargs.get("font_family","Meiryo")
  self.font_size=num0(kwargs.get("font_size"),14)
  self.font=kwargs.get("font",fonts(master,self.font_family,self.font_size,self.weight,self.slant,self.overstrike,self.underline))
  self.justify=kwargs.get("justify") if kwargs.get("justify") in ["right","center","left"] else "left"
  self.wraplength=num0(kwargs.get("wraplength"))
  self.cursor=kwargs.get("cursor")
  self.takefocus=bols(kwargs.get("takefocus"))
  self.borderwidth=num0(kwargs.get("bd"))
  self.relief=kwargs.get("relief") if kwargs.get("relief") in relief_list else "flat"
  self.padx=num0(kwargs.get("padx"))
  self.pady=num0(kwargs.get("pady"))
  self.anchor=kwargs.get("anchor","w") if get_dict(anchor_dict,kwargs.get("anchor","right"))[1] in anchor_list else "w"
  self.activeforeground=parsecolor(kwargs.get("activefg"))
  self.activebackground=parsecolor(kwargs.get("activebg"))
  self.highlightthickness=num0(kwargs.get("highlightthickness"))
  self.highlightcolor=parsecolor(kwargs.get("highlightfg"))
  self.highlightbackground=parsecolor(kwargs.get("highlightbg"))
  self.link_url=kwargs.get("link")
  self.linkchecks(self.link_url)
  txt=kwargs.get("text")
  if (self.link_url and self.link_url!="") and (txt and txt!=""):self.text=txt
  elif (self.link_url and self.link_url!="") and (not txt or txt==""):self.text=self.link_url
  else:self.text=""
  self.size=wi._size(kwargs)
  self.width=self.size[0]
  self.height=self.size[1]
  super().__init__(master,takefocus=self.takefocus,highlightcolor=self.highlightcolor,highlightbackground=self.highlightbackground,highlightthickness=self.highlightthickness,activeforeground=self.activeforeground,activebackground=self.activebackground,anchor=self.anchor,pady=self.pady,padx=self.padx,relief=self.relief,wraplength=self.wraplength,cursor=self.cursor,text=self.text,bg=self.bg,fg=self.fg,font=self.font,width=self.width,height=self.height,justify=self.justify)
  self.bind("<Button-1>",self._link)
 def _delta(self):self.destroy()
 def _link(self,event):
  if self.links==True and self.link_url and self.link_url!="":
   try:webbrowser.open(self.link_url)
   except Exception as e:print(f"error:{e}")
  elif self.links==False:print("error")
 def linkchecks(self,url):self.links=urlcheck(url)
 def get_link(self):return self.link_url
 def set_link(self,link):self.link_url=link
 def get_size(self):return (self.width,self.height)
 def get_text(self):return self.text
 def set_text(self,txt):
  if txt:
   self.text=txt
   self.config(text=txt)
 def get_bg(self):return self.bg
 def set_bg(self,nbg):
  if nbg and isinstance(nbg,str):
   self.bg=nbg
   self.config(bg=nbg)
 def get_fg(self):return self.fg
 def set_fg(self,nfg):
  if nfg and isinstance(nfg,str):
   self.fg=nfg
   self.config(fg=nfg)
 def get_font(self):return self.font
 def set_font(self,nfont):
  if nfont and isinstance(nfont,tuple):
   self.font=nfont
   self.config(font=nfont)