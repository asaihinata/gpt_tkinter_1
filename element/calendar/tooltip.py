from sys import platform
import tkinter as tk
from tkinter import ttk
class Tooltip(tk.Toplevel):
 _initialized=False
 def __init__(self,parent,**kwargs):
  tk.Toplevel.__init__(self,parent,padx=0,pady=0)
  self.transient(parent)
  self.overrideredirect(True)
  self.update_idletasks()
  self.attributes('-alpha',kwargs.pop('alpha',0.8))
  if platform=='linux':self.attributes('-type','tooltip')
  if not Tooltip._initialized:
   style=ttk.Style(self)
   style.configure('tooltip.TLabel',foreground='gray90',background='black',font='TkDefaultFont 9 bold')
   Tooltip._initialized=True
  kw={'compound': 'left','style': 'tooltip.TLabel','padding': 4}
  kw.update(kwargs)
  self.label=ttk.Label(self,**kw)
  self.label.pack(fill='both')
  self.config=self.configure
 def __setitem__(self,key,value):self.configure(**{key: value})
 def __getitem__(self,key):return self.cget(key)
 def cget(self,key):return self.attributes('-alpha') if key=='alpha' else self.label.cget(key)
 def configure(self,**kwargs):
  if 'alpha' in kwargs:self.attributes('-alpha',kwargs.pop('alpha'))
  self.label.configure(**kwargs)
 def keys(self):
  keys=list(self.label.keys())
  keys.insert(0,'alpha')
  return keys
class TooltipWrapper:
 def __init__(self,master,**kwargs):
  self.widgets={}
  self.bind_enter_ids={}
  self.bind_leave_ids={}
  self._delay=2000
  self._timer_id=None
  self.tooltip=Tooltip(master)
  self.tooltip.withdraw()
  self.current_widget=None
  self.configure(**kwargs)
  self.config=self.configure
  self.tooltip.bind('<Leave>',self._on_leave_tooltip)
 def __setitem__(self,key,value):self.configure(**{key: value})
 def __getitem__(self,key):return self.cget(key)
 def cget(self,key):
  if key=='delay':return self._delay
  else:return self.tooltip.cget(key)
 def configure(self,**kwargs):
  try:self._delay=int(kwargs.pop('delay',self._delay))
  except ValueError:raise ValueError('expected integer for the delay option.')
  self.tooltip.configure(**kwargs)
 def add_tooltip(self,widget,text):
  self.widgets[str(widget)]=text
  self.bind_enter_ids[str(widget)]=widget.bind('<Enter>',self._on_enter)
  self.bind_leave_ids[str(widget)]=widget.bind('<Leave>',self._on_leave)
 def set_tooltip_text(self,widget,text):self.widgets[str(widget)]=text
 def remove_all(self):
  for name in self.widgets:
   widget=self.tooltip.nametowidget(name)
   widget.unbind('<Enter>',self.bind_enter_ids[name])
   widget.unbind('<Leave>',self.bind_leave_ids[name])
  self.widgets.clear()
  self.bind_enter_ids.clear()
  self.bind_leave_ids.clear()
 def remove_tooltip(self,widget):
  try:
   name=str(widget)
   del self.widgets[name]
   widget.unbind('<Enter>',self.bind_enter_ids[name])
   widget.unbind('<Leave>',self.bind_leave_ids[name])
   del self.bind_enter_ids[name]
   del self.bind_leave_ids[name]
  except KeyError:pass
 def _on_enter(self,event):
  if not self.tooltip.winfo_ismapped():
   self._timer_id=event.widget.after(self._delay,self.display_tooltip)
   self.current_widget=event.widget
 def _on_leave(self,event):
  if self.tooltip.winfo_ismapped():
   x,y=event.widget.winfo_pointerxy()
   if not event.widget.winfo_containing(x,y) in [event.widget,self.tooltip]:self.tooltip.withdraw()
  else:
   try:event.widget.after_cancel(self._timer_id)
   except ValueError:pass
  self.current_widget=None
 def _on_leave_tooltip(self,event):
  x,y=event.widget.winfo_pointerxy()
  if not event.widget.winfo_containing(x,y) in [self.current_widget,self.tooltip]:self.tooltip.withdraw()
 def display_tooltip(self):
  if self.current_widget==None:return
  try:disabled="disabled" in self.current_widget.state()
  except AttributeError:disabled=self.current_widget.cget('state')=="disabled"
  if not disabled:
   self.tooltip['text']=self.widgets[str(self.current_widget)]
   self.tooltip.deiconify()
   x=self.current_widget.winfo_pointerx()+14
   y=self.current_widget.winfo_rooty()+self.current_widget.winfo_height()+2
   self.tooltip.geometry('+%i+%i'%(x,y))