import itertools,sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import tkr.tkme as tk
from fontTools.ttLib import TTFont
class Fontfile:
 def __init__(self,file=None):
  self.error_j=False if file and (os.path.splitext(file)[1] in [".ttf",".otf",".ttc",".woff",".woff2"]) else True
  self.fontdo(file)
 def fontdo(self,file):
  self.file=file
# font=TTFont('fonts.ttf')
# for record in font['name'].names:print(record.toUnicode())
# print(Fontfile("fonts.ttf"))
def nametofont(name,root=None):return Fontm(name=name,exists=True,root=root)
class Fontm:
 counter=itertools.count(1)
 def _set(self,kw):
  options=[]
  for k,v in kw.items():
   options.append("-"+k)
   options.append(str(v))
  return tuple(options)
 def _get(self,args):
  options=[]
  for k in args:options.append("-"+k)
  return tuple(options)
 def _mkdict(self,args):
  options={}
  for i in range(0,len(args),2):options[args[i][1:]]=args[i+1]
  return options
 def __init__(self,root=None,font=None,name=None,exists=False,**options):
  if root==None:root=tk._get_default_root('use font')
  tk=getattr(root,'tk',root)
  font=tk.splitlist(tk.call("font","actual",font)) if font else self._set(options)
  if not name:name="font"+str(next(self.counter))
  self.name=name
  if exists:
   self.delete_font=False
   if self.name not in tk.splitlist(tk.call("font","names")):raise tk._tkinter.TclError("named font %s does not already exist" % (self.name,))
   if font:tk.call("font","configure",self.name,*font)
  else:
   tk.call("font","create",self.name,*font)
   self.delete_font=True
  self._tk=tk
  self._split=tk.splitlist
  self._call =tk.call
 def __str__(self):return self.name
 def __repr__(self):return f"<{self.__class__.__module__}.{self.__class__.__qualname__} object {self.name!r}>"
 def __eq__(self,other):
  if not isinstance(other,Fontm):return NotImplemented
  return self.name==other.name and self._tk==other._tk
 def __getitem__(self,key):return self.cget(key)
 def __setitem__(self,key,value):self.configure(**{key: value})
 def __del__(self):
  try:
   if self.delete_font:self._call("font","delete",self.name)
  except Exception:pass
 def copy(self):return Fontm(self._tk,**self.actual())
 def actual(self,option=None,displayof=None):
  args=()
  if displayof:args=('-displayof',displayof)
  if option:
   args=args+('-'+option,)
   return self._call("font","actual",self.name,*args)
  else:return self._mkdict(self._split(self._call("font","actual",self.name,*args)))
 def cget(self,option):return self._call("font","config",self.name,"-"+option)
 def config(self,**options):
  if options:self._call("font","config",self.name,*self._set(options))
  else:return self._mkdict(self._split(self._call("font","config",self.name)))
 configure=config
 def measure(self,text,displayof=None):
  args=(text,)
  if displayof:args=('-displayof',displayof,text)
  return self._tk.getint(self._call("font","measure",self.name,*args))
 def metrics(self,*options,**kw):
  args=()
  displayof=kw.pop('displayof',None)
  if displayof:args=('-displayof',displayof)
  if options:
   args=args+self._get(options)
   return self._tk.getint(self._call("font","metrics",self.name,*args))
  else:
   res=self._split(self._call("font","metrics",self.name,*args))
   options={}
   for i in range(0,len(res),2):options[res[i][1:]]=self._tk.getint(res[i+1])
   return options
def families(root=None,displayof=None):
 if root==None:root=tk._get_default_root('use font.families()')
 args=()
 if displayof:args=('-displayof',displayof)
 return root.tk.splitlist(root.tk.call("font","families",*args))
def names(root=None):
 if root==None:root=tk._get_default_root('use font.names()')
 return root.tk.splitlist(root.tk.call("font","names"))
class fonts(Fontm):
 def __init__(self,master,family="Meiryo",size=14,weight="normal",slant="roman",overstrike=False,underline=False):
  super().__init__(master,family=family,size=size,weight=weight,slant=slant,overstrike=overstrike,underline=underline)