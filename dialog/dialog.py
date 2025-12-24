from tkr.tkme import _get_temp_root,_destroy_temp_root,_cnfmerge,TclError,Widget,Button,Pack
class Dialog:
 command=None
 def __init__(self,master=None,**options):
  if master==None:master=options.get('parent')
  self.master=master
  self.options=options
 def _fixoptions(self):pass
 def _fixresult(self,widget,result):return result
 def show(self,**options):
  for k,v in options.items():self.options[k]=v
  self._fixoptions()
  master=self.master
  if master==None:master=_get_temp_root()
  try:
   self._test_callback(master)
   s=master.tk.call(self.command,*master._options(self.options))
   s=self._fixresult(master,s)
  finally:_destroy_temp_root(master)
  return s
 def _test_callback(self,master):pass
DIALOG_ICON='questhead'
class Dialogs(Widget):
 def __init__(self,master=None,cnf={},**kw):
  cnf=_cnfmerge((cnf,kw))
  self.widgetName='__dialog__'
  self._setup(master,cnf)
  self.num=self.tk.getint(self.tk.call('tk_dialog',self._w,cnf['title'],cnf['text'],cnf['bitmap'],cnf['default'],*cnf['strings']))
  try:Widget.destroy(self)
  except TclError:pass
 def destroy(self):pass