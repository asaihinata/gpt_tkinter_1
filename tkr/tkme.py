import collections,enum,sys,types,_tkinter,re,warnings,os,traceback
from tkinter.constants import *
TclError=_tkinter.TclError
wantobjects=1
_debug=False
TkVersion=float(_tkinter.TK_VERSION)
TclVersion=float(_tkinter.TCL_VERSION)
READABLE=_tkinter.READABLE
WRITABLE=_tkinter.WRITABLE
EXCEPTION=_tkinter.EXCEPTION
_magic_re=re.compile(r'([\\{}])')
_space_re=re.compile(r'([\s])',re.ASCII)
def _join(value):return ' '.join(map(_stringify,value))
def _stringify(value):
 if isinstance(value,(list,tuple)):
  if len(value)==1:
   value=_stringify(value[0])
   if _magic_re.search(value):value='{%s}'%value
  else:value='{%s}'%_join(value)
 else:
  if isinstance(value,bytes):value=str(value,'latin1')
  else:value=str(value)
  if not value:value='{}'
  elif _magic_re.search(value):
   value=_magic_re.sub(r'\\\1',value)
   value=value.replace('\n',r'\n')
   value=_space_re.sub(r'\\\1',value)
   if value[0]=='"':value='\\'+value
  elif value[0]=='"' or _space_re.search(value):value='{%s}'%value
 return value
def _flatten(seq):
 res=()
 for item in seq:
  if isinstance(item,(tuple,list)):res=res+_flatten(item)
  elif item!=None:res=res+(item,)
 return res
try:_flatten=_tkinter._flatten
except:pass
def _cnfmerge(cnfs):
 if isinstance(cnfs,dict):return cnfs
 elif isinstance(cnfs,(type(None),str)):return cnfs
 else:
  cnf={}
  for c in _flatten(cnfs):
   try:cnf.update(c)
   except (AttributeError,TypeError) as msg:
    print("_cnfmerge:fallback due to:",msg)
    for k,v in c.items():cnf[k]=v
  return cnf
try:_cnfmerge=_tkinter._cnfmerge
except:pass
def _splitdict(tk,v,cut_minus=True,conv=None):
 t=tk.splitlist(v)
 if len(t)%2:raise RuntimeError('Tcl list representing a dict is expected to contain an even number of elements')
 it=iter(t)
 dict={}
 for key,value in zip(it,it):
  key=str(key)
  if cut_minus and key[0]=='-':key=key[1:]
  if conv:value=conv(value)
  dict[key]=value
 return dict
class _VersionInfoType(collections.namedtuple('_VersionInfoType',('major','minor','micro','releaselevel','serial'))):
 def __str__(self):
  if self.releaselevel=='final':return f'{self.major}.{self.minor}.{self.micro}'
  else:return f'{self.major}.{self.minor}{self.releaselevel[0]}{self.serial}'
def _parse_version(version):
 m=re.fullmatch(r'(\d+)\.(\d+)([ab.])(\d+)',version)
 major,minor,releaselevel,serial=m.groups()
 major,minor,serial=int(major),int(minor),int(serial)
 if releaselevel=='.':
  micro=serial
  serial=0
  releaselevel='final'
 else:
  micro=0
  releaselevel={'a':'alpha','b':'beta'}[releaselevel]
 return _VersionInfoType(major,minor,micro,releaselevel,serial)
@enum._simple_enum(enum.StrEnum)
class EventType:
 KeyPress='2'
 Key=KeyPress
 KeyRelease='3'
 ButtonPress='4'
 Button=ButtonPress
 ButtonRelease='5'
 Motion='6'
 Enter='7'
 Leave='8'
 FocusIn='9'
 FocusOut='10'
 Keymap='11'
 Expose='12'
 GraphicsExpose='13'
 NoExpose='14'
 Visibility='15'
 Create='16'
 Destroy='17'
 Unmap='18'
 Map='19'
 MapRequest='20'
 Reparent='21'
 Configure='22'
 ConfigureRequest='23'
 Gravity='24'
 ResizeRequest='25'
 Circulate='26'
 CirculateRequest='27'
 Property='28'
 SelectionClear='29'
 SelectionRequest='30'
 Selection='31'
 Colormap='32'
 ClientMessage='33'
 Mapping='34'
 VirtualEvent='35'
 Activate='36'
 Deactivate='37'
 MouseWheel='38'
class Event:
 def __repr__(self):
  attrs={k:v for k,v in self.__dict__.items() if v!='??'}
  if not self.char:del attrs['char']
  elif self.char!='??':attrs['char']=repr(self.char)
  if not getattr(self,'send_event',True):del attrs['send_event']
  if self.state==0:del attrs['state']
  elif isinstance(self.state,int):
   state=self.state
   mods=('Shift','Lock','Control','Mod1','Mod2','Mod3','Mod4','Mod5','Button1','Button2','Button3','Button4','Button5')
   s=[]
   for i,n in enumerate(mods):
    if state & (1 << i):s.append(n)
   state=state & ~((1<< len(mods)) - 1)
   if state or not s:s.append(hex(state))
   attrs['state']='|'.join(s)
  if self.delta==0:del attrs['delta']
  keys=('send_event','state','keysym','keycode','char','num','delta','focus','x','y','width','height')
  return '<%s event%s>'%(getattr(self.type,'name',self.type),''.join(' %s=%s'%(k,attrs[k]) for k in keys if k in attrs))
 __class_getitem__=classmethod(types.GenericAlias)
_support_default_root=True
_default_root=None
def NoDefaultRoot():
 global _support_default_root,_default_root
 _support_default_root=False
 _default_root=None
 del _default_root
def _get_default_root(what=None):
 if not _support_default_root:raise RuntimeError("No master specified and tkinter is configured to not support default root")
 if _default_root==None:
  if what:raise RuntimeError(f"Too early to {what}:no default root window")
  root=Tk()
  assert _default_root==root
 return _default_root
def _get_temp_root():
 global _support_default_root
 if not _support_default_root:raise RuntimeError("No master specified and tkinter is configured to not support default root")
 root=_default_root
 if root==None:
  assert _support_default_root
  _support_default_root=False
  root=Tk()
  _support_default_root=True
  assert _default_root==None
  root.withdraw()
  root._temporary=True
 return root
def _destroy_temp_root(master):
 if getattr(master,'_temporary',False):
  try:master.destroy()
  except:pass
def _tkerror(err):pass
def _exit(code=0):
 try:code=int(code)
 except:pass
 raise SystemExit(code)
_varnum=0
class Variable:
 _default=""
 _tk=None
 _tclCommands=None
 def __init__(self,master=None,value=None,name=None):
  if name!=None and not isinstance(name,str):raise TypeError("name must be a string")
  global _varnum
  if master==None:master=_get_default_root('create variable')
  self._root=master._root()
  self._tk=master.tk
  if name:self._name=name
  else:
   self._name='PY_VAR'+repr(_varnum)
   _varnum+=1
  if value!=None:self.initialize(value)
  elif not self._tk.getboolean(self._tk.call("info","exists",self._name)):self.initialize(self._default)
 def __del__(self):
  if self._tk==None:return
  if self._tk.getboolean(self._tk.call("info","exists",self._name)):self._tk.globalunsetvar(self._name)
  if self._tclCommands!=None:
   for name in self._tclCommands:self._tk.deletecommand(name)
   self._tclCommands=None
 def __str__(self):return self._name
 def set(self,value):return self._tk.globalsetvar(self._name,value)
 initialize=set
 def get(self):return self._tk.globalgetvar(self._name)
 def _register(self,callback):
  f=CallWrapper(callback,None,self._root).__call__
  cbname=repr(id(f))
  try:callback=callback.__func__
  except:pass
  try:cbname=cbname+callback.__name__
  except:pass
  self._tk.createcommand(cbname,f)
  if self._tclCommands==None:self._tclCommands=[]
  self._tclCommands.append(cbname)
  return cbname
 def trace_add(self,mode,callback):
  cbname=self._register(callback)
  self._tk.call('trace','add','variable',self._name,mode,(cbname,))
  return cbname
 def trace_remove(self,mode,cbname):
  self._tk.call('trace','remove','variable',self._name,mode,cbname)
  for m,ca in self.trace_info():
   if self._tk.splitlist(ca)[0]==cbname:break
  else:
   self._tk.deletecommand(cbname)
   try:self._tclCommands.remove(cbname)
   except:pass
 def trace_info(self):
  splitlist=self._tk.splitlist
  return [(splitlist(k),v) for k,v in map(splitlist,splitlist(self._tk.call('trace','info','variable',self._name)))]
 def trace_variable(self,mode,callback):
  warnings.warn("trace_variable() is deprecated and not supported with Tcl 9;\nuse trace_add() instead.",DeprecationWarning,stacklevel=2)
  cbname=self._register(callback)
  self._tk.call("trace","variable",self._name,mode,cbname)
  return cbname
 trace=trace_variable
 def trace_vdelete(self,mode,cbname):
  warnings.warn("trace_vdelete() is deprecated and not supported with Tcl 9;\nuse trace_remove() instead.",DeprecationWarning,stacklevel=2)
  self._tk.call("trace","vdelete",self._name,mode,cbname)
  cbname=self._tk.splitlist(cbname)[0]
  for m,ca in self.trace_info():
   if self._tk.splitlist(ca)[0]==cbname:break
  else:
   self._tk.deletecommand(cbname)
   try:self._tclCommands.remove(cbname)
   except:pass
 def trace_vinfo(self):
  warnings.warn("trace_vinfo() is deprecated and not supported with Tcl 9;\nuse trace_info() instead.",DeprecationWarning,stacklevel=2)
  return [self._tk.splitlist(x) for x in self._tk.splitlist(self._tk.call("trace","vinfo",self._name))]
 def __eq__(self,other):
  if not isinstance(other,Variable):return NotImplemented
  return (self._name==other._name and self.__class__.__name__==other.__class__.__name__ and self._tk==other._tk)
class StringVar(Variable):
 _default=""
 def __init__(self,master=None,value=None,name=None):Variable.__init__(self,master,value,name)
 def get(self):
  value=self._tk.globalgetvar(self._name)
  if isinstance(value,str):return value
  return str(value)
class IntVar(Variable):
 _default=0
 def __init__(self,master=None,value=None,name=None):Variable.__init__(self,master,value,name)
 def get(self):
  value=self._tk.globalgetvar(self._name)
  try:return self._tk.getint(value)
  except (TypeError,TclError):return int(self._tk.getdouble(value))
class DoubleVar(Variable):
 _default=0.0
 def __init__(self,master=None,value=None,name=None):Variable.__init__(self,master,value,name)
 def get(self):return self._tk.getdouble(self._tk.globalgetvar(self._name))
class BooleanVar(Variable):
 _default=False
 def __init__(self,master=None,value=None,name=None):Variable.__init__(self,master,value,name)
 def set(self,value):return self._tk.globalsetvar(self._name,self._tk.getboolean(value))
 initialize=set
 def get(self):
  try:return self._tk.getboolean(self._tk.globalgetvar(self._name))
  except TclError:raise ValueError("invalid literal for getboolean()")
def mainloop(n=0):_get_default_root('run the main loop').tk.mainloop(n)
getint=int
getdouble=float
def getboolean(s):
 try:return _get_default_root('use getboolean()').tk.getboolean(s)
 except TclError:raise ValueError("invalid literal for getboolean()")
class Misc:
 _last_child_ids=None
 _tclCommands=None
 def destroy(self):
  if self._tclCommands!=None:
   for name in self._tclCommands:self.tk.deletecommand(name)
   self._tclCommands=None
 def deletecommand(self,name):
  self.tk.deletecommand(name)
  try:self._tclCommands.remove(name)
  except:pass
 def tk_strictMotif(self,boolean=None):return self.tk.getboolean(self.tk.call('set','tk_strictMotif',boolean))
 def tk_bisque(self):self.tk.call('tk_bisque')
 def tk_setPalette(self,*args,**kw):self.tk.call(('tk_setPalette',)+_flatten(args)+_flatten(list(kw.items())))
 def wait_variable(self,name='PY_VAR'):self.tk.call('tkwait','variable',name)
 waitvar=wait_variable
 def wait_window(self,window=None):
  if window==None:window=self
  self.tk.call('tkwait','window',window._w)
 def wait_visibility(self,window=None):
  if window==None:window=self
  self.tk.call('tkwait','visibility',window._w)
 def setvar(self,name='PY_VAR',value='1'):self.tk.setvar(name,value)
 def getvar(self,name='PY_VAR'):return self.tk.getvar(name)
 def getint(self,s):
  try:return self.tk.getint(s)
  except TclError as exc:raise ValueError(str(exc))
 def getdouble(self,s):
  try:return self.tk.getdouble(s)
  except TclError as exc:raise ValueError(str(exc))
 def getboolean(self,s):
  try:return self.tk.getboolean(s)
  except TclError:raise ValueError("invalid literal for getboolean()")
 def focus_set(self):self.tk.call('focus',self._w)
 focus=focus_set
 def focus_force(self):self.tk.call('focus','-force',self._w)
 def focus_get(self):
  name=self.tk.call('focus')
  if name=='none' or not name:return None
  return self._nametowidget(name)
 def focus_displayof(self):
  name=self.tk.call('focus','-displayof',self._w)
  if name=='none' or not name:return None
  return self._nametowidget(name)
 def focus_lastfor(self):
  name=self.tk.call('focus','-lastfor',self._w)
  if name=='none' or not name:return None
  return self._nametowidget(name)
 def tk_focusFollowsMouse(self):self.tk.call('tk_focusFollowsMouse')
 def tk_focusNext(self):
  name=self.tk.call('tk_focusNext',self._w)
  if not name:return None
  return self._nametowidget(name)
 def tk_focusPrev(self):
  name=self.tk.call('tk_focusPrev',self._w)
  if not name:return None
  return self._nametowidget(name)
 def after(self,ms,func=None,*args,**kw):
  if func==None:
   self.tk.call('after',ms)
   return None
  else:
   def callit():
    try:func(*args,**kw)
    finally:
     try:self.deletecommand(name)
     except:pass
   try:callit.__name__=func.__name__
   except AttributeError:callit.__name__=type(func).__name__
   name=self._register(callit)
   return self.tk.call('after',ms,name)
 def after_idle(self,func,*args,**kw):return self.after('idle',func,*args,**kw)
 def after_cancel(self,id):
  if not id:raise ValueError('id must be a valid identifier returned from after or after_idle')
  try:
   data=self.tk.call('after','info',id)
   script=self.tk.splitlist(data)[0]
   self.deletecommand(script)
  except:pass
  self.tk.call('after','cancel',id)
 def after_info(self,id=None):return self.tk.splitlist(self.tk.call('after','info',id))
 def bell(self,displayof=0):self.tk.call(('bell',)+self._displayof(displayof))
 def tk_busy_cget(self,option):return self.tk.call('tk','busy','cget',self._w,'-'+option)
 busy_cget=tk_busy_cget
 def tk_busy_configure(self,cnf=None,**kw):
  if kw:cnf=_cnfmerge((cnf,kw))
  elif cnf:cnf=_cnfmerge(cnf)
  if cnf==None:return self._getconfigure('tk','busy','configure',self._w)
  if isinstance(cnf,str):return self._getconfigure1('tk','busy','configure',self._w,'-'+cnf)
  self.tk.call('tk','busy','configure',self._w,*self._options(cnf))
 busy_config=busy_configure=tk_busy_config=tk_busy_configure
 def tk_busy_current(self,pattern=None):
  return [self._nametowidget(x) for x in self.tk.splitlist(self.tk.call('tk','busy','current',pattern))]
 busy_current=tk_busy_current
 def tk_busy_forget(self):self.tk.call('tk','busy','forget',self._w)
 busy_forget=tk_busy_forget
 def tk_busy_hold(self,**kw):self.tk.call('tk','busy','hold',self._w,*self._options(kw))
 busy=busy_hold=tk_busy=tk_busy_hold
 def tk_busy_status(self):return self.tk.getboolean(self.tk.call('tk','busy','status',self._w))
 busy_status=tk_busy_status
 def clipboard_get(self,**kw):
  if 'type' not in kw and self._windowingsystem=='x11':
   try:
    kw['type']='UTF8_STRING'
    return self.tk.call(('clipboard','get')+self._options(kw))
   except TclError:del kw['type']
  return self.tk.call(('clipboard','get')+self._options(kw))
 def clipboard_clear(self,**kw):
  if 'displayof' not in kw:kw['displayof']=self._w
  self.tk.call(('clipboard','clear')+self._options(kw))
 def clipboard_append(self,string,**kw):
  if 'displayof' not in kw:kw['displayof']=self._w
  self.tk.call(('clipboard','append')+self._options(kw)+('--',string))
 def grab_current(self):
  name=self.tk.call('grab','current',self._w)
  if not name:return None
  return self._nametowidget(name)
 def grab_release(self):self.tk.call('grab','release',self._w)
 def grab_set(self):self.tk.call('grab','set',self._w)
 def grab_set_global(self):self.tk.call('grab','set','-global',self._w)
 def grab_status(self):
  status=self.tk.call('grab','status',self._w)
  if status=='none':status=None
  return status
 def option_add(self,pattern,value,priority=None):self.tk.call('option','add',pattern,value,priority)
 def option_clear(self):self.tk.call('option','clear')
 def option_get(self,name,className):return self.tk.call('option','get',self._w,name,className)
 def option_readfile(self,fileName,priority=None):self.tk.call('option','readfile',fileName,priority)
 def selection_clear(self,**kw):
  if 'displayof' not in kw:kw['displayof']=self._w
  self.tk.call(('selection','clear')+self._options(kw))
 def selection_get(self,**kw):
  if 'displayof' not in kw:kw['displayof']=self._w
  if 'type' not in kw and self._windowingsystem=='x11':
   try:
    kw['type']='UTF8_STRING'
    return self.tk.call(('selection','get')+self._options(kw))
   except TclError:del kw['type']
  return self.tk.call(('selection','get')+self._options(kw))
 def selection_handle(self,command,**kw):self.tk.call(('selection','handle')+self._options(kw)+(self._w,self._register(command)))
 def selection_own(self,**kw):self.tk.call(('selection','own')+self._options(kw)+(self._w,))
 def selection_own_get(self,**kw):
  if 'displayof' not in kw:kw['displayof']=self._w
  name=self.tk.call(('selection','own')+self._options(kw))
  if not name:return None
  return self._nametowidget(name)
 def send(self,interp,cmd,*args):return self.tk.call(('send',interp,cmd)+args)
 def lower(self,belowThis=None):self.tk.call('lower',self._w,belowThis)
 def tkraise(self,aboveThis=None):self.tk.call('raise',self._w,aboveThis)
 lift=tkraise
 def info_patchlevel(self):
  patchlevel=self.tk.call('info','patchlevel')
  return _parse_version(patchlevel)
 def winfo_atom(self,name,displayof=0):
  args=('winfo','atom')+self._displayof(displayof)+(name,)
  return self.tk.getint(self.tk.call(args))
 def winfo_atomname(self,id,displayof=0):
  args=('winfo','atomname')+self._displayof(displayof)+(id,)
  return self.tk.call(args)
 def winfo_cells(self):return self.tk.getint(self.tk.call('winfo','cells',self._w))
 def winfo_children(self):
  result=[]
  for child in self.tk.splitlist(self.tk.call('winfo','children',self._w)):
   try:result.append(self._nametowidget(child))
   except:pass
  return result
 def winfo_class(self):return self.tk.call('winfo','class',self._w)
 def winfo_colormapfull(self):return self.tk.getboolean(self.tk.call('winfo','colormapfull',self._w))
 def winfo_containing(self,rootX,rootY,displayof=0):
  args=('winfo','containing')+self._displayof(displayof)+(rootX,rootY)
  name=self.tk.call(args)
  if not name:return None
  return self._nametowidget(name)
 def winfo_depth(self):return self.tk.getint(self.tk.call('winfo','depth',self._w))
 def winfo_exists(self):return self.tk.getint(self.tk.call('winfo','exists',self._w))
 def winfo_fpixels(self,number):return self.tk.getdouble(self.tk.call('winfo','fpixels',self._w,number))
 def winfo_geometry(self):return self.tk.call('winfo','geometry',self._w)
 def winfo_height(self):return self.tk.getint(self.tk.call('winfo','height',self._w))
 def winfo_id(self):return int(self.tk.call('winfo','id',self._w),0)
 def winfo_interps(self,displayof=0):
  args=('winfo','interps')+self._displayof(displayof)
  return self.tk.splitlist(self.tk.call(args))
 def winfo_ismapped(self):return self.tk.getint(self.tk.call('winfo','ismapped',self._w))
 def winfo_manager(self):return self.tk.call('winfo','manager',self._w)
 def winfo_name(self):return self.tk.call('winfo','name',self._w)
 def winfo_parent(self):return self.tk.call('winfo','parent',self._w)
 def winfo_pathname(self,id,displayof=0):
  if isinstance(id,int):id=hex(id)
  args=('winfo','pathname')+self._displayof(displayof)+(id,)
  return self.tk.call(args)
 def winfo_pixels(self,number):return self.tk.getint(self.tk.call('winfo','pixels',self._w,number))
 def winfo_pointerx(self):return self.tk.getint(self.tk.call('winfo','pointerx',self._w))
 def winfo_pointerxy(self):return self._getints(self.tk.call('winfo','pointerxy',self._w))
 def winfo_pointery(self):return self.tk.getint(self.tk.call('winfo','pointery',self._w))
 def winfo_reqheight(self):return self.tk.getint(self.tk.call('winfo','reqheight',self._w))
 def winfo_reqwidth(self):return self.tk.getint(self.tk.call('winfo','reqwidth',self._w))
 def winfo_rgb(self,color):return self._getints(self.tk.call('winfo','rgb',self._w,color))
 def winfo_rootx(self):return self.tk.getint(self.tk.call('winfo','rootx',self._w))
 def winfo_rooty(self):return self.tk.getint(self.tk.call('winfo','rooty',self._w))
 def winfo_screen(self):return self.tk.call('winfo','screen',self._w)
 def winfo_screencells(self):return self.tk.getint(self.tk.call('winfo','screencells',self._w))
 def winfo_screendepth(self):return self.tk.getint(self.tk.call('winfo','screendepth',self._w))
 def winfo_screenheight(self):return self.tk.getint(self.tk.call('winfo','screenheight',self._w))
 def winfo_screenmmheight(self):return self.tk.getint(self.tk.call('winfo','screenmmheight',self._w))
 def winfo_screenmmwidth(self):return self.tk.getint(self.tk.call('winfo','screenmmwidth',self._w))
 def winfo_screenvisual(self):return self.tk.call('winfo','screenvisual',self._w)
 def winfo_screenwidth(self):return self.tk.getint(self.tk.call('winfo','screenwidth',self._w))
 def winfo_server(self):return self.tk.call('winfo','server',self._w)
 def winfo_toplevel(self):return self._nametowidget(self.tk.call('winfo','toplevel',self._w))
 def winfo_viewable(self):return self.tk.getint(self.tk.call('winfo','viewable',self._w))
 def winfo_visual(self):return self.tk.call('winfo','visual',self._w)
 def winfo_visualid(self):return self.tk.call('winfo','visualid',self._w)
 def winfo_visualsavailable(self,includeids=False):
  data=self.tk.call('winfo','visualsavailable',self._w,'includeids' if includeids else None)
  data=[self.tk.splitlist(x) for x in self.tk.splitlist(data)]
  return [self.__winfo_parseitem(x) for x in data]
 def __winfo_parseitem(self,t):return t[:1]+tuple(map(self.__winfo_getint,t[1:]))
 def __winfo_getint(self,x):return int(x,0)
 def winfo_vrootheight(self):return self.tk.getint(self.tk.call('winfo','vrootheight',self._w))
 def winfo_vrootwidth(self):return self.tk.getint(self.tk.call('winfo','vrootwidth',self._w))
 def winfo_vrootx(self):return self.tk.getint(self.tk.call('winfo','vrootx',self._w))
 def winfo_vrooty(self):return self.tk.getint(self.tk.call('winfo','vrooty',self._w))
 def winfo_width(self):return self.tk.getint(self.tk.call('winfo','width',self._w))
 def winfo_x(self):return self.tk.getint(self.tk.call('winfo','x',self._w))
 def winfo_y(self):return self.tk.getint(self.tk.call('winfo','y',self._w))
 def update(self):self.tk.call('update')
 def update_idletasks(self):self.tk.call('update','idletasks')
 def bindtags(self,tagList=None):
  if tagList==None:return self.tk.splitlist(self.tk.call('bindtags',self._w))
  else:self.tk.call('bindtags',self._w,tagList)
 def _bind(self,what,sequence,func,add,needcleanup=1):
  if isinstance(func,str):self.tk.call(what+(sequence,func))
  elif func:
   funcid=self._register(func,self._substitute,needcleanup)
   cmd=('%sif {"[%s %s]" is "break"} break\n'%(add and '+' or '',funcid,self._subst_format_str))
   self.tk.call(what+(sequence,cmd))
   return funcid
  elif sequence:return self.tk.call(what+(sequence,))
  else:return self.tk.splitlist(self.tk.call(what))
 def bind(self,sequence=None,func=None,add=None):return self._bind(('bind',self._w),sequence,func,add)
 def unbind(self,sequence,funcid=None):self._unbind(('bind',self._w,sequence),funcid)
 def _unbind(self,what,funcid=None):
  if funcid==None:self.tk.call(*what,'')
  else:
   lines=self.tk.call(what).split('\n')
   prefix=f'if {{"[{funcid} '
   keep='\n'.join(line for line in lines if not line.startswith(prefix))
   if not keep.strip():keep=''
   self.tk.call(*what,keep)
   self.deletecommand(funcid)
 def bind_all(self,sequence=None,func=None,add=None):return self._root()._bind(('bind','all'),sequence,func,add,True)
 def unbind_all(self,sequence):self._root()._unbind(('bind','all',sequence))
 def bind_class(self,className,sequence=None,func=None,add=None):return self._root()._bind(('bind',className),sequence,func,add,True)
 def unbind_class(self,className,sequence):self._root()._unbind(('bind',className,sequence))
 def mainloop(self,n=0):self.tk.mainloop(n)
 def quit(self):self.tk.quit()
 def _getints(self,string):
  if string:return tuple(map(self.tk.getint,self.tk.splitlist(string)))
 def _getdoubles(self,string):
  if string:return tuple(map(self.tk.getdouble,self.tk.splitlist(string)))
 def _getboolean(self,string):
  if string:return self.tk.getboolean(string)
 def _displayof(self,displayof):
  if displayof:return('-displayof',displayof)
  if displayof==None:return('-displayof',self._w)
  return()
 @property
 def _windowingsystem(self):
  try:return self._root()._windowingsystem_cached
  except AttributeError:
   ws=self._root()._windowingsystem_cached=self.tk.call('tk','windowingsystem')
   return ws
 def _options(self,cnf,kw=None):
  if kw:cnf=_cnfmerge((cnf,kw))
  else:cnf=_cnfmerge(cnf)
  res=()
  for k,v in cnf.items():
   if v!=None:
    if k[-1]=='_':k=k[:-1]
    if callable(v):v=self._register(v)
    elif isinstance(v,(tuple,list)):
     nv=[]
     for item in v:
      if isinstance(item,int):nv.append(str(item))
      elif isinstance(item,str):nv.append(_stringify(item))
      else:break
     else:v=' '.join(nv)
    res=res+('-'+k,v)
  return res
 def nametowidget(self,name):
  name=str(name).split('.')
  w=self
  if not name[0]:
   w=w._root()
   name=name[1:]
  for n in name:
   if not n:break
   w=w.children[n]
  return w
 _nametowidget=nametowidget
 def _register(self,func,subst=None,needcleanup=1):
  f=CallWrapper(func,subst,self).__call__
  name=repr(id(f))
  try:func=func.__func__
  except:pass
  try:name=name+func.__name__
  except:pass
  self.tk.createcommand(name,f)
  if needcleanup:
   if self._tclCommands==None:self._tclCommands=[]
   self._tclCommands.append(name)
  return name
 register=_register
 def _root(self):
  w=self
  while w.master!=None:w=w.master
  return w
 _subst_format=('%#','%b','%f','%h','%k','%s','%t','%w','%x','%y','%A','%E','%K','%N','%W','%T','%X','%Y','%D')
 _subst_format_str=" ".join(_subst_format)
 def _substitute(self,*args):
  if len(args)!=len(self._subst_format):return args
  getboolean=self.tk.getboolean
  getint=self.tk.getint
  def getint_event(s):
   try:return getint(s)
   except (ValueError,TclError):return s
  if any(isinstance(s,tuple) for s in args):args=[s[0] if isinstance(s,tuple) and len(s)==1 else s for s in args]
  nsign,b,f,h,k,s,t,w,x,y,A,E,K,N,W,T,X,Y,D=args
  e=Event()
  e.serial=getint(nsign)
  e.num=getint_event(b)
  try:e.focus=getboolean(f)
  except:pass
  e.height=getint_event(h)
  e.keycode=getint_event(k)
  e.state=getint_event(s)
  e.time=getint_event(t)
  e.width=getint_event(w)
  e.x=getint_event(x)
  e.y=getint_event(y)
  e.char=A
  try:e.send_event=getboolean(E)
  except:pass
  e.keysym=K
  e.keysym_num=getint_event(N)
  try:e.type=EventType(T)
  except ValueError:
   try:e.type=EventType(str(T))
   except ValueError:e.type=T
  try:e.widget=self._nametowidget(W)
  except KeyError:e.widget=W
  e.x_root=getint_event(X)
  e.y_root=getint_event(Y)
  try:e.delta=getint(D)
  except (ValueError,TclError):e.delta=0
  return (e,)
 def _report_exception(self):
  exc,val,tb=sys.exc_info()
  root=self._root()
  root.report_callback_exception(exc,val,tb)
 def _getconfigure(self,*args):
  cnf={}
  for x in self.tk.splitlist(self.tk.call(*args)):
   x=self.tk.splitlist(x)
   cnf[x[0][1:]]=(x[0][1:],)+x[1:]
  return cnf
 def _getconfigure1(self,*args):
  x=self.tk.splitlist(self.tk.call(*args))
  return (x[0][1:],)+x[1:]
 def _configure(self,cmd,cnf,kw):
  if kw:cnf=_cnfmerge((cnf,kw))
  elif cnf:cnf=_cnfmerge(cnf)
  if cnf==None:return self._getconfigure(_flatten((self._w,cmd)))
  if isinstance(cnf,str):return self._getconfigure1(_flatten((self._w,cmd,'-'+cnf)))
  self.tk.call(_flatten((self._w,cmd))+self._options(cnf))
 def configure(self,cnf=None,**kw):return self._configure('configure',cnf,kw)
 config=configure
 def cget(self,key):return self.tk.call(self._w,'cget','-'+key)
 __getitem__=cget
 def __setitem__(self,key,value):self.configure({key:value})
 def keys(self):
  splitlist=self.tk.splitlist
  return [splitlist(x)[0][1:] for x in splitlist(self.tk.call(self._w,'configure'))]
 def __str__(self):return self._w
 def __repr__(self):return '<%s.%s object %s>'%(self.__class__.__module__,self.__class__.__qualname__,self._w)
 _noarg_=['_noarg_']
 def pack_propagate(self,flag=_noarg_):
  if flag==Misc._noarg_:return self._getboolean(self.tk.call('pack','propagate',self._w))
  else:self.tk.call('pack','propagate',self._w,flag)
 propagate=pack_propagate
 def pack_slaves(self):return [self._nametowidget(x) for x in self.tk.splitlist(self.tk.call('pack','slaves',self._w))]
 slaves=pack_slaves
 def place_slaves(self):return [self._nametowidget(x) for x in self.tk.splitlist(self.tk.call('place','slaves',self._w))]
 def grid_anchor(self,anchor=None):self.tk.call('grid','anchor',self._w,anchor)
 anchor=grid_anchor
 def grid_bbox(self,column=None,row=None,col2=None,row2=None):
  args=('grid','bbox',self._w)
  if column!=None and row!=None:args=args+(column,row)
  if col2!=None and row2!=None:args=args+(col2,row2)
  return self._getints(self.tk.call(*args)) or None
 bbox=grid_bbox
 def _gridconvvalue(self,value):
  if isinstance(value,(str,_tkinter.Tcl_Obj)):
   try:
    svalue=str(value)
    if not svalue:return None
    elif '.' in svalue:return self.tk.getdouble(svalue)
    else:return self.tk.getint(svalue)
   except:pass
  return value
 def _grid_configure(self,command,index,cnf,kw):
  if isinstance(cnf,str) and not kw:
   if cnf[-1:]=='_':cnf=cnf[:-1]
   if cnf[:1]!='-':cnf='-'+cnf
   options=(cnf,)
  else:options=self._options(cnf,kw)
  if not options:return _splitdict(self.tk,self.tk.call('grid',command,self._w,index),conv=self._gridconvvalue)
  res=self.tk.call(('grid',command,self._w,index)+options)
  if len(options)==1:return self._gridconvvalue(res)
 def grid_columnconfigure(self,index,cnf={},**kw):return self._grid_configure('columnconfigure',index,cnf,kw)
 columnconfigure=grid_columnconfigure
 def grid_location(self,x,y):return self._getints(self.tk.call('grid','location',self._w,x,y)) or None
 def grid_propagate(self,flag=_noarg_):
  if flag==Misc._noarg_:return self._getboolean(self.tk.call('grid','propagate',self._w))
  else:self.tk.call('grid','propagate',self._w,flag)
 def grid_rowconfigure(self,index,cnf={},**kw):return self._grid_configure('rowconfigure',index,cnf,kw)
 rowconfigure=grid_rowconfigure
 def grid_size(self):return self._getints(self.tk.call('grid','size',self._w)) or None
 size=grid_size
 def grid_slaves(self,row=None,column=None):
  args=()
  if row!=None:args=args+('-row',row)
  if column!=None:args=args+('-column',column)
  return [self._nametowidget(x) for x in self.tk.splitlist(self.tk.call(('grid','slaves',self._w)+args))]
 def event_add(self,virtual,*sequences):
  args=('event','add',virtual)+sequences
  self.tk.call(args)
 def event_delete(self,virtual,*sequences):
  args=('event','delete',virtual)+sequences
  self.tk.call(args)
 def event_generate(self,sequence,**kw):
  args=('event','generate',self._w,sequence)
  for k,v in kw.items():args=args+('-%s'%k,str(v))
  self.tk.call(args)
 def event_info(self,virtual=None):return self.tk.splitlist(self.tk.call('event','info',virtual))
 def image_names(self):return self.tk.splitlist(self.tk.call('image','names'))
 def image_types(self):return self.tk.splitlist(self.tk.call('image','types'))
class CallWrapper:
 def __init__(self,func,subst,widget):
  self.func=func
  self.subst=subst
  self.widget=widget
 def __call__(self,*args):
  try:
   if self.subst:args=self.subst(*args)
   return self.func(*args)
  except SystemExit:raise
  except:self.widget._report_exception()
class XView:
 def xview(self,*args):
  res=self.tk.call(self._w,'xview',*args)
  if not args:return self._getdoubles(res)
 def xview_moveto(self,fraction):self.tk.call(self._w,'xview','moveto',fraction)
 def xview_scroll(self,number,what):self.tk.call(self._w,'xview','scroll',number,what)
class YView:
 def yview(self,*args):
  res=self.tk.call(self._w,'yview',*args)
  if not args:return self._getdoubles(res)
 def yview_moveto(self,fraction):self.tk.call(self._w,'yview','moveto',fraction)
 def yview_scroll(self,number,what):self.tk.call(self._w,'yview','scroll',number,what)
class Wm:
 def wm_aspect(self,minNumer=None,minDenom=None,maxNumer=None,maxDenom=None):
  return self._getints(self.tk.call('wm','aspect',self._w,minNumer,minDenom,maxNumer,maxDenom))
 aspect=wm_aspect
 def wm_attributes(self,*args,return_python_dict=False,**kwargs):
  if not kwargs:
   if not args:
    res=self.tk.call('wm','attributes',self._w)
    return _splitdict(self.tk,res) if return_python_dict else self.tk.splitlist(res)
   if len(args)==1 and args[0]!=None:
    option=args[0]
    if option[0]=='-':option=option[1:]
    return self.tk.call('wm','attributes',self._w,'-'+option)
   return self.tk.call('wm','attributes',self._w,*args)
  elif args:raise TypeError('wm_attribute() options have been specified as\npositional and keyword arguments')
  else:self.tk.call('wm','attributes',self._w,*self._options(kwargs))
 attributes=wm_attributes
 def wm_client(self,name=None):return self.tk.call('wm','client',self._w,name)
 client=wm_client
 def wm_colormapwindows(self,*wlist):
  if len(wlist)>1:wlist=(wlist,)
  args=('wm','colormapwindows',self._w)+wlist
  if wlist:self.tk.call(args)
  else:return [self._nametowidget(x) for x in self.tk.splitlist(self.tk.call(args))]
 colormapwindows=wm_colormapwindows
 def wm_command(self,value=None):return self.tk.call('wm','command',self._w,value)
 command=wm_command
 def wm_deiconify(self):return self.tk.call('wm','deiconify',self._w)
 deiconify=wm_deiconify
 def wm_focusmodel(self,model=None):return self.tk.call('wm','focusmodel',self._w,model)
 focusmodel=wm_focusmodel
 def wm_forget(self,window):self.tk.call('wm','forget',window)
 forget=wm_forget
 def wm_frame(self):return self.tk.call('wm','frame',self._w)
 frame=wm_frame
 def wm_geometry(self,newGeometry=None):return self.tk.call('wm','geometry',self._w,newGeometry)
 geometry=wm_geometry
 def wm_grid(self,baseWidth=None,baseHeight=None,widthInc=None,heightInc=None):return self._getints(self.tk.call('wm','grid',self._w,baseWidth,baseHeight,widthInc,heightInc))
 grid=wm_grid
 def wm_group(self,pathName=None):return self.tk.call('wm','group',self._w,pathName)
 group=wm_group
 def wm_iconbitmap(self,bitmap=None,default=None):return self.tk.call('wm','iconbitmap',self._w,'-default',default)if default!=None else self.tk.call('wm','iconbitmap',self._w,bitmap)
 iconbitmap=wm_iconbitmap
 def wm_iconify(self):return self.tk.call('wm','iconify',self._w)
 iconify=wm_iconify
 def wm_iconmask(self,bitmap=None):return self.tk.call('wm','iconmask',self._w,bitmap)
 iconmask=wm_iconmask
 def wm_iconname(self,newName=None):return self.tk.call('wm','iconname',self._w,newName)
 iconname=wm_iconname
 def wm_iconphoto(self,default=False,*args):
  if default:self.tk.call('wm','iconphoto',self._w,"-default",*args)
  else:self.tk.call('wm','iconphoto',self._w,*args)
 iconphoto=wm_iconphoto
 def wm_iconposition(self,x=None,y=None):return self._getints(self.tk.call('wm','iconposition',self._w,x,y))
 iconposition=wm_iconposition
 def wm_iconwindow(self,pathName=None):return self.tk.call('wm','iconwindow',self._w,pathName)
 iconwindow=wm_iconwindow
 def wm_manage(self,widget):self.tk.call('wm','manage',widget)
 manage=wm_manage
 def wm_maxsize(self,width=None,height=None):return self._getints(self.tk.call('wm','maxsize',self._w,width,height))
 maxsize=wm_maxsize
 def wm_minsize(self,width=None,height=None):return self._getints(self.tk.call('wm','minsize',self._w,width,height))
 minsize=wm_minsize
 def wm_overrideredirect(self,boolean=None):return self._getboolean(self.tk.call('wm','overrideredirect',self._w,boolean))
 overrideredirect=wm_overrideredirect
 def wm_positionfrom(self,who=None):return self.tk.call('wm','positionfrom',self._w,who)
 positionfrom=wm_positionfrom
 def wm_protocol(self,name=None,func=None):return self.tk.call('wm','protocol',self._w,name,self._register(func) if callable(func) else func)
 protocol=wm_protocol
 def wm_resizable(self,width=None,height=None):return self.tk.call('wm','resizable',self._w,width,height)
 resizable=wm_resizable
 def wm_sizefrom(self,who=None):return self.tk.call('wm','sizefrom',self._w,who)
 sizefrom=wm_sizefrom
 def wm_state(self,newstate=None):return self.tk.call('wm','state',self._w,newstate)
 state=wm_state
 def wm_title(self,string=None):return self.tk.call('wm','title',self._w,string)
 title=wm_title
 def wm_transient(self,master=None):return self.tk.call('wm','transient',self._w,master)
 transient=wm_transient
 def wm_withdraw(self):return self.tk.call('wm','withdraw',self._w)
 withdraw=wm_withdraw
class Tk(Misc,Wm):
 _w='.'
 def __init__(self,screenName=None,baseName=None,className='Tk',useTk=True,sync=False,use=None):
  self.master=None
  self.children={}
  self._tkloaded=False
  self.tk=None
  if baseName==None:
   baseName=os.path.basename(sys.argv[0])
   baseName,ext=os.path.splitext(baseName)
   if ext not in ('.py','.pyc'):baseName=baseName+ext
  interactive=False
  self.tk=_tkinter.create(screenName,baseName,className,interactive,wantobjects,useTk,sync,use)
  if _debug:self.tk.settrace(_print_command)
  if useTk:self._loadtk()
  if not sys.flags.ignore_environment:self.readprofile(baseName,className)
 def loadtk(self):
  if not self._tkloaded:
   self.tk.loadtk()
   self._loadtk()
 def _loadtk(self):
  self._tkloaded=True
  global _default_root
  tk_version=self.tk.getvar('tk_version')
  if tk_version!=_tkinter.TK_VERSION:raise RuntimeError("tk.h version (%s) doesn't match libtk.a version (%s)"%(_tkinter.TK_VERSION,tk_version))
  tcl_version=str(self.tk.getvar('tcl_version'))
  if tcl_version!=_tkinter.TCL_VERSION:raise RuntimeError("tcl.h version (%s) doesn't match libtcl.a version (%s)" %(_tkinter.TCL_VERSION,tcl_version))
  if self._tclCommands==None:self._tclCommands=[]
  self.tk.createcommand('tkerror',_tkerror)
  self.tk.createcommand('exit',_exit)
  self._tclCommands.append('tkerror')
  self._tclCommands.append('exit')
  if _support_default_root and _default_root==None:_default_root=self
  self.protocol("WM_DELETE_WINDOW",self.destroy)
 def destroy(self):
  for c in list(self.children.values()):c.destroy()
  self.tk.call('destroy',self._w)
  Misc.destroy(self)
  global _default_root
  if _support_default_root and _default_root==self:_default_root=None
 def readprofile(self,baseName,className):
  home=os.environ['HOME'] if 'HOME' in os.environ else os.curdir
  class_tcl=os.path.join(home,'.%s.tcl'%className)
  class_py=os.path.join(home,'.%s.py'%className)
  base_tcl=os.path.join(home,'.%s.tcl'%baseName)
  base_py=os.path.join(home,'.%s.py'%baseName)
  dir={'self':self}
  exec('from tkinter import *',dir)
  if os.path.isfile(class_tcl):self.tk.call('source',class_tcl)
  if os.path.isfile(class_py):exec(open(class_py).read(),dir)
  if os.path.isfile(base_tcl):self.tk.call('source',base_tcl)
  if os.path.isfile(base_py):exec(open(base_py).read(),dir)
 def report_callback_exception(self,exc,val,tb):
  print("Exception in Tkinter callback",file=sys.stderr)
  sys.last_exc=val
  sys.last_type=exc
  sys.last_value=val
  sys.last_traceback=tb
  traceback.print_exception(exc,val,tb)
 def __getattr__(self,attr):return getattr(self.tk,attr)
def _print_command(cmd,*,file=sys.stderr):
 assert isinstance(cmd,tuple)
 cmd=_join(cmd)
 print(cmd,file=file)
def Tcl(screenName=None,baseName=None,className='Tk',useTk=False):return Tk(screenName,baseName,className,useTk)
class Pack:
 def pack_configure(self,cnf={},**kw):self.tk.call(('pack','configure',self._w)+self._options(cnf,kw))
 pack=configure=config=pack_configure
 def pack_forget(self):self.tk.call('pack','forget',self._w)
 forget=pack_forget
 def pack_info(self):
  d=_splitdict(self.tk,self.tk.call('pack','info',self._w))
  if 'in' in d:d['in']=self.nametowidget(d['in'])
  return d
 info=pack_info
 propagate=pack_propagate=Misc.pack_propagate
 slaves=pack_slaves=Misc.pack_slaves
class Place:
 def place_configure(self,cnf={},**kw):self.tk.call(('place','configure',self._w)+self._options(cnf,kw))
 place=configure=config=place_configure
 def place_forget(self):self.tk.call('place','forget',self._w)
 forget=place_forget
 def place_info(self):
  d=_splitdict(self.tk,self.tk.call('place','info',self._w))
  if 'in' in d:d['in']=self.nametowidget(d['in'])
  return d
 info=place_info
 slaves=place_slaves=Misc.place_slaves
class Grid:
 def grid_configure(self,cnf={},**kw):self.tk.call(('grid','configure',self._w)+self._options(cnf,kw))
 grid=configure=config=grid_configure
 bbox=grid_bbox=Misc.grid_bbox
 columnconfigure=grid_columnconfigure=Misc.grid_columnconfigure
 def grid_forget(self):self.tk.call('grid','forget',self._w)
 forget=grid_forget
 def grid_remove(self):self.tk.call('grid','remove',self._w)
 def grid_info(self):
  d=_splitdict(self.tk,self.tk.call('grid','info',self._w))
  if 'in' in d:d['in']=self.nametowidget(d['in'])
  return d
 info=grid_info
 location=grid_location=Misc.grid_location
 propagate=grid_propagate=Misc.grid_propagate
 rowconfigure=grid_rowconfigure=Misc.grid_rowconfigure
 size=grid_size=Misc.grid_size
 slaves=grid_slaves=Misc.grid_slaves
class BaseWidget(Misc):
 def _setup(self,master,cnf):
  if master==None:master=_get_default_root()
  self.master=master
  self.tk=master.tk
  name=None
  if 'name' in cnf:
   name=cnf['name']
   del cnf['name']
  if not name:
   name=self.__class__.__name__.lower()
   if name[-1].isdigit():name+="!"
   if master._last_child_ids==None:master._last_child_ids={}
   count=master._last_child_ids.get(name,0)+1
   master._last_child_ids[name]=count
   name='!%s'%(name,) if count==1 else'!%s%d'%(name,count)
  self._name=name
  self._w='.'+name if master._w=='.' else master._w+'.'+name
  self.children={}
  if self._name in self.master.children:self.master.children[self._name].destroy()
  self.master.children[self._name]=self
 def __init__(self,master,widgetName,cnf={},kw={},extra=()):
  if kw:cnf=_cnfmerge((cnf,kw))
  self.widgetName=widgetName
  self._setup(master,cnf)
  if self._tclCommands==None:self._tclCommands=[]
  classes=[(k,v) for k,v in cnf.items() if isinstance(k,type)]
  for k,v in classes:del cnf[k]
  self.tk.call((widgetName,self._w)+extra+self._options(cnf))
  for k,v in classes:k.configure(self,v)
 def destroy(self):
  for c in list(self.children.values()):c.destroy()
  self.tk.call('destroy',self._w)
  if self._name in self.master.children:del self.master.children[self._name]
  Misc.destroy(self)
 def _do(self,name,args=()):return self.tk.call((self._w,name)+args)
class Widget(BaseWidget,Pack,Place,Grid):pass
class Toplevel(BaseWidget,Wm):
 def __init__(self,master=None,cnf={},**kw):
  if kw:cnf=_cnfmerge((cnf,kw))
  extra=()
  for wmkey in ['screen','class_','class','visual','colormap']:
   if wmkey in cnf:
    val=cnf[wmkey]
    opt='-'+wmkey[:-1] if wmkey[-1]=='_' else '-'+wmkey
    extra=extra+(opt,val)
    del cnf[wmkey]
  BaseWidget.__init__(self,master,'toplevel',cnf,{},extra)
  root=self._root()
  self.iconname(root.iconname())
  self.title(root.title())
  self.protocol("WM_DELETE_WINDOW",self.destroy)
class Button(Widget):
 def __init__(self,master=None,cnf={},**kw):Widget.__init__(self,master,'button',cnf,kw)
 def flash(self):self.tk.call(self._w,'flash')
 def invoke(self):return self.tk.call(self._w,'invoke')
class Canvas(Widget,XView,YView):
 def __init__(self,master=None,cnf={},**kw):Widget.__init__(self,master,'canvas',cnf,kw)
 def addtag(self,*args):self.tk.call((self._w,'addtag')+args)
 def addtag_above(self,newtag,tagOrId):self.addtag(newtag,'above',tagOrId)
 def addtag_all(self,newtag):self.addtag(newtag,'all')
 def addtag_below(self,newtag,tagOrId):self.addtag(newtag,'below',tagOrId)
 def addtag_closest(self,newtag,x,y,halo=None,start=None):self.addtag(newtag,'closest',x,y,halo,start)
 def addtag_enclosed(self,newtag,x1,y1,x2,y2):self.addtag(newtag,'enclosed',x1,y1,x2,y2)
 def addtag_overlapping(self,newtag,x1,y1,x2,y2):self.addtag(newtag,'overlapping',x1,y1,x2,y2)
 def addtag_withtag(self,newtag,tagOrId):self.addtag(newtag,'withtag',tagOrId)
 def bbox(self,*args):return self._getints(self.tk.call((self._w,'bbox')+args)) or None
 def tag_unbind(self,tagOrId,sequence,funcid=None):self._unbind((self._w,'bind',tagOrId,sequence),funcid)
 def tag_bind(self,tagOrId,sequence=None,func=None,add=None):return self._bind((self._w,'bind',tagOrId),sequence,func,add)
 def canvasx(self,screenx,gridspacing=None):return self.tk.getdouble(self.tk.call(self._w,'canvasx',screenx,gridspacing))
 def canvasy(self,screeny,gridspacing=None):return self.tk.getdouble(self.tk.call(self._w,'canvasy',screeny,gridspacing))
 def coords(self,*args):
  args=_flatten(args)
  return [self.tk.getdouble(x) for x in self.tk.splitlist(self.tk.call((self._w,'coords')+args))]
 def _create(self,itemType,args,kw):
  args=_flatten(args)
  cnf=args[-1]
  if isinstance(cnf,(dict,tuple)):args=args[:-1]
  else:cnf={}
  return self.tk.getint(self.tk.call(self._w,'create',itemType,*(args+self._options(cnf,kw))))
 def create_arc(self,*args,**kw):return self._create('arc',args,kw)
 def create_bitmap(self,*args,**kw):return self._create('bitmap',args,kw)
 def create_image(self,*args,**kw):return self._create('image',args,kw)
 def create_line(self,*args,**kw):return self._create('line',args,kw)
 def create_oval(self,*args,**kw):return self._create('oval',args,kw)
 def create_polygon(self,*args,**kw):return self._create('polygon',args,kw)
 def create_rectangle(self,*args,**kw):return self._create('rectangle',args,kw)
 def create_text(self,*args,**kw):return self._create('text',args,kw)
 def create_window(self,*args,**kw):return self._create('window',args,kw)
 def dchars(self,*args):self.tk.call((self._w,'dchars')+args)
 def delete(self,*args):self.tk.call((self._w,'delete')+args)
 def dtag(self,*args):self.tk.call((self._w,'dtag')+args)
 def find(self,*args):return self._getints(self.tk.call((self._w,'find')+args)) or ()
 def find_above(self,tagOrId):return self.find('above',tagOrId)
 def find_all(self):return self.find('all')
 def find_below(self,tagOrId):return self.find('below',tagOrId)
 def find_closest(self,x,y,halo=None,start=None):return self.find('closest',x,y,halo,start)
 def find_enclosed(self,x1,y1,x2,y2):return self.find('enclosed',x1,y1,x2,y2)
 def find_overlapping(self,x1,y1,x2,y2):return self.find('overlapping',x1,y1,x2,y2)
 def find_withtag(self,tagOrId):return self.find('withtag',tagOrId)
 def focus(self,*args):return self.tk.call((self._w,'focus')+args)
 def gettags(self,*args):return self.tk.splitlist(self.tk.call((self._w,'gettags')+args))
 def icursor(self,*args):self.tk.call((self._w,'icursor')+args)
 def index(self,*args):return self.tk.getint(self.tk.call((self._w,'index')+args))
 def insert(self,*args):self.tk.call((self._w,'insert')+args)
 def itemcget(self,tagOrId,option):return self.tk.call((self._w,'itemcget')+(tagOrId,'-'+option))
 def itemconfigure(self,tagOrId,cnf=None,**kw):return self._configure(('itemconfigure',tagOrId),cnf,kw)
 itemconfig=itemconfigure
 def tag_lower(self,*args):self.tk.call((self._w,'lower')+args)
 lower=tag_lower
 def move(self,*args):self.tk.call((self._w,'move')+args)
 def moveto(self,tagOrId,x='',y=''):self.tk.call(self._w,'moveto',tagOrId,x,y)
 def postscript(self,cnf={},**kw):return self.tk.call((self._w,'postscript')+self._options(cnf,kw))
 def tag_raise(self,*args):self.tk.call((self._w,'raise')+args)
 lift=tkraise=tag_raise
 def scale(self,*args):self.tk.call((self._w,'scale')+args)
 def scan_mark(self,x,y):self.tk.call(self._w,'scan','mark',x,y)
 def scan_dragto(self,x,y,gain=10):self.tk.call(self._w,'scan','dragto',x,y,gain)
 def select_adjust(self,tagOrId,index):self.tk.call(self._w,'select','adjust',tagOrId,index)
 def select_clear(self):self.tk.call(self._w,'select','clear')
 def select_from(self,tagOrId,index):self.tk.call(self._w,'select','from',tagOrId,index)
 def select_item(self):return self.tk.call(self._w,'select','item') or None
 def select_to(self,tagOrId,index):self.tk.call(self._w,'select','to',tagOrId,index)
 def type(self,tagOrId):return self.tk.call(self._w,'type',tagOrId) or None
_checkbutton_count=0
class Checkbutton(Widget):
 def __init__(self,master=None,cnf={},**kw):Widget.__init__(self,master,'checkbutton',cnf,kw)
 def _setup(self,master,cnf):
  if not cnf.get('name'):
   global _checkbutton_count
   name=self.__class__.__name__.lower()
   _checkbutton_count+=1
   cnf['name']=f'!{name}-{_checkbutton_count}'
  super()._setup(master,cnf)
 def deselect(self):self.tk.call(self._w,'deselect')
 def flash(self):self.tk.call(self._w,'flash')
 def invoke(self):return self.tk.call(self._w,'invoke')
 def select(self):self.tk.call(self._w,'select')
 def toggle(self):self.tk.call(self._w,'toggle')
class Entry(Widget,XView):
 def __init__(self,master=None,cnf={},**kw):Widget.__init__(self,master,'entry',cnf,kw)
 def delete(self,first,last=None):self.tk.call(self._w,'delete',first,last)
 def get(self):return self.tk.call(self._w,'get')
 def icursor(self,index):self.tk.call(self._w,'icursor',index)
 def index(self,index):return self.tk.getint(self.tk.call(self._w,'index',index))
 def insert(self,index,string):self.tk.call(self._w,'insert',index,string)
 def scan_mark(self,x):self.tk.call(self._w,'scan','mark',x)
 def scan_dragto(self,x):self.tk.call(self._w,'scan','dragto',x)
 def selection_adjust(self,index):self.tk.call(self._w,'selection','adjust',index)
 select_adjust=selection_adjust
 def selection_clear(self):self.tk.call(self._w,'selection','clear')
 select_clear=selection_clear
 def selection_from(self,index):self.tk.call(self._w,'selection','from',index)
 select_from=selection_from
 def selection_present(self):return self.tk.getboolean(self.tk.call(self._w,'selection','present'))
 select_present=selection_present
 def selection_range(self,start,end):self.tk.call(self._w,'selection','range',start,end)
 select_range=selection_range
 def selection_to(self,index):self.tk.call(self._w,'selection','to',index)
 select_to=selection_to
class Frame(Widget):
 def __init__(self,master=None,cnf={},**kw):
  cnf=_cnfmerge((cnf,kw))
  extra=()
  if 'class_' in cnf:
   extra=('-class',cnf['class_'])
   del cnf['class_']
  elif 'class' in cnf:
   extra=('-class',cnf['class'])
   del cnf['class']
  Widget.__init__(self,master,'frame',cnf,{},extra)
class Label(Widget):
 def __init__(self,master=None,cnf={},**kw):Widget.__init__(self,master,'label',cnf,kw)
class Listbox(Widget,XView,YView):
 def __init__(self,master=None,cnf={},**kw):Widget.__init__(self,master,'listbox',cnf,kw)
 def activate(self,index):self.tk.call(self._w,'activate',index)
 def bbox(self,index):return self._getints(self.tk.call(self._w,'bbox',index)) or None
 def curselection(self):return self._getints(self.tk.call(self._w,'curselection')) or ()
 def delete(self,first,last=None):self.tk.call(self._w,'delete',first,last)
 def get(self,first,last=None):return self.tk.splitlist(self.tk.call(self._w,'get',first,last)) if last!=None else self.tk.call(self._w,'get',first)
 def index(self,index):
  i=self.tk.call(self._w,'index',index)
  return None if i=='none' else self.tk.getint(i)
 def insert(self,index,*elements):self.tk.call((self._w,'insert',index)+elements)
 def nearest(self,y):return self.tk.getint(self.tk.call(self._w,'nearest',y))
 def scan_mark(self,x,y):self.tk.call(self._w,'scan','mark',x,y)
 def scan_dragto(self,x,y):self.tk.call(self._w,'scan','dragto',x,y)
 def see(self,index):self.tk.call(self._w,'see',index)
 def selection_anchor(self,index):self.tk.call(self._w,'selection','anchor',index)
 select_anchor=selection_anchor
 def selection_clear(self,first,last=None):self.tk.call(self._w,'selection','clear',first,last)
 select_clear=selection_clear
 def selection_includes(self,index):return self.tk.getboolean(self.tk.call(self._w,'selection','includes',index))
 select_includes=selection_includes
 def selection_set(self,first,last=None):self.tk.call(self._w,'selection','set',first,last)
 select_set=selection_set
 def size(self):return self.tk.getint(self.tk.call(self._w,'size'))
 def itemcget(self,index,option):return self.tk.call((self._w,'itemcget')+(index,'-'+option))
 def itemconfigure(self,index,cnf=None,**kw):return self._configure(('itemconfigure',index),cnf,kw)
 itemconfig=itemconfigure
class Menu(Widget):
 def __init__(self,master=None,cnf={},**kw):Widget.__init__(self,master,'menu',cnf,kw)
 def tk_popup(self,x,y,entry=""):self.tk.call('tk_popup',self._w,x,y,entry)
 def activate(self,index):self.tk.call(self._w,'activate',index)
 def add(self,itemType,cnf={},**kw):self.tk.call((self._w,'add',itemType)+self._options(cnf,kw))
 def add_cascade(self,cnf={},**kw):self.add('cascade',cnf or kw)
 def add_checkbutton(self,cnf={},**kw):self.add('checkbutton',cnf or kw)
 def add_command(self,cnf={},**kw):self.add('command',cnf or kw)
 def add_radiobutton(self,cnf={},**kw):self.add('radiobutton',cnf or kw)
 def add_separator(self,cnf={},**kw):self.add('separator',cnf or kw)
 def insert(self,index,itemType,cnf={},**kw):self.tk.call((self._w,'insert',index,itemType)+self._options(cnf,kw))
 def insert_cascade(self,index,cnf={},**kw):self.insert(index,'cascade',cnf or kw)
 def insert_checkbutton(self,index,cnf={},**kw):self.insert(index,'checkbutton',cnf or kw)
 def insert_command(self,index,cnf={},**kw):self.insert(index,'command',cnf or kw)
 def insert_radiobutton(self,index,cnf={},**kw):self.insert(index,'radiobutton',cnf or kw)
 def insert_separator(self,index,cnf={},**kw):self.insert(index,'separator',cnf or kw)
 def delete(self,index1,index2=None):
  if index2==None:index2=index1
  num_index1,num_index2=self.index(index1),self.index(index2)
  if (num_index1==None) or (num_index2==None):num_index1,num_index2=0,-1
  for i in range(num_index1,num_index2+1):
   if 'command' in self.entryconfig(i):
    c=str(self.entrycget(i,'command'))
    if c:self.deletecommand(c)
  self.tk.call(self._w,'delete',index1,index2)
 def entrycget(self,index,option):return self.tk.call(self._w,'entrycget',index,'-'+option)
 def entryconfigure(self,index,cnf=None,**kw):return self._configure(('entryconfigure',index),cnf,kw)
 entryconfig=entryconfigure
 def index(self,index):
  i=self.tk.call(self._w,'index',index)
  return None if i in('','none')else self.tk.getint(i)
 def invoke(self,index):return self.tk.call(self._w,'invoke',index)
 def post(self,x,y):self.tk.call(self._w,'post',x,y)
 def type(self,index):return self.tk.call(self._w,'type',index)
 def unpost(self):self.tk.call(self._w,'unpost')
 def xposition(self,index):return self.tk.getint(self.tk.call(self._w,'xposition',index))
 def yposition(self,index):return self.tk.getint(self.tk.call(self._w,'yposition',index))
class Menubutton(Widget):
 def __init__(self,master=None,cnf={},**kw):Widget.__init__(self,master,'menubutton',cnf,kw)
class Message(Widget):
 def __init__(self,master=None,cnf={},**kw):Widget.__init__(self,master,'message',cnf,kw)
class Radiobutton(Widget):
 def __init__(self,master=None,cnf={},**kw):Widget.__init__(self,master,'radiobutton',cnf,kw)
 def deselect(self):self.tk.call(self._w,'deselect')
 def flash(self):self.tk.call(self._w,'flash')
 def invoke(self):return self.tk.call(self._w,'invoke')
 def select(self):self.tk.call(self._w,'select')
class Scale(Widget):
 def __init__(self,master=None,cnf={},**kw):Widget.__init__(self,master,'scale',cnf,kw)
 def get(self):
  value=self.tk.call(self._w,'get')
  try:return self.tk.getint(value)
  except (ValueError,TypeError,TclError):return self.tk.getdouble(value)
 def set(self,value):self.tk.call(self._w,'set',value)
 def coords(self,value=None):return self._getints(self.tk.call(self._w,'coords',value))
 def identify(self,x,y):return self.tk.call(self._w,'identify',x,y)
class Scrollbar(Widget):
 def __init__(self,master=None,cnf={},**kw):Widget.__init__(self,master,'scrollbar',cnf,kw)
 def activate(self,index=None):return self.tk.call(self._w,'activate',index) or None
 def delta(self,deltax,deltay):return self.tk.getdouble(self.tk.call(self._w,'delta',deltax,deltay))
 def fraction(self,x,y):return self.tk.getdouble(self.tk.call(self._w,'fraction',x,y))
 def identify(self,x,y):return self.tk.call(self._w,'identify',x,y)
 def get(self):return self._getdoubles(self.tk.call(self._w,'get'))
 def set(self,first,last):self.tk.call(self._w,'set',first,last)
class Text(Widget,XView,YView):
 def __init__(self,master=None,cnf={},**kw):Widget.__init__(self,master,'text',cnf,kw)
 def bbox(self,index):return self._getints(self.tk.call(self._w,'bbox',index)) or None
 def compare(self,index1,op,index2):return self.tk.getboolean(self.tk.call(self._w,'compare',index1,op,index2))
 def count(self,index1,index2,*options,return_ints=False):
  options=['-%s'%arg for arg in options]
  res=self.tk.call(self._w,'count',*options,index1,index2)
  if not isinstance(res,int):
   res=self._getints(res)
   if len(res)==1:res,=res
  if not return_ints:
   if not res:res=None
   elif len(options)<=1:res=(res,)
  return res
 def debug(self,boolean=None):
  if boolean==None:return self.tk.getboolean(self.tk.call(self._w,'debug'))
  self.tk.call(self._w,'debug',boolean)
 def delete(self,index1,index2=None):self.tk.call(self._w,'delete',index1,index2)
 def dlineinfo(self,index):return self._getints(self.tk.call(self._w,'dlineinfo',index))
 def dump(self,index1,index2=None,command=None,**kw):
  args=[]
  func_name=None
  result=None
  if not command:
   result=[]
   def append_triple(key,value,index,result=result):result.append((key,value,index))
   command=append_triple
  try:
   if not isinstance(command,str):func_name=command=self._register(command)
   args+=["-command",command]
   for key in kw:
    if kw[key]:args.append("-"+key)
   args.append(index1)
   if index2:args.append(index2)
   self.tk.call(self._w,"dump",*args)
   return result
  finally:
   if func_name:self.deletecommand(func_name)
 def edit(self,*args):return self.tk.call(self._w,'edit',*args)
 def edit_modified(self,arg=None):return self.edit("modified",arg)
 def edit_redo(self):return self.edit("redo")
 def edit_reset(self):return self.edit("reset")
 def edit_separator(self):return self.edit("separator")
 def edit_undo(self):return self.edit("undo")
 def get(self,index1,index2=None):return self.tk.call(self._w,'get',index1,index2)
 def image_cget(self,index,option):
  if option[:1]!="-":option="-"+option
  if option[-1:]=="_":option=option[:-1]
  return self.tk.call(self._w,"image","cget",index,option)
 def image_configure(self,index,cnf=None,**kw):return self._configure(('image','configure',index),cnf,kw)
 def image_create(self,index,cnf={},**kw):return self.tk.call(self._w,"image","create",index,*self._options(cnf,kw))
 def image_names(self):return self.tk.call(self._w,"image","names")
 def index(self,index):return str(self.tk.call(self._w,'index',index))
 def insert(self,index,chars,*args):self.tk.call((self._w,'insert',index,chars)+args)
 def mark_gravity(self,markName,direction=None):return self.tk.call((self._w,'mark','gravity',markName,direction))
 def mark_names(self):return self.tk.splitlist(self.tk.call(self._w,'mark','names'))
 def mark_set(self,markName,index):self.tk.call(self._w,'mark','set',markName,index)
 def mark_unset(self,*markNames):self.tk.call((self._w,'mark','unset')+markNames)
 def mark_next(self,index):return self.tk.call(self._w,'mark','next',index) or None
 def mark_previous(self,index):return self.tk.call(self._w,'mark','previous',index) or None
 def peer_create(self,newPathName,cnf={},**kw):self.tk.call(self._w,'peer','create',newPathName,*self._options(cnf,kw))
 def peer_names(self):return self.tk.splitlist(self.tk.call(self._w,'peer','names'))
 def replace(self,index1,index2,chars,*args):self.tk.call(self._w,'replace',index1,index2,chars,*args)
 def scan_mark(self,x,y):self.tk.call(self._w,'scan','mark',x,y)
 def scan_dragto(self,x,y):self.tk.call(self._w,'scan','dragto',x,y)
 def search(self,pattern,index,stopindex=None,forwards=None,backwards=None,exact=None,regexp=None,nocase=None,count=None,elide=None):
  args=[self._w,'search']
  if forwards:args.append('-forwards')
  if backwards:args.append('-backwards')
  if exact:args.append('-exact')
  if regexp:args.append('-regexp')
  if nocase:args.append('-nocase')
  if elide:args.append('-elide')
  if count:args.append('-count'); args.append(count)
  if pattern and pattern[0]=='-':args.append('--')
  args.append(pattern)
  args.append(index)
  if stopindex:args.append(stopindex)
  return str(self.tk.call(tuple(args)))
 def see(self,index):self.tk.call(self._w,'see',index)
 def tag_add(self,tagName,index1,*args):self.tk.call((self._w,'tag','add',tagName,index1)+args)
 def tag_unbind(self,tagName,sequence,funcid=None):return self._unbind((self._w,'tag','bind',tagName,sequence),funcid)
 def tag_bind(self,tagName,sequence,func,add=None):return self._bind((self._w,'tag','bind',tagName),sequence,func,add)
 def _tag_bind(self,tagName,sequence=None,func=None,add=None):return self._bind((self._w,'tag','bind',tagName),sequence,func,add)
 def tag_cget(self,tagName,option):
  if option[:1]!='-':option='-'+option
  if option[-1:]=='_':option=option[:-1]
  return self.tk.call(self._w,'tag','cget',tagName,option)
 def tag_configure(self,tagName,cnf=None,**kw):return self._configure(('tag','configure',tagName),cnf,kw)
 tag_config=tag_configure
 def tag_delete(self,*tagNames):self.tk.call((self._w,'tag','delete')+tagNames)
 def tag_lower(self,tagName,belowThis=None):self.tk.call(self._w,'tag','lower',tagName,belowThis)
 def tag_names(self,index=None):return self.tk.splitlist(self.tk.call(self._w,'tag','names',index))
 def tag_nextrange(self,tagName,index1,index2=None):return self.tk.splitlist(self.tk.call(self._w,'tag','nextrange',tagName,index1,index2))
 def tag_prevrange(self,tagName,index1,index2=None):return self.tk.splitlist(self.tk.call(self._w,'tag','prevrange',tagName,index1,index2))
 def tag_raise(self,tagName,aboveThis=None):self.tk.call(self._w,'tag','raise',tagName,aboveThis)
 def tag_ranges(self,tagName):return self.tk.splitlist(self.tk.call(self._w,'tag','ranges',tagName))
 def tag_remove(self,tagName,index1,index2=None):self.tk.call(self._w,'tag','remove',tagName,index1,index2)
 def window_cget(self,index,option):
  if option[:1]!='-':option='-'+option
  if option[-1:]=='_':option=option[:-1]
  return self.tk.call(self._w,'window','cget',index,option)
 def window_configure(self,index,cnf=None,**kw):return self._configure(('window','configure',index),cnf,kw)
 window_config=window_configure
 def window_create(self,index,cnf={},**kw):self.tk.call((self._w,'window','create',index)+self._options(cnf,kw))
 def window_names(self):return self.tk.splitlist(self.tk.call(self._w,'window','names'))
 def yview_pickplace(self,*what):self.tk.call((self._w,'yview','-pickplace')+what)
class _setit:
 def __init__(self,var,value,callback=None):
  self.__value=value
  self.__var=var
  self.__callback=callback
 def __call__(self,*args):
  self.__var.set(self.__value)
  if self.__callback!=None:self.__callback(self.__value,*args)
class OptionMenu(Menubutton):
 def __init__(self,master,variable,value,*values,**kwargs):
  kw={"borderwidth":2,"textvariable":variable,"indicatoron":1,"relief":RAISED,"anchor":"c","highlightthickness":2,"name":kwargs.pop("name",None)}
  Widget.__init__(self,master,"menubutton",kw)
  self.widgetName='tk_optionMenu'
  menu=self.__menu=Menu(self,name="menu",tearoff=0)
  self.menuname=menu._w
  callback=kwargs.get('command')
  if 'command' in kwargs:del kwargs['command']
  if kwargs:raise TclError('unknown option -'+next(iter(kwargs)))
  menu.add_command(label=value,command=_setit(variable,value,callback))
  for v in values:menu.add_command(label=v,command=_setit(variable,v,callback))
  self["menu"]=menu
 def __getitem__(self,name):
  if name=='menu':return self.__menu
  return Widget.__getitem__(self,name)
 def destroy(self):
  Menubutton.destroy(self)
  self.__menu=None
class Image:
 _last_id=0
 def __init__(self,imgtype,name=None,cnf={},master=None,**kw):
  self.name=None
  if master==None:master=_get_default_root('create image')
  self.tk=getattr(master,'tk',master)
  if not name:
   Image._last_id+=1
   name="pyimage%r"%(Image._last_id,)
  if kw and cnf:cnf=_cnfmerge((cnf,kw))
  elif kw:cnf=kw
  options=()
  for k,v in cnf.items():options=options+('-'+k,v)
  self.tk.call(('image','create',imgtype,name,)+options)
  self.name=name
 def __str__(self):return self.name
 def __del__(self):
  if self.name:
   try:self.tk.call('image','delete',self.name)
   except:pass
 def __setitem__(self,key,value):self.tk.call(self.name,'configure','-'+key,value)
 def __getitem__(self,key):return self.tk.call(self.name,'configure','-'+key)
 def configure(self,**kw):
  res=()
  for k,v in _cnfmerge(kw).items():
   if v!=None:
    if k[-1]=='_':k=k[:-1]
    res=res+('-'+k,v)
  self.tk.call((self.name,'config')+res)
 config=configure
 def height(self):return self.tk.getint(self.tk.call('image','height',self.name))
 def type(self):return self.tk.call('image','type',self.name)
 def width(self):return self.tk.getint(self.tk.call('image','width',self.name))
class PhotoImage(Image):
 def __init__(self,name=None,cnf={},master=None,**kw):Image.__init__(self,'photo',name,cnf,master,**kw)
 def blank(self):self.tk.call(self.name,'blank')
 def cget(self,option):return self.tk.call(self.name,'cget','-'+option)
 def __getitem__(self,key):return self.tk.call(self.name,'cget','-'+key)
 def copy(self,*,from_coords=None,zoom=None,subsample=None):
  destImage=PhotoImage(master=self.tk)
  destImage.copy_replace(self,from_coords=from_coords,zoom=zoom,subsample=subsample)
  return destImage
 def zoom(self,x,y='',*,from_coords=None):
  if y=='':y=x
  return self.copy(zoom=(x,y),from_coords=from_coords)
 def subsample(self,x,y='',*,from_coords=None):
  if y=='':y=x
  return self.copy(subsample=(x,y),from_coords=from_coords)
 def copy_replace(self,sourceImage,*,from_coords=None,to=None,shrink=False,zoom=None,subsample=None,compositingrule=None):
  options=[]
  if from_coords!=None:options.extend(('-from',*from_coords))
  if to!=None:options.extend(('-to',*to))
  if shrink:options.append('-shrink')
  if zoom!=None:
   if not isinstance(zoom,(tuple,list)):zoom=(zoom,)
   options.extend(('-zoom',*zoom))
  if subsample!=None:
   if not isinstance(subsample,(tuple,list)):subsample=(subsample,)
   options.extend(('-subsample',*subsample))
  if compositingrule:options.extend(('-compositingrule',compositingrule))
  self.tk.call(self.name,'copy',sourceImage,*options)
 def get(self,x,y):return self.tk.call(self.name,'get',x,y)
 def put(self,data,to=None):
  args=(self.name,'put',data)
  if to:
   if to[0]=='-to':to=to[1:]
   args=args+('-to',)+tuple(to)
  self.tk.call(args)
 def read(self,filename,format=None,*,from_coords=None,to=None,shrink=False):
  options=()
  if format!=None:options+=('-format',format)
  if from_coords!=None:options+=('-from',*from_coords)
  if shrink:options+=('-shrink',)
  if to!=None:options+=('-to',*to)
  self.tk.call(self.name,'read',filename,*options)
 def write(self,filename,format=None,from_coords=None,*,background=None,grayscale=False):
  options=()
  if format!=None:options+=('-format',format)
  if from_coords!=None:options+=('-from',*from_coords)
  if grayscale:options+=('-grayscale',)
  if background!=None:options+=('-background',background)
  self.tk.call(self.name,'write',filename,*options)
 def data(self,format=None,*,from_coords=None,background=None,grayscale=False):
  options=()
  if format!=None:options+=('-format',format)
  if from_coords!=None:options+=('-from',*from_coords)
  if grayscale:options+=('-grayscale',)
  if background!=None:options+=('-background',background)
  data=self.tk.call(self.name,'data',*options)
  if isinstance(data,str):data=self.tk.splitlist(data) if format==None else bytes(data,'latin1')
  return data
 def transparency_get(self,x,y):return self.tk.getboolean(self.tk.call(self.name,'transparency','get',x,y))
 def transparency_set(self,x,y,boolean):self.tk.call(self.name,'transparency','set',x,y,boolean)
class BitmapImage(Image):
 def __init__(self,name=None,cnf={},master=None,**kw):Image.__init__(self,'bitmap',name,cnf,master,**kw)
def image_names():
 tk=_get_default_root('use image_names()').tk
 return tk.splitlist(tk.call('image','names'))
def image_types():
 tk=_get_default_root('use image_types()').tk
 return tk.splitlist(tk.call('image','types'))
class Spinbox(Widget,XView):
 def __init__(self,master=None,cnf={},**kw):Widget.__init__(self,master,'spinbox',cnf,kw)
 def bbox(self,index):return self._getints(self.tk.call(self._w,'bbox',index)) or None
 def delete(self,first,last=None):return self.tk.call(self._w,'delete',first,last)
 def get(self):return self.tk.call(self._w,'get')
 def icursor(self,index):return self.tk.call(self._w,'icursor',index)
 def identify(self,x,y):return self.tk.call(self._w,'identify',x,y)
 def index(self,index):return self.tk.call(self._w,'index',index)
 def insert(self,index,s):return self.tk.call(self._w,'insert',index,s)
 def invoke(self,element):return self.tk.call(self._w,'invoke',element)
 def scan(self,*args):return self._getints(self.tk.call((self._w,'scan')+args)) or ()
 def scan_mark(self,x):return self.scan("mark",x)
 def scan_dragto(self,x):return self.scan("dragto",x)
 def selection(self,*args):return self._getints(self.tk.call((self._w,'selection')+args)) or ()
 def selection_adjust(self,index):return self.selection("adjust",index)
 def selection_clear(self):return self.selection("clear")
 def selection_element(self,element=None):return self.tk.call(self._w,'selection','element',element)
 def selection_from(self,index):self.selection('from',index)
 def selection_present(self):return self.tk.getboolean(self.tk.call(self._w,'selection','present'))
 def selection_range(self,start,end):self.selection('range',start,end)
 def selection_to(self,index):self.selection('to',index)
class LabelFrame(Widget):
 def __init__(self,master=None,cnf={},**kw):Widget.__init__(self,master,'labelframe',cnf,kw)
class PanedWindow(Widget):
 def __init__(self,master=None,cnf={},**kw):Widget.__init__(self,master,'panedwindow',cnf,kw)
 def add(self,child,**kw):self.tk.call((self._w,'add',child)+self._options(kw))
 def remove(self,child):self.tk.call(self._w,'forget',child)
 forget=remove
 def identify(self,x,y):return self.tk.call(self._w,'identify',x,y)
 def proxy(self,*args):return self._getints(self.tk.call((self._w,'proxy')+args)) or ()
 def proxy_coord(self):return self.proxy("coord")
 def proxy_forget(self):return self.proxy("forget")
 def proxy_place(self,x,y):return self.proxy("place",x,y)
 def sash(self,*args):return self._getints(self.tk.call((self._w,'sash')+args)) or ()
 def sash_coord(self,index):return self.sash("coord",index)
 def sash_mark(self,index):return self.sash("mark",index)
 def sash_place(self,index,x,y):return self.sash("place",index,x,y)
 def panecget(self,child,option):return self.tk.call((self._w,'panecget')+(child,'-'+option))
 def paneconfigure(self,tagOrId,cnf=None,**kw):
  if cnf==None and not kw:return self._getconfigure(self._w,'paneconfigure',tagOrId)
  if isinstance(cnf,str) and not kw:return self._getconfigure1(self._w,'paneconfigure',tagOrId,'-'+cnf)
  self.tk.call((self._w,'paneconfigure',tagOrId)+self._options(cnf,kw))
 paneconfig=paneconfigure
 def panes(self):return self.tk.splitlist(self.tk.call(self._w,'panes'))