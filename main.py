import tkinter as tk
from tkinter import Menu, filedialog
from Config import Config  # Config 模組
from About import About  # About 模組
from AssetbundleUtils.AssetsList import list_assets_window
import os


Selected_File = None # 選擇的檔案
PickFile_Title = "" #FilePicker 標題


# 讓視窗置中
def center_window(win, offset_y=100):
    win.update_idletasks()  # 更新視窗資訊
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    window_width = win.winfo_width()
    window_height = win.winfo_height()
    
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2 - offset_y  # 上移 offset_y 像素
    
    win.geometry(f"{window_width}x{window_height}+{x}+{y}")

# 即時更新語言設定
def reload_config():
    global PickFile_Title
    lang, lang_code = Config.reload_config()
    
    root.title(lang["title"])
    menu.entryconfig(1, label=lang["file"])
    menu.entryconfig(2, label=lang["help"])
    menu.entryconfig(3, label=lang["lang"])

    subMenu.entryconfig(0, label=lang["open_file"])
    # subMenu.entryconfig(1, label=lang["open_dir"])
    subMenu.entryconfig(1, label=lang["save"])
    subMenu.entryconfig(2, label=lang["exit"])

    helpMenu.entryconfig(0, label=lang["about"])

    langMenu.entryconfig(0, label=lang["zh_tw"])
    langMenu.entryconfig(1, label=lang["zh_cn"])
    langMenu.entryconfig(2, label=lang["english"])

    # 更新主視窗中的文字，**如果沒有選擇檔案，才會顯示 lang["No_File"]**
    if Selected_File is None:
        set_file_text(lang["No_File"])
    Info_BTN.config(text=lang["Info"])

    # FilePicker 標題
    PickFile_Title = lang["Pick_File"]

# 變更語言後，立即更新 UI
def setting_languages(new_lang_code):
    Config.setting_languages(new_lang_code)  # 更新語言設定
    reload_config()  # 重新加載並更新 UI

# 打開檔案選擇器並設置檔案類型為 .assetbundle
def open_file():
    global Selected_File
    file_path = filedialog.askopenfilename(
        title=PickFile_Title,
        filetypes=[("AssetBundle files", "*.assetbundle")]
    )
    if file_path:
        Selected_File = file_path
        file = os.path.basename(file_path)  # 只取檔名+副檔名
        set_file_text(file)  # 更新標籤顯示檔案名稱

# 設定 Label 文字
def set_file_text(file_name):
    label_file.config(state="normal")  # 解除不可編輯狀態
    label_file.delete("1.0", tk.END)   # 清除舊內容
    label_file.insert("1.0", file_name)  # 插入新內容
    label_file.config(state="disabled")  # 設回不可編輯狀態

# 開啟 Assets List
def Get_Assests():
    if Selected_File:
        list_assets_window(Selected_File)
    else:
        root.bell()


# 初始化 GUI
root = tk.Tk()
lang, lang_code = Config.reload_config()  # 使用 Config 來讀取設定

root.title(lang["title"])
root.geometry("390x87")

# 禁止最小化和放大
root.resizable(False, False)
# 設定視窗的圖標
root.iconbitmap("icon.ico")
# Menu 初始化
menu = Menu(root)
root.config(menu=menu)
# 檔案選單
subMenu = Menu(menu, tearoff=0)
menu.add_cascade(label=lang["file"], menu=subMenu)
subMenu.add_command(label=lang["open_file"], command=open_file)
# subMenu.add_command(label=lang["open_dir"])
subMenu.add_command(label=lang["save"])
subMenu.add_command(label=lang["exit"])
# 幫助選單
helpMenu = Menu(menu, tearoff=0)
menu.add_cascade(label=lang["help"], menu=helpMenu)
helpMenu.add_command(label=lang["about"], command=lambda: About.About())
# 語言選單
langMenu = Menu(menu, tearoff=0)
menu.add_cascade(label=lang["lang"], menu=langMenu)
langMenu.add_command(label=lang["zh_tw"], command=lambda: setting_languages("zh-tw"))
langMenu.add_command(label=lang["zh_cn"], command=lambda: setting_languages("zh-cn"))
langMenu.add_command(label=lang["english"], command=lambda: setting_languages("en"))
# 選擇檔案標題
PickFile_Title = lang["Pick_File"]

# 使用 Frame 包裹最外層的控件
root_frame = tk.Frame(root, padx=13, pady=13)
root_frame.pack(fill=tk.BOTH, expand=True)
# 檔案名稱顯示區域 + 滾動條容器
file_frame = tk.Frame(root_frame)
file_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
# 創建不可編輯的文本框（顯示檔案名稱）
label_file = tk.Text(file_frame, font=("Microsoft YaHei", 13), height=1, wrap="none", width=25)  # 固定寬度，避免壓縮按鈕
label_file.insert("1.0", lang["No_File"])  # 初始文字-請選擇一個檔案
label_file.config(state="disabled")  # 設回不可編輯狀態
label_file.pack(fill=tk.X, expand=True)
# 按鈕
Info_BTN = tk.Button(root_frame, text=lang["Info"], font=("Microsoft YaHei", 13), width=7, height=2, command=Get_Assests)
Info_BTN.pack(side=tk.LEFT, padx=(10, 0))  # 加點間距，避免太擠

# 視窗畫面置中
root.update()  # 讓 Tkinter 先計算出視窗大小
center_window(root)

root.mainloop()
