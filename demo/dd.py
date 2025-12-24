import tkinter as tk

root=tk.Tk()

font_path="fonts.ttf"

root.tk.call("font","create","CustomFont","-family","NotoSansJP","-size",20,"-fontfile",font_path)

tk.Label(root,text="カスタムフォント使用",font="CustomFont").pack()

root.mainloop()
