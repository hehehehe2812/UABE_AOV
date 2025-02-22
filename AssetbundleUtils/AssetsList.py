import tkinter as tk
from tkinter import ttk, Toplevel, filedialog, messagebox
from Config import Config  # 引入 Config 模組
import os, UnityPy_AOV

DEBUG = False  # 切換為 True 進入調適模式

list_window = None  # 避免重複開啟視窗
global current_sort_col, ascending
env = None  # 全域變數儲存 UnityPy 環境
current_sort_col = "Name"
ascending = True
selected_items = []  # 用於記錄使用者選取的項目


def center_window(win):
    """讓視窗置中
    """
    win.update_idletasks()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    window_width = win.winfo_width()
    window_height = win.winfo_height()
    
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    
    win.geometry(f"{window_width}x{window_height}+{x}+{y}")

def list_assets_window(input_path):
    global list_window, name_entry, path_id_entry, type_entry, env
    if list_window and list_window.winfo_exists():
        list_window.lift()
        return
    
    lang, lang_code = Config.reload_config()

    if DEBUG:
        list_window = tk.Tk()  # 如果是調適模式，使用 Tk()
    else:
        list_window = Toplevel()  # 正常運行時使用 Toplevel()
        list_window.grab_set()
        list_window.transient()
        #list_window.attributes('-topmost', True)

    list_window.title(lang["List_Window_title"])
    list_window.geometry("900x600")
    list_window.iconbitmap("icon.ico")

    frame = tk.Frame(list_window)
    frame.pack(fill=tk.BOTH, expand=True)

    columns = ["Name", "Type", "Path ID", "Size"]
    tree = ttk.Treeview(frame, columns=columns, show="headings")
    column_widths = {"Name": 250, "Type": 130, "Path ID": 170, "Size": 60}

    for col in columns:
        tree.heading(col, text=col, command=lambda c=col: sort_column(tree, c))
        tree.column(col, anchor="w", width=column_widths[col])
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.LEFT, fill=tk.Y)

    info_frame = tk.Frame(frame, width=290, bg="#F0F0F0")
    info_frame.pack(side=tk.RIGHT, fill=tk.Y)

    # 新增標籤與輸入框
    def create_label_entry(label_text):
        tk.Label(info_frame, text=label_text, font=("Microsoft JhengHei", 10)).pack(anchor="w", padx=20, pady=(10, 0))
        entry = tk.Text(info_frame, height=1, width=27, state="disabled", wrap="none", font=("Microsoft JhengHei", 10))
        entry.pack(padx=20, pady=5)
        return entry

    name_entry = create_label_entry(lang["Name"])
    path_id_entry = create_label_entry(lang["PathID"])
    type_entry = create_label_entry(lang["Type"])

    # 第一排按鈕
    btn_frame = tk.Frame(info_frame, bg="#F0F0F0")
    btn_frame.pack(fill="x", pady=5, padx=20)
    
    export_raw_btn = tk.Button(btn_frame, text=lang["Export_Raw"], command=lambda: export_raw(lang))
    import_raw_btn = tk.Button(btn_frame, text=lang["Import_Raw"], command=lambda: import_raw(lang))
    
    export_raw_btn.grid(row=0, column=0, sticky="ew", padx=5)
    import_raw_btn.grid(row=0, column=1, sticky="ew", padx=5)
    
    btn_frame.columnconfigure(0, weight=1)
    btn_frame.columnconfigure(1, weight=1)
    
    # 第二排按鈕
    btn_frame2 = tk.Frame(info_frame, bg="#F0F0F0")
    btn_frame2.pack(fill="x", pady=5, padx=20)
    
    export_texture_btn = tk.Button(btn_frame2, text=lang["Export_Texture"], command=lambda: export_texture(lang))
    import_texture_btn = tk.Button(btn_frame2, text=lang["Import_Texture"], command=lambda: import_texture(lang))
    
    export_texture_btn.grid(row=0, column=0, sticky="ew", padx=5)
    import_texture_btn.grid(row=0, column=1, sticky="ew", padx=5)
    
    btn_frame2.columnconfigure(0, weight=1)
    btn_frame2.columnconfigure(1, weight=1)

    # 新增一個與兩個按鈕 + 間隔等寬的按鈕
    btn_frame3 = tk.Frame(info_frame, bg="#F0F0F0")
    btn_frame3.pack(fill="x", pady=5, padx=20)
    
    extra_btn = tk.Button(btn_frame3, text=lang["Export_Mesh"], command=lambda: export_mesh(lang))
    extra_btn.pack(fill="x", padx=5)  # 讓按鈕完全填滿

    progress_var = tk.IntVar()
    progress_bar = ttk.Progressbar(list_window, variable=progress_var, maximum=100, mode='determinate')
    progress_bar.pack(fill=tk.X)

    # 綁定 Ctrl + A 鍵盤事件
    tree.bind('<Control-a>', lambda event, t=tree: select_all(t))
    tree.bind("<ButtonRelease-1>", lambda event, t=tree: on_item_selected(event, t))  # 綁定點擊事件

    list_window.protocol("WM_DELETE_WINDOW", on_close)
    list_window.update()
    center_window(list_window)

    list_window.after(100, lambda: list_assets(input_path, tree, progress_var, progress_bar))

def list_assets(input_path, tree, progress_var, progress_bar):
    global env
    env = UnityPy_AOV.load(input_path)
    assets = []
    total = len(env.objects)

    for i, obj in enumerate(env.objects, 1):
        dump_tree = obj.read_typetree()
        data = obj.read()
        name = getattr(data, 'm_Name', 'Unnamed asset') or "SpringNode"
        assets.append((name, obj.type.name, obj.path_id, obj.byte_size))
        progress_var.set(int((i / total) * 100))
        tree.update_idletasks()
    
    assets.sort(key=lambda x: x[0])
    update_treeview(tree, assets)
    progress_var.set(100)
    progress_bar.pack_forget()

def update_treeview(tree, assets):
    for row in tree.get_children():
        tree.delete(row)
    
    for asset in assets:
        tree.insert("", "end", values=asset)
    
    apply_row_colors(tree)

def apply_row_colors(tree):
    for index, item in enumerate(tree.get_children()):
        color = "#E6F7FF" if index % 2 == 0 else "#FFFFFF"
        tree.item(item, tags=(color,))
    tree.tag_configure("#E6F7FF", background="#E6F7FF")
    tree.tag_configure("#FFFFFF", background="#FFFFFF")

# 因為沒有內建 ctrl + a，自己寫一個
def select_all(tree):
    global selected_items
    selected_items = []  # 清空舊選擇
    # 全選並收集資料
    for item in tree.get_children():
        tree.selection_add(item)  # 選擇項目
        item_values = tree.item(item, "values")  # 獲取項目的資料
        if item_values:
            selected_items.append(item_values)  # 收集資料

# 點擊事件
def on_item_selected(event, tree):
    """當使用者點選項目時，取得該項目的資料"""
    global selected_items
    selected_items = []  # 清空舊選擇
    for item in tree.selection():
        item_values = tree.item(item, "values")
        if item_values:
            selected_items.append(item_values)
    
    if selected_items:
        name, asset_type, path_id, _ = selected_items[-1]
        update_entry(name_entry, name)
        update_entry(path_id_entry, path_id)
        update_entry(type_entry, asset_type)

# 變更右側文字
def update_entry(entry, value):
    entry.config(state="normal")
    entry.delete("1.0", tk.END)
    entry.insert("1.0", value)
    entry.config(state="disabled")
        

# 匯出項目
def export_raw(lang):
    # print(selected_items)
    if not selected_items:
        print("未選取任何項目")
        list_window.bell()
        return
    output_path = filedialog.askdirectory(title=lang["Pick_Output_Folder"])
    if not output_path:
        return
    
    # 使用列表推導式取得所有 tuple 的第三個項目，即 PathID
    pathID = [item[2] for item in selected_items]

    for obj in env.objects:
        if str(obj.path_id) in pathID:
            data = obj.read()
            path_ID = obj.path_id
            dest = os.path.join(output_path, f'{data.m_Name}_{path_ID}.dat')
            with open(dest, "wb") as f:
                f.write(obj.get_raw_data())
    print("匯出完成")
    show_dialog("提示", "匯出完成！")

# 匯入項目
def import_raw(lang):
    """待實作的導入功能"""
    print("Import Raw 功能尚未實作")

# 匯出圖片
def export_texture(lang):
    # print(selected_items)
    if not selected_items:
        print("未選取任何項目")
        list_window.bell()
        return
    output_path = filedialog.askdirectory(title=lang["Pick_Output_Folder"])
    if not output_path:
        return
    
    # 使用列表推導式取得所有 tuple 的第三個項目，即 PathID
    pathID = [item[2] for item in selected_items]

    for obj in env.objects:
        if str(obj.path_id) in pathID:
            if obj.type.name.lower() in ["texture2d", "sprite"]:
                data = obj.read()
                img = data.image
                path_ID = obj.path_id
                dest = os.path.join(output_path, f'{data.m_Name}_{path_ID}.png')
                try:
                    img.save(dest)
                except:
                    print
    print("匯出完成")
    show_dialog("提示", "匯出完成！")

# 匯入圖片
def import_texture(lang):
    """待實作的導入功能"""
    print("Import Texture 功能尚未實作")

# 匯出模型
def export_mesh(lang):
    # print(selected_items)
    if not selected_items:
        print("未選取任何項目")
        list_window.bell()
        return
    output_path = filedialog.askdirectory(title=lang["Pick_Output_Folder"])
    if not output_path:
        return
    
    # 使用列表推導式取得所有 tuple 的第三個項目，即 PathID
    pathID = [item[2] for item in selected_items]

    for obj in env.objects:
        if str(obj.path_id) in pathID:
            if obj.type.name == "Mesh":
                data = obj.read()
                path_ID = obj.path_id
                dest = os.path.join(output_path, f'{data.m_Name}_{path_ID}.obj')
                with open(dest, "w") as f:
                    f.write(data.export())
    print("匯出完成")
    show_dialog("提示", "匯出完成！")


def sort_column(tree, col):
    global ascending, current_sort_col
    items = [(tree.set(k, col), k) for k in tree.get_children("")]
    
    reverse_order = False
    if col == current_sort_col:
        ascending = not ascending
    else:
        ascending = True

    reverse_order = not ascending
    current_sort_col = col

    def sort_key(val):
        try:
            return float(val[0]) if col in ["Path ID", "Size"] else val[0].lower()
        except ValueError:
            return val[0].lower()

    items.sort(reverse=reverse_order, key=lambda x: sort_key(x))

    for index, (_, k) in enumerate(items):
        tree.move(k, "", index)

    apply_row_colors(tree)

def show_dialog(title, message):
    """顯示一個簡單的對話框"""
    messagebox.showinfo(title, message)

def on_close():
    global list_window
    if list_window:
        list_window.destroy()
        list_window = None
    if DEBUG:
        root.quit()  # 在調適模式下，關閉 Tk() 主視窗


# 切換為調適模式
# Debug 模式可直接運行該py
DEBUG = False

if DEBUG:
    root = tk.Tk()  # 創建主視窗
    root.withdraw()  # 隱藏主視窗
    file_path = "C:\\Users\\JamesYang\\Downloads\\50120\\50120_telannas_show_raw_h.assetbundle"
    root.after(100, lambda: list_assets_window(file_path))
    root.mainloop()
