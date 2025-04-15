import tkinter as tk
from tkinter import Menu, filedialog, messagebox
from Config import Config  # Config 模組
from About import About  # About 模組
from UI.CenterWindows import center_window
from AssetbundleUtils.AssetsList import list_assets_window
import os, shutil

Selected_Dir = None  # Save Selected Directory
Selected_File = None  # 選擇的檔案

PickDir_Title = ""  # DirectoryPicker 標題
PickFile_Title = ""  # FilePicker 標題

SaveFile_Title = ""  # 存檔 標題


# 即時更新語言設定
def reload_config():
    global PickFile_Title, PickDir_Title, SaveFile_Title
    lang, lang_code = Config.reload_config()

    root.title(lang["title"])
    menu.entryconfig(1, label=lang["file"])
    menu.entryconfig(2, label=lang["help"])
    menu.entryconfig(3, label=lang["lang"])

    subMenu.entryconfig(0, label=lang["open_file"])
    subMenu.entryconfig(1, label=lang["open_dir"])
    subMenu.entryconfig(2, label=lang["save"])
    subMenu.entryconfig(3, label=lang["exit"])

    helpMenu.entryconfig(0, label=lang["about"])

    langMenu.entryconfig(0, label=lang["zh_tw"])
    langMenu.entryconfig(1, label=lang["zh_cn"])
    langMenu.entryconfig(2, label=lang["english"])
    langMenu.entryconfig(3, label=lang["Vietnamese"])

    # 更新主視窗中的文字，**如果沒有選擇檔案，才會顯示 lang["No_File"]**
    if Selected_File is None:
        set_file_text(lang["No_File"])
    Info_BTN.config(text=lang["Info"])

    # FilePicker 標題
    PickFile_Title = lang["Pick_File"]
    PickDir_Title = lang["Pick_Dir"]
    # SaveFile 標題
    SaveFile_Title = lang["Save_File"]


# 變更語言後，立即更新 UI
def setting_languages(new_lang_code):
    Config.setting_languages(new_lang_code)  # 更新語言設定
    reload_config()  # 重新加載並更新 UI


# 打開檔案選擇器並設置檔案類型為 .assetbundle
def open_file():
    global Selected_File, Selected_Dir
    Selected_Dir = None
    file_path = filedialog.askopenfilename(
        title=PickFile_Title, filetypes=[("AssetBundle files", "*.assetbundle")]
    )
    if file_path:
        Selected_File = file_path
        file = os.path.basename(file_path)  # 只取檔名+副檔名
        set_file_text(file)  # 更新標籤顯示檔案名稱


# select folder
def open_dir():
    global Selected_Dir, Selected_File
    Selected_File = None
    file_path = filedialog.askdirectory(title=PickDir_Title)
    if file_path:
        Selected_Dir = file_path
        file = os.path.basename(file_path)  # 只取檔名+副檔名
        set_file_text(file)  # 更新標籤顯示檔案名稱


# 設定 Label 文字
def set_file_text(file_name):
    label_file.config(state="normal")  # 解除不可編輯狀態
    label_file.delete("1.0", tk.END)  # 清除舊內容
    label_file.insert("1.0", file_name)  # 插入新內容
    label_file.config(state="disabled")  # 設回不可編輯狀態


# 開啟 Assets List
def Get_Assests():
    if Selected_File:
        list_assets_window(Selected_File, IsInputDir=False)
    elif Selected_Dir:
        list_assets_window(Selected_Dir, IsInputDir=True)
    else:
        root.bell()


def show_dialog(title, message):
    """顯示一個簡單的對話框"""
    messagebox.showinfo(title, message)


# 保存 (複製出來)
def save_assetbundle(lang):
    list_cache_file = os.listdir("./AssetbundleUtils/tmp")
    i = len(list_cache_file)
    bDir = False
    match i:
        case 0:
            return
        case 1:
            bDir = False
        case _:
            bDir = True

    # 讓使用者選擇新檔案名稱和位置
    new_path = (
        filedialog.askdirectory(title=lang["SaveDir_Title"]) 
        if bDir
        else filedialog.asksaveasfilename(
            title=SaveFile_Title,
            defaultextension=".assetbundle",  # 預設副檔名，可依需求修改
            filetypes=[("AssetBundle files", "*.assetbundle")],
        )
    )

    if not new_path:
        return  # 使用者取消存檔

    try:
        if not bDir:
            return shutil.move(
            f"./AssetbundleUtils/tmp/{list_cache_file[0]}", new_path
        )  # 移動並重新命名檔案

        for name_file in list_cache_file:

            shutil.move(
           f"./AssetbundleUtils/tmp/{name_file}", os.path.join( new_path , name_file)
        ) 
        show_dialog(lang["Save_Successful"], lang["Save_file_to"] + "\n" + new_path)
    except Exception as e:
        show_dialog("Save Failed", f"Error:\n{str(e)}")


def on_close():
    root.quit()  # 關閉 Tk() 主視窗
    try:
        shutil.rmtree("./AssetbundleUtils/tmp")
    except:
        print


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
subMenu.add_command(label=lang["open_dir"], command=open_dir)
subMenu.add_command(label=lang["save"], command=lambda: save_assetbundle(lang))
subMenu.add_command(label=lang["exit"], command=on_close)
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
langMenu.add_command(label=lang["Vietnamese"], command=lambda: setting_languages("vn"))
# 選擇檔案標題
PickFile_Title = lang["Pick_File"]
PickDir_Title = lang["Pick_Dir"]

# SaveFile 標題
SaveFile_Title = lang["Save_File"]

# 使用 Frame 包裹最外層的控件
root_frame = tk.Frame(root, padx=13, pady=13)
root_frame.pack(fill=tk.BOTH, expand=True)
# 檔案名稱顯示區域 + 滾動條容器
file_frame = tk.Frame(root_frame)
file_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
# 創建不可編輯的文本框（顯示檔案名稱）
label_file = tk.Text(
    file_frame, font=("Microsoft YaHei", 13), height=1, wrap="none", width=25
)  # 固定寬度，避免壓縮按鈕
label_file.insert("1.0", lang["No_File"])  # 初始文字-請選擇一個檔案
label_file.config(state="disabled")  # 設回不可編輯狀態
label_file.pack(fill=tk.X, expand=True)
# 按鈕
Info_BTN = tk.Button(
    root_frame,
    text=lang["Info"],
    font=("Microsoft YaHei", 13),
    width=8,
    height=2,
    command=Get_Assests,
)
Info_BTN.pack(side=tk.LEFT, padx=(10, 0))  # 加點間距，避免太擠

root.protocol("WM_DELETE_WINDOW", on_close)

# 視窗畫面置中
root.update()  # 讓 Tkinter 先計算出視窗大小
center_window(root, 100)

root.mainloop()
