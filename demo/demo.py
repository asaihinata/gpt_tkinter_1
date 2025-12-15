import tkinter as tk
from tkinter import scrolledtext
import mylibral

# --- ウィンドウ作成 ---
root = tk.Tk()
root.title("GPT Tkinter Demo")

# --- テキスト入力欄 ---
input_label = tk.Label(root, text="入力テキスト:")
input_label.pack()

txt_input = tk.Entry(root, width=50)
txt_input.pack()

# --- 出力表示エリア ---
output_area = scrolledtext.ScrolledText(root, width=60, height=15)
output_area.pack()

# --- 実行処理 ---
def run_demo():
    user_text = txt_input.get()
    if not user_text:
        return

    # 例: mylibral にある関数を呼び出す
    # たとえば何か加工する関数があるとする
    try:
        result = mylibral.process(user_text)
    except AttributeError:
        result = f"関数 process が見つかりません: {user_text}"

    output_area.insert(tk.END, f"> 入力: {user_text}\n")
    output_area.insert(tk.END, f"→ 出力: {result}\n\n")

# --- 実行ボタン ---
btn_run = tk.Button(root, text="実行", command=run_demo)
btn_run.pack()

root.mainloop()
