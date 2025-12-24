import tkinter as tk,calendar,re
from sys import platform
from tkinter import ttk
from font.font import fonts
from babel import default_locale
from babel.dates import format_date,parse_date,get_day_names,get_month_names,get_date_format
from .tooltip import TooltipWrapper
MAPS={'winnative':{'focusfill':[('readonly','focus','SystemHighlight')],
'foreground':[('disabled','SystemGrayText'),
('readonly','focus','SystemHighlightText')],
'selectforeground':[('!focus','SystemWindowText')],
'fieldbackground':[('readonly','SystemButtonFace'),
('disabled','SystemButtonFace')],
'selectbackground':[('!focus','SystemWindow')]},
'clam':{'foreground':[('readonly','focus','#ffffff')],
'fieldbackground':[('readonly','focus','#4a6984'),('readonly','#dcdad5')],
'background':[('active','#eeebe7'),('pressed','#eeebe7')],
'arrowcolor':[('disabled','#999999')]},
'alt':{'fieldbackground':[('readonly','#d9d9d9'),
('disabled','#d9d9d9')],
'arrowcolor':[('disabled','#a3a3a3')]},
'default':{'fieldbackground':[('readonly','#d9d9d9'),('disabled','#d9d9d9')],
'arrowcolor':[('disabled','#a3a3a3')]},
'classic':{'fieldbackground':[('readonly','#d9d9d9'),('disabled','#d9d9d9')]},
'vista':{'focusfill':[('readonly','focus','SystemHighlight')],
'foreground':[('disabled','SystemGrayText'),
('readonly','focus','SystemHighlightText')],
'selectforeground':[('!focus','SystemWindowText')],
'selectbackground':[('!focus','SystemWindow')]},
'xpnative':{'focusfill':[('readonly','focus','SystemHighlight')],
'foreground':[('disabled','SystemGrayText'),
('readonly','focus','SystemHighlightText')],
'selectforeground':[('!focus','SystemWindowText')],
'selectbackground':[('!focus','SystemWindow')]}}
class DateEntry(ttk.Entry):
 entry_kw={'exportselection':1,'invalidcommand':'','justify':'left','show':'','cursor':'xterm','style':'','state':'normal','takefocus':'ttk::takefocus','textvariable':'','validate':'none','validatecommand':'','width':12,'xscrollcommand':''}
 def __init__(self,master=None,**kw):
  kw['selectmode']='day'
  entry_kw={}
  style=kw.pop('style','DateEntry')
  for key in self.entry_kw:entry_kw[key]=kw.pop(key,self.entry_kw[key])
  entry_kw['font']=kw.get('font',None)
  self._cursor=entry_kw['cursor']
  kw['cursor']=kw.pop('calendar_cursor',None)
  ttk.Entry.__init__(self,master,**entry_kw)
  self._determine_downarrow_name_after_id=''
  self._top_cal=tk.Toplevel(self)
  self._top_cal.withdraw()
  if platform=="linux":self._top_cal.attributes('-type','DROPDOWN_MENU')
  self._top_cal.overrideredirect(True)
  self._calendar=Calendar(self._top_cal,**kw)
  self._calendar.pack()
  self.format_date=self._calendar.format_date
  self.parse_date=self._calendar.parse_date
  self._theme_name=''
  self.style=ttk.Style(self)
  self._setup_style()
  self.configure(style=style)
  validatecmd=self.register(self._validate_date)
  self.configure(validate='focusout',validatecommand=validatecmd)
  self._date=self._calendar.selection_get()
  if self._date==None:
   today=self._calendar.date.today()
   year=kw.get('year',today.year)
   month=kw.get('month',today.month)
   day=kw.get('day',today.day)
   try:self._date=self._calendar.date(year,month,day)
   except ValueError:self._date=today
  self._set_text(self.format_date(self._date))
  self.bind('<<ThemeChanged>>',lambda e:self.after(10,self._on_theme_change))
  self.bind('<Configure>',self._determine_downarrow_name)
  self.bind('<Map>',self._determine_downarrow_name)
  self.bind('<Leave>',lambda e:self.state(['!active']))
  self.bind('<Motion>',self._on_motion)
  self.bind('<ButtonPress-1>',self._on_b1_press)
  self._calendar.bind('<<CalendarSelected>>',self._select)
  self._calendar.bind('<FocusOut>',self._on_focus_out_cal)
 def __getitem__(self,key):return self.cget(key)
 def __setitem__(self,key,value):self.configure(**{key:value})
 def _setup_style(self,event=None):
  self.style.layout('DateEntry',self.style.layout('TCombobox'))
  self.update_idletasks()
  conf=self.style.configure('TCombobox')
  if conf:self.style.configure('DateEntry',**conf)
  maps=self.style.map('TCombobox')
  if maps:
   try:self.style.map('DateEntry',**maps)
   except tk.TclError:
    maps=MAPS.get(self.style.theme_use(),MAPS['default'])
    self.style.map('DateEntry',**maps)
  try:self.after_cancel(self._determine_downarrow_name_after_id)
  except:pass
  self._determine_downarrow_name_after_id=self.after(10,self._determine_downarrow_name)
 def _determine_downarrow_name(self,event=None):
  try:self.after_cancel(self._determine_downarrow_name_after_id)
  except:pass
  if self.winfo_ismapped():
   self.update_idletasks()
   y=self.winfo_height()//2
   x=self.winfo_width()-10
   name=self.identify(x,y)
   if name:self._downarrow_name=name
   else:self._determine_downarrow_name_after_id=self.after(10,self._determine_downarrow_name)
 def _on_motion(self,event):
  x,y=event.x,event.y
  if 'disabled' not in self.state():
   if self.identify(x,y)==self._downarrow_name:
    self.state(['active'])
    ttk.Entry.configure(self,cursor='arrow')
   else:
    self.state(['!active'])
    ttk.Entry.configure(self,cursor=self._cursor)
 def _on_theme_change(self):
  theme=self.style.theme_use()
  if self._theme_name!=theme:
   self._theme_name=theme
   self._setup_style()
 def _on_b1_press(self,event):
  x,y=event.x,event.y
  if (('disabled' not in self.state()) and self.identify(x,y)==self._downarrow_name):
   self.state(['pressed'])
   self.drop_down()
 def _on_focus_out_cal(self,event):
  if self.focus_get()!=None:
   if self.focus_get()==self:
    x,y=event.x,event.y
    if (type(x)!=int or type(y)!=int or self.identify(x,y)!=self._downarrow_name):
     self._top_cal.withdraw()
     self.state(['!pressed'])
   else:
    self._top_cal.withdraw()
    self.state(['!pressed'])
  elif self.grab_current():
   x,y=self._top_cal.winfo_pointerxy()
   xc=self._top_cal.winfo_rootx()
   yc=self._top_cal.winfo_rooty()
   w=self._top_cal.winfo_width()
   h=self._top_cal.winfo_height()
   if xc<=x<=xc+w and yc<=y<=yc+h:self._calendar.focus_force()
   else:
    self._top_cal.withdraw()
    self.state(['!pressed'])
  else:
   if 'active' in self.state():self._calendar.focus_force()
   else:
    self._top_cal.withdraw()
    self.state(['!pressed'])
 def _validate_date(self):
  try:
   date=self.parse_date(self.get())
   self._date=self._calendar.check_date_range(date)
   if self._date!=date:
    self._set_text(self.format_date(self._date))
    return False
   else:return True
  except (ValueError,IndexError):
   self._set_text(self.format_date(self._date))
   return False
 def _select(self,event=None):
  date=self._calendar.selection_get()
  if date!=None:
   self._set_text(self.format_date(date))
   self._date=date
   self.event_generate('<<DateEntrySelected>>')
  self._top_cal.withdraw()
  if 'readonly' not in self.state():self.focus_set()
 def _set_text(self,txt):
  if 'readonly' in self.state():
   readonly=True
   self.state(('!readonly',))
  else:readonly=False
  self.delete(0,'end')
  self.insert(0,txt)
  if readonly:self.state(('readonly',))
 def destroy(self):
  try:self.after_cancel(self._determine_downarrow_name_after_id)
  except:pass
  ttk.Entry.destroy(self)
 def drop_down(self):
  if self._calendar.winfo_ismapped():self._top_cal.withdraw()
  else:
   self._validate_date()
   date=self.parse_date(self.get())
   x=self.winfo_rootx()
   y=self.winfo_rooty()+self.winfo_height()
   if self.winfo_toplevel().attributes('-topmost'):self._top_cal.attributes('-topmost',True)
   else:self._top_cal.attributes('-topmost',False)
   self._top_cal.geometry('+%i+%i'%(x,y))
   self._top_cal.deiconify()
   self._calendar.focus_set()
   self._calendar.selection_set(date)
 def state(self,*args):
  if args:
   states=args[0]
   if 'disabled' in states or 'readonly' in states:self.configure(cursor='arrow')
   elif '!disabled' in states or '!readonly' in states:self.configure(cursor='xterm')
  return ttk.Entry.state(self,*args)
 def keys(self):
  keys=list(self.entry_kw)
  keys.extend(self._calendar.keys())
  keys.append('calendar_cursor')
  return list(set(keys))
 def cget(self,key):
  if key in self.entry_kw:return ttk.Entry.cget(self,key)
  elif key=='calendar_cursor':return self._calendar.cget('cursor')
  else:return self._calendar.cget(key)
 def configure(self,cnf={},**kw):
  if not isinstance(cnf,dict):raise TypeError("Expected a dictionary or keyword arguments.")
  kwargs=cnf.copy()
  kwargs.update(kw)
  entry_kw={}
  keys=list(kwargs.keys())
  for key in keys:
   if key in self.entry_kw:entry_kw[key]=kwargs.pop(key)
  font=kwargs.get('font',None)
  if font!=None:entry_kw['font']=font
  self._cursor=str(entry_kw.get('cursor',self._cursor))
  if entry_kw.get('state')=='readonly' and self._cursor=='xterm' and 'cursor' not in entry_kw:
   entry_kw['cursor']='arrow'
   self._cursor='arrow'
  ttk.Entry.configure(self,entry_kw)
  kwargs['cursor']=kwargs.pop('calendar_cursor',None)
  self._calendar.configure(kwargs)
  if 'date_pattern' in kwargs or 'locale' in kwargs:self._set_text(self.format_date(self._date))
 config=configure
 def set_date(self,date):
  try:txt=self.format_date(date)
  except AssertionError:
   txt=str(date)
   try:self.parse_date(txt)
   except Exception:raise ValueError("%r!=a valid date."%date)
  self._set_text(txt)
  self._validate_date()
 def get_date(self):
  self._validate_date()
  return self.parse_date(self.get())
class Calendar(ttk.Frame):
 date=calendar.datetime.date
 datetime=calendar.datetime.datetime
 timedelta=calendar.datetime.timedelta
 strptime=calendar.datetime.datetime.strptime
 strftime=calendar.datetime.datetime.strftime
 def __init__(self,master=None,**kw):
  curs=kw.pop("cursor","")
  font=kw.pop("font","Meiryo")
  classname=kw.pop('class_',"Calendar")
  name=kw.pop('name',None)
  ttk.Frame.__init__(self,master,class_=classname,cursor=curs,name=name)
  self._style_prefixe=str(self)
  ttk.Frame.configure(self,style='main.%s.TFrame'%self._style_prefixe)
  self._textvariable=kw.pop("textvariable",None)
  self._font=fonts(self,font)
  prop=self._font.actual()
  prop["size"]+=1
  self._header_font=fonts(self,**prop)
  state=kw.get('state','normal')
  try:bd=int(kw.pop('borderwidth',2))
  except ValueError:raise ValueError("expected integer for the 'borderwidth' option.")
  firstweekday=kw.pop('firstweekday','monday')
  if firstweekday not in ["monday","sunday"]:raise ValueError("'firstweekday' option should be 'monday' or 'sunday'.")
  self._cal=calendar.TextCalendar((firstweekday=='sunday')*6)
  weekenddays=kw.pop("weekenddays",None)
  if not weekenddays:
   l=list(self._cal.iterweekdays())
   weekenddays=[l.index(5)+1,l.index(6)+1]
  self._check_weekenddays(weekenddays)
  locale=kw.pop("locale",default_locale())
  if locale==None:locale='en'
  self._day_names=get_day_names('abbreviated',locale=locale)
  self._month_names=get_month_names('wide',locale=locale)
  date_pattern=self._get_date_pattern(kw.pop("date_pattern","short"),locale)
  today=self.date.today()
  if self._textvariable!=None:
   try:
    self._sel_date=parse_date(self._textvariable.get(),locale)
    month=self._sel_date.month
    year=self._sel_date.year
   except IndexError:
    self._sel_date=None
    self._textvariable.set('')
    month=kw.pop("month",today.month)
    year=kw.pop('year',today.year)
  else:
   if (("month" in kw) or ("year" in kw)) and ("day" not in kw):
    month=kw.pop("month",today.month)
    year=kw.pop('year',today.year)
    self._sel_date=None
   else:
    day=kw.pop('day',today.day)
    month=kw.pop("month",today.month)
    year=kw.pop('year',today.year)
    try:self._sel_date=self.date(year,month,day)
    except ValueError:self._sel_date=None
  self._date=self.date(year,month,1)
  maxdate=kw.pop('maxdate',None)
  mindate=kw.pop('mindate',None)
  if maxdate!=None:
   if isinstance(maxdate,self.datetime):maxdate=maxdate.date()
   elif not isinstance(maxdate,self.date):raise TypeError("expected %s for the 'maxdate' option."%self.date)
  if mindate!=None:
   if isinstance(mindate,self.datetime):mindate=mindate.date()
   elif not isinstance(mindate,self.date):raise TypeError("expected %s for the 'mindate' option."%self.date)
  if (mindate!=None) and (maxdate!=None) and (mindate>maxdate):raise ValueError("mindate should be smaller than maxdate.")
  selectmode=kw.pop("selectmode","day")
  if selectmode not in ("none","day"):raise ValueError("'selectmode' option should be 'none' or 'day'.")
  showweeknumbers=kw.pop('showweeknumbers',True)
  self.style=ttk.Style(self)
  active_bg=self.style.lookup('TEntry','selectbackground',('focus',))
  dis_active_bg=self.style.lookup('TEntry','selectbackground',('disabled',))
  dis_bg=self.style.lookup('TLabel','background',('disabled',))
  dis_fg=self.style.lookup('TLabel','foreground',('disabled',))
  options=['cursor','font','borderwidth','state','selectmode','textvariable','locale','date_pattern','maxdate','mindate','showweeknumbers','showothermonthdays','firstweekday','weekenddays','selectbackground','selectforeground','disabledselectbackground','disabledselectforeground','normalbackground','normalforeground','background','foreground','disabledbackground','disabledforeground','bordercolor','othermonthforeground','othermonthbackground','othermonthweforeground','othermonthwebackground','weekendbackground','weekendforeground','headersbackground','headersforeground','disableddaybackground','disableddayforeground','tooltipforeground','tooltipbackground','tooltipalpha','tooltipdelay']
  keys=list(kw.keys())
  for option in keys:
   if option not in options:del(kw[option])
  self._properties={"cursor":curs,
"font":font,
"borderwidth":bd,
"state":state,
"locale":locale,
"date_pattern":date_pattern,
"selectmode":selectmode,
'textvariable':self._textvariable,
'firstweekday':firstweekday,
'weekenddays':weekenddays,
'mindate':mindate,
'maxdate':maxdate,
'showweeknumbers':showweeknumbers,
'showothermonthdays':kw.pop('showothermonthdays',True),
'selectbackground':active_bg,
'selectforeground':'white',
'disabledselectbackground':dis_active_bg,
'disabledselectforeground':'white',
'normalbackground':'white',
'normalforeground':'black',
'background':'gray30',
'foreground':'white',
'disabledbackground':'gray30',
'disabledforeground':'gray70',
'bordercolor':'gray70',
'othermonthforeground':'gray45',
'othermonthbackground':'gray93',
'othermonthweforeground':'gray45',
'othermonthwebackground':'gray75',
'weekendbackground':'gray80',
'weekendforeground':'gray30',
'headersbackground':'gray70',
'headersforeground':'black',
'disableddaybackground':dis_bg,
'disableddayforeground':dis_fg,
'tooltipforeground':'gray90',
'tooltipbackground':'black',
'tooltipalpha':0.8,
'tooltipdelay':2000}
  self._properties.update(kw)
  self.calevents={}
  self._calevent_dates={}
  self._tags={}
  self.tooltip_wrapper=TooltipWrapper(self,alpha=self._properties['tooltipalpha'],style=self._style_prefixe+'.tooltip.TLabel',delay=self._properties['tooltipdelay'])
  self._header=ttk.Frame(self,style='main.%s.TFrame'%self._style_prefixe)
  f_month=ttk.Frame(self._header,style='main.%s.TFrame'%self._style_prefixe)
  self._l_month=ttk.Button(f_month,style='L.%s.TButton'%self._style_prefixe,command=self._prev_month)
  self._header_month=ttk.Label(f_month,width=10,anchor='center',style='main.%s.TLabel'%self._style_prefixe,font=self._header_font)
  self._r_month=ttk.Button(f_month,style='R.%s.TButton'%self._style_prefixe,command=self._next_month)
  self._l_month.pack(side='left',fill="y")
  self._header_month.pack(side='left',padx=4)
  self._r_month.pack(side='left',fill="y")
  f_year=ttk.Frame(self._header,style='main.%s.TFrame'%self._style_prefixe)
  self._l_year=ttk.Button(f_year,style='L.%s.TButton'%self._style_prefixe,command=self._prev_year)
  self._header_year=ttk.Label(f_year,width=4,anchor='center',style='main.%s.TLabel'%self._style_prefixe,font=self._header_font)
  self._r_year=ttk.Button(f_year,style='R.%s.TButton'%self._style_prefixe,command=self._next_year)
  self._l_year.pack(side='left',fill="y")
  self._header_year.pack(side='left',padx=4)
  self._r_year.pack(side='left',fill="y")
  f_month.pack(side='left',fill='x')
  f_year.pack(side='right')
  self._cal_frame=ttk.Frame(self,style='cal.%s.TFrame'%self._style_prefixe)
  ttk.Label(self._cal_frame,style='headers.%s.TLabel'%self._style_prefixe).grid(row=0,column=0,sticky="eswn")
  self._week_days=[]
  for i,day in enumerate(self._cal.iterweekdays()):
   d=self._day_names[day%7]
   self._cal_frame.columnconfigure(i+1,weight=1)
   self._week_days.append(ttk.Label(self._cal_frame,font=self._font,style='headers.%s.TLabel'%self._style_prefixe,anchor="center",text=d,width=4))
   self._week_days[-1].grid(row=0,column=i+1,sticky="ew",pady=(0,1))
  self._week_nbs=[]
  self._calendar=[]
  for i in range(1,7):
   self._cal_frame.rowconfigure(i,weight=1)
   wlabel=ttk.Label(self._cal_frame,style='headers.%s.TLabel'%self._style_prefixe,font=self._font,padding=2,anchor="e",width=2)
   self._week_nbs.append(wlabel)
   wlabel.grid(row=i,column=0,sticky="esnw",padx=(0,1))
   if not showweeknumbers:
    wlabel.grid_remove()
   self._calendar.append([])
   for j in range(1,8):
    label=ttk.Label(self._cal_frame,style='normal.%s.TLabel'%self._style_prefixe,font=self._font,anchor="center")
    self._calendar[-1].append(label)
    label.grid(row=i,column=j,padx=(0,1),pady=(0,1),sticky="nsew")
    if selectmode=="day":label.bind("<1>",self._on_click)
  self._header.pack(fill="x",padx=2,pady=2)
  self._cal_frame.pack(fill="both",expand=True,padx=bd,pady=bd)
  self.config(state=state)
  self.bind('<<ThemeChanged>>',self._setup_style)
  self._setup_style()
  self._display_calendar()
  self._btns_date_range()
  self._check_sel_date()
  if self._textvariable!=None:
   try:self._textvariable_trace_id=self._textvariable.trace_add('write',self._textvariable_trace)
   except AttributeError:self._textvariable_trace_id=self._textvariable.trace('w',self._textvariable_trace)
 def __getitem__(self,key):
  try:return self._properties[key]
  except KeyError:raise AttributeError("Calendar object has no attribute %s."%key)
 def __setitem__(self,key,value):
  if key not in self._properties:raise AttributeError("Calendar object has no attribute %s."%key)
  elif key=='date_pattern':
   date_pattern=self._get_date_pattern(value)
   self._properties[key]=date_pattern
  else:
   if key=="selectmode":
    if value=="none":
     for week in self._calendar:
      for day in week:day.unbind("<1>")
    elif value=="day":
     for week in self._calendar:
      for day in week:day.bind("<1>",self._on_click)
    else:raise ValueError("'selectmode' option should be 'none' or 'day'.")
   elif key=="locale":
    self._day_names=get_day_names('abbreviated',locale=value)
    self._month_names=get_month_names('wide',locale=value)
    self._properties['date_pattern']=self._get_date_pattern("short",value)
    for i,l in enumerate(self._week_days):l.configure(text=self._day_names[i])
    self._header_month.configure(text=self._month_names[self._date.month].title())
   elif key=='textvariable':
    try:
     if self._textvariable!=None:self._textvariable.trace_remove('write',self._textvariable_trace_id)
     if value!=None:self._textvariable_trace_id=value.trace_add('write',self._textvariable_trace)
    except AttributeError:
     if self._textvariable!=None:self._textvariable.trace_vdelete('w',self._textvariable_trace_id)
     if value!=None:value.trace('w',self._textvariable_trace)
    self._textvariable=value
    value.set(value.get())
   elif key=='showweeknumbers':
    if value:
     for wlabel in self._week_nbs:wlabel.grid()
    else:
     for wlabel in self._week_nbs:wlabel.grid_remove()
   elif key=='firstweekday':
    if value not in ["monday","sunday"]:raise ValueError("'firstweekday' option should be 'monday' or 'sunday'.")
    self._cal.firstweekday=(value=='sunday')*6
    for label,day in zip(self._week_days,self._cal.iterweekdays()):label.configure(text=self._day_names[day%7])
   elif key=='weekenddays':self._check_weekenddays(value)
   elif key=='borderwidth':
    try:
     bd=int(value)
     self._cal_frame.pack_configure(padx=bd,pady=bd)
    except ValueError:raise ValueError('expected integer for the borderwidth option.')
   elif key=='state':
    if value not in ['normal','disabled']:raise ValueError("bad state '%s':must be disabled or normal"%value)
    else:
     state='!'*(value=='normal')+'disabled'
     self.state((state,))
     self._header.state((state,))
     for child in self._header.children.values():child.state((state,))
     self._header_month.state((state,))
     self._header_year.state((state,))
     self._l_year.state((state,))
     self._r_year.state((state,))
     self._l_month.state((state,))
     self._r_month.state((state,))
     for child in self._cal_frame.children.values():child.state((state,))
   elif key=="maxdate":
    if value!=None:
     if isinstance(value,self.datetime):value=value.date()
     elif not isinstance(value,self.date):raise TypeError("expected %s for the 'maxdate' option."%self.date)
     mindate=self['mindate']
     if mindate!=None and mindate>value:
      self._properties['mindate']=value
      self._date=self._date.replace(year=value.year,month=value.month)
     elif self._date>value:self._date=self._date.replace(year=value.year,month=value.month)
    self._r_month.state(['!disabled'])
    self._r_year.state(['!disabled'])
    self._l_month.state(['!disabled'])
    self._l_year.state(['!disabled'])
   elif key=="mindate":
    if value!=None:
     if isinstance(value,self.datetime):value=value.date()
     elif not isinstance(value,self.date):raise TypeError("expected %s for the 'mindate' option."%self.date)
     maxdate=self['maxdate']
     if maxdate!=None and maxdate<value:
      self._properties['maxdate']=value
      self._date=self._date.replace(year=value.year,month=value.month)
     elif self._date<value:self._date=self._date.replace(year=value.year,month=value.month)
    self._r_month.state(['!disabled'])
    self._r_year.state(['!disabled'])
    self._l_month.state(['!disabled'])
    self._l_year.state(['!disabled'])
   elif key=="font":
    font=fonts(self,value)
    prop=font.actual()
    self._font.configure(**prop)
    prop["size"]+=1
    self._header_font.configure(**prop)
    size=max(prop["size"],10)
    self.style.configure('R.%s.TButton'%self._style_prefixe,arrowsize=size)
    self.style.configure('L.%s.TButton'%self._style_prefixe,arrowsize=size)
   elif key=="normalbackground":
    self.style.configure('cal.%s.TFrame'%self._style_prefixe,background=value)
    self.style.configure('normal.%s.TLabel'%self._style_prefixe,background=value)
    self.style.configure('normal_om.%s.TLabel'%self._style_prefixe,background=value)
   elif key=="normalforeground":self.style.configure('normal.%s.TLabel'%self._style_prefixe,foreground=value)
   elif key=="bordercolor":self.style.configure('cal.%s.TFrame'%self._style_prefixe,background=value)
   elif key=="othermonthforeground":self.style.configure('normal_om.%s.TLabel'%self._style_prefixe,foreground=value)
   elif key=="othermonthbackground":self.style.configure('normal_om.%s.TLabel'%self._style_prefixe,background=value)
   elif key=="othermonthweforeground":self.style.configure('we_om.%s.TLabel'%self._style_prefixe,foreground=value)
   elif key=="othermonthwebackground":self.style.configure('we_om.%s.TLabel'%self._style_prefixe,background=value)
   elif key=="selectbackground":self.style.configure('sel.%s.TLabel'%self._style_prefixe,background=value)
   elif key=="selectforeground":self.style.configure('sel.%s.TLabel'%self._style_prefixe,foreground=value)
   elif key=="disabledselectbackground":self.style.map('sel.%s.TLabel'%self._style_prefixe,background=[('disabled',value)])
   elif key=="disabledselectforeground":self.style.map('sel.%s.TLabel'%self._style_prefixe,foreground=[('disabled',value)])
   elif key=="disableddaybackground":self.style.map('%s.TLabel'%self._style_prefixe,background=[('disabled',value)])
   elif key=="disableddayforeground":self.style.map('%s.TLabel'%self._style_prefixe,foreground=[('disabled',value)])
   elif key=="weekendbackground":
    self.style.configure('we.%s.TLabel'%self._style_prefixe,background=value)
    self.style.configure('we_om.%s.TLabel'%self._style_prefixe,background=value)
   elif key=="weekendforeground":self.style.configure('we.%s.TLabel'%self._style_prefixe,foreground=value)
   elif key=="headersbackground":self.style.configure('headers.%s.TLabel'%self._style_prefixe,background=value)
   elif key=="headersforeground":self.style.configure('headers.%s.TLabel'%self._style_prefixe,foreground=value)
   elif key=="background":
    self.style.configure('main.%s.TFrame'%self._style_prefixe,background=value)
    self.style.configure('main.%s.TLabel'%self._style_prefixe,background=value)
    self.style.configure('R.%s.TButton'%self._style_prefixe,background=value,bordercolor=value,lightcolor=value,darkcolor=value)
    self.style.configure('L.%s.TButton'%self._style_prefixe,background=value,bordercolor=value,lightcolor=value,darkcolor=value)
   elif key=="foreground":
    self.style.configure('R.%s.TButton'%self._style_prefixe,arrowcolor=value)
    self.style.configure('L.%s.TButton'%self._style_prefixe,arrowcolor=value)
    self.style.configure('main.%s.TLabel'%self._style_prefixe,foreground=value)
   elif key=="disabledbackground":
    self.style.map('%s.TButton'%self._style_prefixe,background=[('active','!disabled',self.style.lookup('TEntry','selectbackground',('focus',))),('disabled',value)],)
    self.style.map('main.%s.TFrame'%self._style_prefixe,background=[('disabled',value)])
    self.style.map('main.%s.TLabel'%self._style_prefixe,background=[('disabled',value)])
   elif key=="disabledforeground":
    self.style.map('%s.TButton'%self._style_prefixe,arrowcolor=[('disabled',value)])
    self.style.map('main.%s.TLabel'%self._style_prefixe,foreground=[('disabled',value)])
   elif key=="cursor":ttk.Frame.configure(self,cursor=value)
   elif key=="tooltipbackground":self.style.configure('%s.tooltip.TLabel'%self._style_prefixe,background=value)
   elif key=="tooltipforeground":self.style.configure('%s.tooltip.TLabel'%self._style_prefixe,foreground=value)
   elif key=="tooltipalpha":self.tooltip_wrapper.configure(alpha=value)
   elif key=="tooltipdelay":self.tooltip_wrapper.configure(delay=value)
   self._properties[key]=value
   if key in ['showothermonthdays','firstweekday','weekenddays','maxdate','mindate']:
    self._display_calendar()
    self._check_sel_date()
    self._btns_date_range()
 @staticmethod
 def _check_weekenddays(weekenddays):
  try:
   if len(weekenddays)!=2:raise ValueError("weekenddays should be a list of two days.")
   else:
    for d in weekenddays:
     if d not in range(1,8):raise ValueError("weekenddays should contain integers between 1 and 7.")
  except TypeError:raise TypeError("weekenddays should be a list of two days.")
 def _textvariable_trace(self,*args):
  if self._properties.get("selectmode")=="day":
   date=self._textvariable.get()
   if not date:
    self._remove_selection()
    self._sel_date=None
   else:
    try:self._sel_date=self.parse_date(date)
    except Exception:
     if self._sel_date==None:self._textvariable.set('')
     else:self._textvariable.set(self.format_date(self._sel_date))
     raise ValueError("%r!=a valid date."%date)
    else:
     self._date=self._sel_date.replace(day=1)
     self._display_calendar()
     self._display_selection()
 def _setup_style(self,event=None):
  self.style.layout('L.%s.TButton'%self._style_prefixe,[('Button.focus',{'children':[('Button.leftarrow',None)]})])
  self.style.layout('R.%s.TButton'%self._style_prefixe,[('Button.focus',{'children':[('Button.rightarrow',None)]})])
  active_bg=self.style.lookup('TEntry','selectbackground',('focus',))
  sel_bg=self._properties.get('selectbackground')
  sel_fg=self._properties.get('selectforeground')
  dis_sel_bg=self._properties.get('disabledselectbackground')
  dis_sel_fg=self._properties.get('disabledselectforeground')
  dis_day_bg=self._properties.get('disableddaybackground')
  dis_day_fg=self._properties.get('disableddayforeground')
  cal_bg=self._properties.get('normalbackground')
  cal_fg=self._properties.get('normalforeground')
  hd_bg=self._properties.get("headersbackground")
  hd_fg=self._properties.get("headersforeground")
  bg=self._properties.get('background')
  fg=self._properties.get('foreground')
  dis_bg=self._properties.get('disabledbackground')
  dis_fg=self._properties.get('disabledforeground')
  bc=self._properties.get('bordercolor')
  om_fg=self._properties.get('othermonthforeground')
  om_bg=self._properties.get('othermonthbackground')
  omwe_fg=self._properties.get('othermonthweforeground')
  omwe_bg=self._properties.get('othermonthwebackground')
  we_bg=self._properties.get('weekendbackground')
  we_fg=self._properties.get('weekendforeground')
  self.style.configure('main.%s.TFrame'%self._style_prefixe,background=bg)
  self.style.configure('cal.%s.TFrame'%self._style_prefixe,background=bc)
  self.style.configure('main.%s.TLabel'%self._style_prefixe,background=bg,foreground=fg)
  self.style.configure('headers.%s.TLabel'%self._style_prefixe,background=hd_bg,foreground=hd_fg)
  self.style.configure('normal.%s.TLabel'%self._style_prefixe,background=cal_bg,foreground=cal_fg)
  self.style.configure('normal_om.%s.TLabel'%self._style_prefixe,background=om_bg,foreground=om_fg)
  self.style.configure('we_om.%s.TLabel'%self._style_prefixe,background=omwe_bg,foreground=omwe_fg)
  self.style.configure('sel.%s.TLabel'%self._style_prefixe,background=sel_bg,foreground=sel_fg)
  self.style.configure('we.%s.TLabel'%self._style_prefixe,background=we_bg,foreground=we_fg)
  size=max(self._header_font.actual()["size"],10)
  self.style.configure('%s.TButton'%self._style_prefixe,background=bg,arrowcolor=fg,arrowsize=size,bordercolor=bg,relief="flat",lightcolor=bg,darkcolor=bg)
  self.style.configure('%s.tooltip.TLabel'%self._style_prefixe,background=self._properties['tooltipbackground'],foreground=self._properties['tooltipforeground'])
  self.style.map('%s.TButton'%self._style_prefixe,background=[('active','!disabled',active_bg),('disabled',dis_bg)],bordercolor=[('active',active_bg)],relief=[('active','flat')],arrowcolor=[('disabled',dis_fg)],darkcolor=[('active',active_bg)],lightcolor=[('active',active_bg)])
  self.style.map('main.%s.TFrame'%self._style_prefixe,background=[('disabled',dis_bg)])
  self.style.map('main.%s.TLabel'%self._style_prefixe,background=[('disabled',dis_bg)],foreground=[('disabled',dis_fg)])
  self.style.map('sel.%s.TLabel'%self._style_prefixe,background=[('disabled',dis_sel_bg)],foreground=[('disabled',dis_sel_fg)])
  self.style.map(self._style_prefixe+'.TLabel',background=[('disabled',dis_day_bg)],foreground=[('disabled',dis_day_fg)])
 def _display_calendar(self):
  year,month=self._date.year,self._date.month
  header=self._month_names[month]
  self._header_month.configure(text=header.title())
  self._header_year.configure(text=str(year))
  self.tooltip_wrapper.remove_all()
  if self['showothermonthdays']:self._display_days_with_othermonthdays()
  else:self._display_days_without_othermonthdays()
  self._display_selection()
  maxdate=self['maxdate']
  mindate=self['mindate']
  if maxdate!=None:
   mi,mj=self._get_day_coords(maxdate)
   if mi!=None:
    for j in range(mj+1,7):self._calendar[mi][j].state(['disabled'])
    for i in range(mi+1,6):
     for j in range(7):self._calendar[i][j].state(['disabled'])
  if mindate!=None:
   mi,mj=self._get_day_coords(mindate)
   if mi!=None:
    for j in range(mj):self._calendar[mi][j].state(['disabled'])
    for i in range(mi):
     for j in range(7):self._calendar[i][j].state(['disabled'])
 def _display_days_without_othermonthdays(self):
  year,month=self._date.year,self._date.month
  cal=self._cal.monthdays2calendar(year,month)
  while len(cal)<6:cal.append([(0,i) for i in range(7)])
  week_days={i:'normal.%s.TLabel'%self._style_prefixe for i in range(7)}
  week_days[self['weekenddays'][0]-1]='we.%s.TLabel'%self._style_prefixe
  week_days[self['weekenddays'][1]-1]='we.%s.TLabel'%self._style_prefixe
  _,week_nb,d=self._date.isocalendar()
  if d==7 and self['firstweekday']=='sunday':week_nb+=1
  modulo=max(week_nb,52)
  for i_week in range(6):
   if i_week==0 or cal[i_week][0][0]:self._week_nbs[i_week].configure(text=str((week_nb+i_week-1)%modulo+1))
   else:self._week_nbs[i_week].configure(text='')
   for i_day in range(7):
    day_number,week_day=cal[i_week][i_day]
    style=week_days[i_day]
    label=self._calendar[i_week][i_day]
    label.state(['!disabled'])
    if day_number:
     txt=str(day_number)
     label.configure(text=txt,style=style)
     date=self.date(year,month,day_number)
     if date in self._calevent_dates:
      ev_ids=self._calevent_dates[date]
      i=len(ev_ids)-1
      while i>=0 and not self.calevents[ev_ids[i]]['tags']:i-=1
      if i>=0:
       tag=self.calevents[ev_ids[i]]['tags'][-1]
       label.configure(style='tag_%s.%s.TLabel'%(tag,self._style_prefixe))
      text='\n'.join(['➢ {}'.format(self.calevents[ev]['text']) for ev in ev_ids])
      self.tooltip_wrapper.add_tooltip(label,text)
    else:label.configure(text='',style=style)
 def _display_days_with_othermonthdays(self):
  year,month=self._date.year,self._date.month
  cal=self._cal.monthdatescalendar(year,month)
  next_m=month+1
  y=year
  if next_m==13:
   next_m=1
   y+=1
  if len(cal)<6:
   if cal[-1][-1].month==month:i=0
   else:i=1
   cal.append(self._cal.monthdatescalendar(y,next_m)[i])
   if len(cal)<6:cal.append(self._cal.monthdatescalendar(y,next_m)[i+1])
  week_days={i:'normal' for i in range(7)}
  week_days[self['weekenddays'][0]-1]='we'
  week_days[self['weekenddays'][1]-1]='we'
  prev_m=(month-2)%12+1
  months={month:'.%s.TLabel'%self._style_prefixe,next_m:'_om.%s.TLabel'%self._style_prefixe,prev_m:'_om.%s.TLabel'%self._style_prefixe}
  week_nb=cal[0][1].isocalendar()[1]
  modulo=max(week_nb,52)
  for i_week in range(6):
   self._week_nbs[i_week].configure(text=str((week_nb+i_week-1)%modulo+1))
   for i_day in range(7):
    style=week_days[i_day]+months[cal[i_week][i_day].month]
    label=self._calendar[i_week][i_day]
    label.state(['!disabled'])
    txt=str(cal[i_week][i_day].day)
    label.configure(text=txt,style=style)
    if cal[i_week][i_day] in self._calevent_dates:
     date=cal[i_week][i_day]
     ev_ids=self._calevent_dates[date]
     i=len(ev_ids)-1
     while i>=0 and not self.calevents[ev_ids[i]]['tags']:i-=1
     if i>=0:
      tag=self.calevents[ev_ids[i]]['tags'][-1]
      label.configure(style='tag_%s.%s.TLabel'%(tag,self._style_prefixe))
     text='\n'.join(['➢ {}'.format(self.calevents[ev]['text']) for ev in ev_ids])
     self.tooltip_wrapper.add_tooltip(label,text)
 def _get_day_coords(self,date):
  y1,y2=date.year,self._date.year
  m1,m2=date.month,self._date.month
  if y1==y2 or (y1-y2==1 and m1==1 and m2==12) or (y2-y1==1 and m2==1 and m1==12):
   _,w,d=date.isocalendar()
   _,wn,dn=self._date.isocalendar()
   if self['firstweekday']=='sunday':
    d%=7
    if d==0:w+=1
    if dn==7:wn+=1
   else:d-=1
   w-=wn
   w%=max(52,wn)
   if 0<=w<6:return w,d
   else:return None,None
  else:return None,None
 def _display_selection(self):
  if self._sel_date!=None:
   w,d=self._get_day_coords(self._sel_date)
   if w!=None:
    label=self._calendar[w][d]
    if label.cget('text'):label.configure(style='sel.%s.TLabel'%self._style_prefixe)
 def _reset_day(self,date):
  month=date.month
  w,d=self._get_day_coords(date)
  if w!=None:
   self.tooltip_wrapper.remove_tooltip(self._calendar[w][d])
   week_end=[0,6] if self['firstweekday']=='sunday' else [5,6]
   if month==date.month:
    if d in week_end:self._calendar[w][d].configure(style='we.%s.TLabel'%self._style_prefixe)
    else:self._calendar[w][d].configure(style='normal.%s.TLabel'%self._style_prefixe)
   else:
    if d in week_end:self._calendar[w][d].configure(style='we_om.%s.TLabel'%self._style_prefixe)
    else:self._calendar[w][d].configure(style='normal_om.%s.TLabel'%self._style_prefixe)
 def _remove_selection(self):
  if self._sel_date!=None:
   if self._sel_date in self._calevent_dates:self._show_event(self._sel_date)
   else:
    w,d=self._get_day_coords(self._sel_date)
    if w!=None:
     week_end=[0,6] if self['firstweekday']=='sunday' else [5,6]
     if self._sel_date.month==self._date.month:
      if d in week_end:self._calendar[w][d].configure(style='we.%s.TLabel'%self._style_prefixe)
      else:self._calendar[w][d].configure(style='normal.%s.TLabel'%self._style_prefixe)
     else:
      if d in week_end:self._calendar[w][d].configure(style='we_om.%s.TLabel'%self._style_prefixe)
      else:self._calendar[w][d].configure(style='normal_om.%s.TLabel'%self._style_prefixe)
 def _show_event(self,date):
  w,d=self._get_day_coords(date)
  if w!=None:
   label=self._calendar[w][d]
   if not label.cget('text'):return
   ev_ids=self._calevent_dates[date]
   i=len(ev_ids)-1
   while i>=0 and not self.calevents[ev_ids[i]]['tags']:i-=1
   if i>=0:
    tag=self.calevents[ev_ids[i]]['tags'][-1]
    label.configure(style='tag_%s.%s.TLabel'%(tag,self._style_prefixe))
   text='\n'.join(['➢ {}'.format(self.calevents[ev]['text']) for ev in ev_ids])
   self.tooltip_wrapper.remove_tooltip(label)
   self.tooltip_wrapper.add_tooltip(label,text)
 def check_date_range(self,date):
  maxdate=self['maxdate']
  mindate=self['mindate']
  if maxdate!=None and date>maxdate:return maxdate
  elif mindate!=None and date<mindate:return mindate
  else:return date
 def _check_sel_date(self):
  if self._sel_date!=None:
   maxdate=self['maxdate']
   mindate=self['mindate']
   if maxdate!=None and self._sel_date>maxdate:
    self._sel_date=maxdate
    self._display_selection()
   elif mindate!=None and self._sel_date<mindate:
    self._sel_date=mindate
    self._display_selection()
 def _btns_date_range(self):
  maxdate=self['maxdate']
  mindate=self['mindate']
  if maxdate!=None:
   max_year,max_month=maxdate.year,maxdate.month
   if self._date>maxdate:
    self._date=self._date.replace(year=max_year,month=max_month)
    self._display_calendar()
   dy=max_year-self._date.year
   if dy==0:
    self._r_year.state(['disabled'])
    if self._date.month==max_month:self._r_month.state(['disabled'])
    else:self._r_month.state(['!disabled'])
   elif dy==1:
    if self._date.month>max_month:self._r_year.state(['disabled'])
    else:
     self._r_year.state(['!disabled'])
     self._r_month.state(['!disabled'])
   else:
    self._r_year.state(['!disabled'])
    self._r_month.state(['!disabled'])
  if mindate!=None:
   min_year,min_month=mindate.year,mindate.month
   if self._date<mindate:
    self._date=self._date.replace(year=min_year,month=min_month)
    self._display_calendar()
   dy=self._date.year-min_year
   if dy==0:
    self._l_year.state(['disabled'])
    if self._date.month==min_month:self._l_month.state(['disabled'])
    else:self._l_month.state(['!disabled'])
   elif dy==1:
    if self._date.month>=min_month:
     self._l_year.state(['!disabled'])
     self._l_month.state(['!disabled'])
    else:self._l_year.state(['disabled'])
   else:
    self._l_year.state(['!disabled'])
    self._l_month.state(['!disabled'])
 def _next_month(self):
  year,month=self._date.year,self._date.month
  self._date=self._date+self.timedelta(days=calendar.monthrange(year,month)[1])
  self._display_calendar()
  self.event_generate('<<CalendarMonthChanged>>')
  self._btns_date_range()
 def _prev_month(self):
  self._date=self._date-self.timedelta(days=1)
  self._date=self._date.replace(day=1)
  self._display_calendar()
  self.event_generate('<<CalendarMonthChanged>>')
  self._btns_date_range()
 def _next_year(self):
  year=self._date.year
  self._date=self._date.replace(year=year+1)
  self._display_calendar()
  self.event_generate('<<CalendarMonthChanged>>')
  self._btns_date_range()
 def _prev_year(self):
  year=self._date.year
  self._date=self._date.replace(year=year-1)
  self._display_calendar()
  self.event_generate('<<CalendarMonthChanged>>')
  self._btns_date_range()
 def _on_click(self,event):
  if self._properties['state']=='normal':
   label=event.widget
   if "disabled" not in label.state():
    day=label.cget("text")
    style=label.cget("style")
    if style in ['normal_om.%s.TLabel'%self._style_prefixe,'we_om.%s.TLabel'%self._style_prefixe]:
     if label in self._calendar[0]:self._prev_month()
     else:self._next_month()
    if day:
     day=int(day)
     year,month=self._date.year,self._date.month
     self._remove_selection()
     self._sel_date=self.date(year,month,day)
     self._display_selection()
     if self._textvariable!=None:self._textvariable.set(self.format_date(self._sel_date))
     self.event_generate("<<CalendarSelected>>")
 def _get_date_pattern(self,date_pattern,locale=None):
  if locale==None:locale=self._properties["locale"]
  if date_pattern=="short":return get_date_format("short",locale).pattern
  pattern=date_pattern.lower()
  res=((re.search(r"^y+[^a-zA-Z]*m{1,2}[^a-z]*d{1,2}[^mdy]*$",pattern)!=None) or (re.search(r"^m{1,2}[^a-zA-Z]*d{1,2}[^a-z]*y+[^mdy]*$",pattern)!=None) or (re.search(r"^d{1,2}[^a-zA-Z]*m{1,2}[^a-z]*y+[^mdy]*$",pattern)!=None))
  if res:return pattern.replace('m','M')
  raise ValueError("%r!=a valid date pattern"%date_pattern)
 def format_date(self,date=None):return format_date(date,self._properties['date_pattern'],self._properties['locale'])
 def parse_date(self,date):
  date_format=self._properties['date_pattern'].lower()
  year_idx=date_format.index('y')
  month_idx=date_format.index('m')
  day_idx=date_format.index('d')
  indexes=[(year_idx,'Y'),(month_idx,'M'),(day_idx,'D')]
  indexes.sort()
  indexes=dict([(item[1],idx) for idx,item in enumerate(indexes)])
  numbers=re.findall(r'(\d+)',date)
  year=numbers[indexes['Y']]
  if len(year)==2:year=2000+int(year)
  else:year=int(year)
  month=int(numbers[indexes['M']])
  day=int(numbers[indexes['D']])
  if month>12:month,day=day,month
  return self.date(year,month,day)
 def see(self,date):
  if isinstance(date,self.datetime):date=date.date()
  elif not isinstance(date,self.date):raise TypeError("expected %s for the 'date' argument."%self.date)
  self._date=self._date.replace(month=date.month,year=date.year)
  self._display_calendar()
  self._btns_date_range()
 def selection_clear(self):
  self._remove_selection()
  self._sel_date=None
  if self._textvariable!=None:self._textvariable.set('')
 def selection_get(self):
  if self._properties.get("selectmode")=="day":return self._sel_date
  else:return None
 def selection_set(self,date):
  if self._properties.get("selectmode")=="day" and self._properties['state']=='normal':
   if date==None:self.selection_clear()
   else:
    if isinstance(date,self.datetime):self._sel_date=date.date()
    elif isinstance(date,self.date):self._sel_date=date
    else:
     try:self._sel_date=self.parse_date(date)
     except Exception:raise ValueError("%r!=a valid date."%date)
    if self['mindate']!=None and self._sel_date<self['mindate']:self._sel_date=self['mindate']
    elif self['maxdate']!=None and self._sel_date>self['maxdate']:self._sel_date=self['maxdate']
    if self._textvariable!=None:self._textvariable.set(self.format_date(self._sel_date))
    self._date=self._sel_date.replace(day=1)
    self._display_calendar()
    self._display_selection()
    self._btns_date_range()
 def get_displayed_month(self):return self._date.month,self._date.year
 def get_date(self):
  if self._sel_date!=None:return self.format_date(self._sel_date)
  else:return ""
 def calevent_create(self,date,text,tags=[]):
  if isinstance(date,Calendar.datetime):date=date.date()
  if not isinstance(date,Calendar.date):raise TypeError("date option should be a %s instance"%(Calendar.date))
  if self.calevents:ev_id=max(self.calevents)+1
  else:ev_id=0
  if isinstance(tags,str):tags_=[tags]
  else:tags_=list(tags)
  self.calevents[ev_id]={'date':date,'text':text,'tags':tags_}
  for tag in tags_:
   if tag not in self._tags:self._tag_initialize(tag)
  if date not in self._calevent_dates:self._calevent_dates[date]=[ev_id]
  else:self._calevent_dates[date].append(ev_id)
  self._show_event(date)
  return ev_id
 def _calevent_remove(self,ev_id):
  try:date=self.calevents[ev_id]['date']
  except KeyError:ValueError("event %s does not exists"%ev_id)
  else:
   del self.calevents[ev_id]
   self._calevent_dates[date].remove(ev_id)
   if not self._calevent_dates[date]:
    del self._calevent_dates[date]
    self._reset_day(date)
   else:self._show_event(date)
 def calevent_remove(self,*ev_ids,**kw):
  if ev_ids:
   if 'all' in ev_ids:ev_ids=self.get_calevents()
   for ev_id in ev_ids:self._calevent_remove(ev_id)
  else:
   date=kw.get('date')
   tag=kw.get('tag')
   evs=self.get_calevents(tag=tag,date=date)
   for ev_id in evs:self._calevent_remove(ev_id)
 def calevent_cget(self,ev_id,option):
  try:ev=self.calevents[ev_id]
  except KeyError:raise ValueError("event %s does not exists"%ev_id)
  else:
   try:return ev[option]
   except KeyError:raise ValueError('unknown option "%s"'%option)
 def calevent_configure(self,ev_id,**kw):
  try:ev=self.calevents[ev_id]
  except KeyError:raise ValueError("event %s does not exists"%ev_id)
  else:
   text=kw.pop('text',None)
   tags=kw.pop('tags',None)
   date=kw.pop('date',None)
   if kw:raise KeyError('Invalid keyword option(s) %s,valid options are "text","tags" and "date".'%(kw.keys(),))
   else:
    if text!=None:ev['text']=str(text)
    if tags!=None:
     if isinstance(tags,str):tags_=[tags]
     else:tags_=list(tags)
     for tag in tags_:
      if tag not in self._tags:self._tag_initialize(tag)
     ev['tags']=tags_
    if date!=None:
     if isinstance(date,Calendar.datetime):date=date.date()
     if not isinstance(date,Calendar.date):raise TypeError("date option should be a %s instance"%(Calendar.date))
     old_date=ev['date']
     self._calevent_dates[old_date].remove(ev_id)
     if not self._calevent_dates[old_date]:self._reset_day(old_date)
     else:self._show_event(old_date)
     ev['date']=date
     if date not in self._calevent_dates:self._calevent_dates[date]=[ev_id]
     else:self._calevent_dates[date].append(ev_id)
    self._show_event(ev['date'])
 def calevent_raise(self,ev_id,above=None):
  try:date=self.calevents[ev_id]['date']
  except KeyError:raise ValueError("event %s does not exists"%ev_id)
  else:
   evs=self._calevent_dates[date]
   if above==None:
    evs.remove(ev_id)
    evs.insert(0,ev_id)
   else:
    if above not in evs:raise ValueError("event %s does not exists on %s"%(above,date))
    else:
     evs.remove(ev_id)
     index=evs.index(above)
     evs.insert(index,ev_id)
   self._show_event(date)
 def calevent_lower(self,ev_id,below=None):
  try:date=self.calevents[ev_id]['date']
  except KeyError:raise ValueError("event %s does not exists"%ev_id)
  else:
   evs=self._calevent_dates[date]
   if below==None:
    evs.remove(ev_id)
    evs.append(ev_id)
   else:
    if below not in evs:raise ValueError("event %s does not exists on %s"%(below,date))
    else:
     evs.remove(ev_id)
     index=evs.index(below)+1
     evs.insert(index,ev_id)
   self._show_event(date)
 def get_calevents(self,date=None,tag=None):
  if date!=None:
   if isinstance(date,Calendar.datetime):date=date.date()
   if not isinstance(date,Calendar.date):raise TypeError("date option should be a %s instance"%(Calendar.date))
   try:
    if tag!=None:return tuple(ev_id for ev_id in self._calevent_dates[date] if tag in self.calevents[ev_id]['tags'])
    else:return tuple(self._calevent_dates[date])
   except KeyError:return()
  elif tag!=None:return tuple(ev_id for ev_id,prop in self.calevents.items() if tag in prop['tags'])
  else:return tuple(self.calevents.keys())
 def _tag_initialize(self,tag):
  props=dict(foreground='white',background='royal blue')
  self._tags[tag]=props
  self.style.configure('tag_%s.%s.TLabel'%(tag,self._style_prefixe),**props)
 def tag_config(self,tag,**kw):
  if tag not in self._tags:self._tags[tag]={}
  props=dict(foreground='white',background='royal blue')
  props.update(self._tags[tag])
  props.update(kw)
  self.style.configure('tag_%s.%s.TLabel'%(tag,self._style_prefixe),**props)
  self._tags[tag]=props
 def tag_cget(self,tag,option):
  try:prop=self._tags[tag]
  except KeyError:raise ValueError('unknow tag "%s"'%tag)
  else:
   try:return prop[option]
   except KeyError:raise ValueError('unknow option "%s"'%option)
 def tag_names(self):return tuple(self._tags.keys())
 def tag_delete(self,tag):
  try:del self._tags[tag]
  except KeyError:raise ValueError('tag "%s" does not exists'%tag)
  else:
   for props in self.calevents.values():
    if tag in props['tags']:props['tags'].remove(tag)
   self._display_calendar()
 def keys(self):return list(self._properties.keys())
 def cget(self,key):return self[key]
 def configure(self,cnf={},**kw):
  if not isinstance(cnf,dict):raise TypeError("Expected a dictionary or keyword arguments.")
  kwargs=cnf.copy()
  kwargs.update(kw)
  for item,value in kwargs.items():self[item]=value
 config=configure