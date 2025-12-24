from pathlib import Path
import json
global data
with open(f"{Path(__file__).parent}\color.json","r",encoding="utf-8")as f:data=json.load(f)
class Color:
 def __init__(self,color):self.colors=color
 def color(self,other=None):
  if self.colors==None or not isinstance(self.colors,str):return other
  t=self.colors.lower()
  if t.startswith("rgb(") and t.endswith(")"):
   try:
    r,g,b=map(int,t[4:-1].split(","))
    return self.rgb_to_hex(r,g,b)
   except:return other
  if t.startswith("rgba(") and t.endswith(")"):
   try:
    r,g,b,a=map(int,t[5:-1].split(","))
    return self.rgba_to_hex(r,g,b,a)
   except:return other
  if t.startswith("hsv(") and t.endswith(")"):
   try:
    h,s,v=map(float,t[4:-1].split(","))
    return self.hsv_to_hex(h,s,v)
   except:return other
  return self.color_name(self.colors,other)
 def rgb_to_hex(self,r,g,b):
  if r<0 or r>255 or g<0 or g>255 or b<0 or b>255:
   return None
  return "#{:02X}{:02X}{:02X}".format(r,g,b)
 def rgba_to_hex(self,r,g,b,a):
  if r<0 or r>255 or g<0 or g>255 or b<0 or b>255 or a<0 or a>255:return None
  return "#{:02X}{:02X}{:02X}{:02X}".format(r,g,b,a)
 def hsv_to_hex(self,h,s,v):
  if h<0 or h>1 or s<0 or s>1 or v<0 or v>1:return None
  r,g,b=self.hsv_to_rgb(h,s,v)
  return self.rgb_to_hex(int(r*255),int(g*255),int(b*255))
 def color_name(self,colorname,other=None):
  try:return data[colorname] if colorname in data else other
  except:return other
 def hsv_to_rgb(self,h,s,v):
  if s==0.0:return v,v,v
  i=int(h*6.0)
  f=(h*6.0)-i
  p,q,t,i=v*(1.0-s),v*(1.0-s*f),v*(1.0-s*(1.0-f)),i%6
  if i==0:return v,t,p
  if i==1:return q,v,p
  if i==2:return p,v,t
  if i==3:return p,q,v
  if i==4:return t,p,v
  if i==5:return v,p,q