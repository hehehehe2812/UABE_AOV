import tkinter as tk
from tkinter import Toplevel
from Config import Config  # 引入 Config 模組

about_window = None  # 全域變數，避免重複開啟視窗

# 讓視窗置中
def center_window(win):
    win.update_idletasks()  # 更新視窗資訊
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    window_width = win.winfo_width()
    window_height = win.winfo_height()
    
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    
    win.geometry(f"{window_width}x{window_height}+{x}+{y}")

def About():
    global about_window
    if about_window and about_window.winfo_exists():  # 確保視窗唯一
        about_window.lift()  # 提升視窗到最前
        return
    
    # 讀取 Config 模組的語言設定
    lang, lang_code = Config.reload_config()  # 假設 reload_config 會返回當前語言和語言代碼

    about_window = Toplevel()
    about_window.title(lang["about"])
    about_window.geometry("540x200")

    # 禁止最小化和放大
    about_window.resizable(False, False)  
    about_window.attributes('-toolwindow', True)  

    # **強制最上層**
    about_window.attributes('-topmost', True)  

    # 設定為模態視窗（阻止主視窗操作）
    about_window.grab_set()  
    about_window.transient()  

    # 設計 About 視窗 UI，並依據語言設定更新文字
    title_label = tk.Label(about_window, text=lang["title"], font=("Microsoft YaHei", 23, "bold"))
    title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
    
    version_label = tk.Label(about_window, text="Version : 1.0.0", font=("Microsoft YaHei", 13))
    version_label.grid(row=0, column=1, padx=20, pady=10, sticky="w")
    
    desc_label = tk.Label(
        about_window,
        text=lang["about_text"],
        wraplength=460,
        justify="left",
        font=("Microsoft YaHei", 13)
    )
    desc_label.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="w")

    author_label = tk.Label(about_window, text=lang["author"], font=("Microsoft YaHei", 13))
    author_label.grid(row=3, column=0, padx=20, sticky="w")

    # 設定關閉時的行為
    about_window.protocol("WM_DELETE_WINDOW", on_close)

    # 監聽 main 視窗被點擊時的行為
    about_window.bind("<FocusOut>", on_main_click)

    # 視窗畫面置中
    about_window.update()  # 讓 Tkinter 先計算出視窗大小
    center_window(about_window)

    # 延遲焦點設置
    about_window.after(1, force_focus)  # 1 毫秒後強制焦點

def on_main_click(event=None):
    """ 當試圖點擊 main 視窗時，讓 About 閃爍並發出提示音 """
    if about_window:
        about_window.bell()  # 發出聲音
        force_focus()

def force_focus():
    """ 強制 About 視窗保持在最上層並奪回焦點 """
    if about_window:
        about_window.lift()
        about_window.attributes('-topmost', True)  # 讓 About 始終置頂
        about_window.after(50, lambda: about_window.focus_force())  # 確保焦點回到 About

def on_close():
    global about_window
    if about_window:
        about_window.destroy()
        about_window = None  # 清除變數，確保下次能正確開啟
