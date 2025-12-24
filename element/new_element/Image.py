from function.manyfunction import *
from pathlib import Path
from PIL import Image,ImageTk
import tkinter as tk
class Images(tk.Label):
 def __init__(self,master,kwargs):
  self.master=master
  self.path=Path(kwargs.get("path"))
  self.size=self._img_size(kwargs,self.path)
  self.takefocus=bols(kwargs.get("takefocus"))
  self.width=self.size[0]
  self.height=self.size[1]
  self.image_ref=None
  self.image=None
  self._image_set()
 def _img_size(self,kwargs,path):
  size=list(kwargs.get("size",(100,100)))
  if size and isinstance(size,tuple) and len(size)==2:
   width,height=nums(kwargs.get("width",None)),nums(kwargs.get("height",None))
   return (width if size[0]==None and width!=None else size[0],height if size[1]==None and height!=None else size[1])
  try:
   with Image.open(path) as img:return img.size
  except:return (100,100)
 def _image_set(self,path=None):
  try:
   if path==None:path=self.path
   img=Image.open(path)
   if self.size and isinstance(self.size,tuple):img=img.resize(self.size)
   self.image_ref=ImageTk.PhotoImage(img)
   super().__init__(self.master,takefocus=self.takefocus,image=self.image_ref,height=self.height,width=self.width)
   self.image=self.image_ref
   self.path=path
  except:
   e_txt=f"error:{self.path}"
   super().__init__(self.master,takefocus=self.takefocus,text=e_txt,height=1,width=len(e_txt))
 def _delta(self):self.destroy()
 def clear(self):
  self.image=None
  self.image_ref=None
  self.config(image="",text="")
 def get_path(self):return self.path
 def get_ex(self):return os.path.split(self.path)[1].split(".",1)[1]