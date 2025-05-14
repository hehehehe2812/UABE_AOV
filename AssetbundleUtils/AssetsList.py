import tkinter as tk
from tkinter import ttk, Toplevel
from PIL import ImageTk
import os
from UI.CenterWindows import center_window
from Config import Config  # 引入 Config 模組
import AssetbundleUtils.PreviewAsset
import AssetbundleUtils.AssetOperations
from AssetbundleUtils.OBJ_Viewer import OBJViewer
from AssetbundleUtils import UnityPy_AOV


list_window = None  # 避免重複開啟視窗
global current_sort_col, ascending, small_hint_text_label
env_list = []  # 全域變數儲存 UnityPy 環境
current_sort_col = "Name"
ascending = True
selected_items = []  # 用於記錄使用者選取的項目
modified_assets = {}  # 用來記錄已修改的項目
isDir = False
indexFile = 0
list_path = []

def list_assets_window(input_path , IsInputDir = False):
    global list_window,name_file_entry, name_entry, path_id_entry, type_entry, env, preview_label, obj_viewer , isDir, small_hint_text_label
    isDir = IsInputDir
    if list_window and list_window.winfo_exists():
        list_window.lift()
        return
    
    lang, lang_code = Config.reload_config()

    list_window = Toplevel()  # 正常運行時使用 Toplevel()
    list_window.grab_set()
    list_window.transient()
    list_window.minsize(width=1000, height=600)  # 設定最小尺寸
    #list_window.attributes('-topmost', True)

    list_window.title(lang["List_Window_title"])
    list_window.geometry("1200x600")
    list_window.iconbitmap("icon.ico")

    frame = tk.Frame(list_window)
    frame.pack(fill=tk.BOTH, expand=True)

    columns = [ "Name", "Type", "Path ID", "Size", "Modified"]
    column_widths = {"Name": 250, "Type": 130, "Path ID": 170, "Size": 60, "Modified": 70}

    if isDir:
        columns.insert(0,"File")
        column_widths["File"] = 10

    tree = ttk.Treeview(frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col, command=lambda c=col: sort_column(tree, c))
        tree.column(col, anchor="w", width=column_widths[col])
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.LEFT, fill=tk.Y)

    info_frame = tk.Frame(frame, width=290, bg="#F0F0F0")
    info_frame.pack(side=tk.RIGHT, fill=tk.Y)

    # 2分頁
    notebook = ttk.Notebook(info_frame)
    notebook.pack(fill=tk.BOTH, expand=True)

    info_tab = tk.Frame(notebook, bg="#F0F0F0")
    preview_tab = tk.Frame(notebook, bg="#F0F0F0")  # 預覽頁面
    notebook.add(info_tab, text=lang["Info_tab"])
    notebook.add(preview_tab, text=lang["Preview_tab"])

    # 新增標籤與輸入框
    def create_label_entry(parent, label_text):
        tk.Label(parent, text=label_text, font=("Microsoft JhengHei", 10)).pack(anchor="w", padx=20, pady=(10, 0))
        entry = tk.Text(parent, height=1, width=27, state="disabled", wrap="none", font=("Microsoft JhengHei", 10))
        entry.pack(padx=20, pady=5)
        return entry

    name_file_entry = create_label_entry(info_tab, lang["File_Name"])
    name_entry = create_label_entry(info_tab, lang["Name"])
    path_id_entry = create_label_entry(info_tab, lang["PathID"])
    type_entry = create_label_entry(info_tab, lang["Type"])


    preview_label = tk.Label(preview_tab, font=("Microsoft JhengHei", 17), bg="#F0F0F0")
    obj_viewer = OBJViewer(preview_tab)
    # 讓兩個元件都置中
    obj_viewer.config(width=1, height=1)  # 初始化時縮到極小，避免影響 UI
    preview_label.place(relx=0.5, rely=0.5, anchor="center")
    obj_viewer.place(relx=0.5, rely=0.5, anchor="center")

    # OBJ Viewer Hint

    hint_text = lang["OBJ_Viewer_Hint"]

    small_hint_text_label = tk.Label(
        preview_tab,
        text=hint_text,
        font=("Microsoft JhengHei", 10),  # 字體小一點
        bg="#F0F0F0",
        justify="left"
    )

    # 第一排按鈕
    btn_frame = tk.Frame(info_tab, bg="#F0F0F0")
    btn_frame.pack(fill="x", pady=5, padx=20)
    
    export_raw_btn = tk.Button(btn_frame, text=lang["Export_Raw"], command=lambda: AssetbundleUtils.AssetOperations.export_raw(lang))
    import_raw_btn = tk.Button(btn_frame, text=lang["Import_Raw"], command=lambda: AssetbundleUtils.AssetOperations.import_raw(lang, tree))
    
    export_raw_btn.grid(row=0, column=0, sticky="ew", padx=5)
    import_raw_btn.grid(row=0, column=1, sticky="ew", padx=5)
    
    btn_frame.columnconfigure(0, weight=1)
    btn_frame.columnconfigure(1, weight=1)
    
    # 第二排按鈕
    btn_frame2 = tk.Frame(info_tab, bg="#F0F0F0")
    btn_frame2.pack(fill="x", pady=5, padx=20)
    
    export_texture_btn = tk.Button(btn_frame2, text=lang["Export_Texture"], command=lambda: AssetbundleUtils.AssetOperations.export_texture(lang))
    import_texture_btn = tk.Button(btn_frame2, text=lang["Import_Texture"], command=lambda: AssetbundleUtils.AssetOperations.import_texture(lang, tree))
    
    export_texture_btn.grid(row=0, column=0, sticky="ew", padx=5)
    import_texture_btn.grid(row=0, column=1, sticky="ew", padx=5)
    
    btn_frame2.columnconfigure(0, weight=1)
    btn_frame2.columnconfigure(1, weight=1)

    # 新增一個與兩個按鈕 + 間隔等寬的按鈕
    btn_frame3 = tk.Frame(info_tab, bg="#F0F0F0")
    btn_frame3.pack(fill="x", pady=5, padx=20)
    
    export_mesh_btn = tk.Button(btn_frame3, text=lang["Export_Mesh"], command=lambda: AssetbundleUtils.AssetOperations.export_mesh(lang))
    export_mesh_btn.pack(fill="x", padx=5)  # 讓按鈕完全填滿

    # Khung chứa các nút FBX
btn_frame_fbx = tk.Frame(info_tab, bg="#F0F0F0")
btn_frame_fbx.pack(fill="x", pady=5, padx=20)
export_fbx_btn = tk.Button(btn_frame_fbx, text=lang["Export_FBX"],
                           command=lambda: AssetbundleUtils.AssetOperations.export_fbx_full(lang))
export_fbx_btn.pack(fill="x", padx=5)
import_fbx_btn = tk.Button(btn_frame_fbx, text=lang["Import_FBX"],
                           command=lambda: AssetbundleUtils.AssetOperations.import_fbx_full(lang))
import_fbx_btn.pack(fill="x", padx=5)

# Khung chứa nút Batch Export
btn_frame_batch = tk.Frame(info_tab, bg="#F0F0F0")
btn_frame_batch.pack(fill="x", pady=5, padx=20)
batch_export_btn = tk.Button(btn_frame_batch, text=lang["Batch_Export_All_Models"],
                             command=lambda: AssetbundleUtils.AssetOperations.batch_export_all_models(lang))
batch_export_btn.pack(fill="x", padx=5)

    
    # 增加間距
    tk.Frame(info_tab, height=10, bg="#F0F0F0").pack(fill="x") 

    # 保存退出按鈕
    btn_frame4 = tk.Frame(info_tab, bg="#F0F0F0")
    btn_frame4.pack(fill="x", pady=10, padx=20)  # 增加 pady 讓距離更遠
    
    save_btn = tk.Button(btn_frame4, text=lang["Save"], command=lambda: save_and_exit())
    save_btn.pack(fill="x", padx=5)

    progress_var = tk.IntVar()
    progress_bar = ttk.Progressbar(list_window, variable=progress_var, maximum=100, mode='determinate')
    progress_bar.pack(fill=tk.X)

    # 綁定 Tab 分頁切換事件
    notebook.bind("<<NotebookTabChanged>>", on_tab_selected)

    # 綁定 Ctrl + A 鍵盤事件
    tree.bind('<Control-a>', lambda event, t=tree: select_all(t))
    tree.bind("<ButtonRelease-1>", lambda event, t=tree: on_item_selected(lang, t, notebook))  # 綁定點擊事件

    list_window.protocol("WM_DELETE_WINDOW", on_close)
    list_window.update()
    center_window(list_window, 0)

    list_window.after(100, lambda: list_assets(input_path, tree, progress_var, progress_bar))

def list_assets(input_path, tree, progress_var, progress_bar):
    global env_list , list_path
    list_path = [ os.path.join(input_path, file_name) for file_name in os.listdir(input_path) if os.path.isfile(os.path.join(input_path, file_name) ) and "assetbundle" in file_name.lower()] if isDir  else [ input_path ] 
    assets = []
    env_list = []
    for j , path in enumerate(list_path, 0):
        env = UnityPy_AOV.load(path)
        total = 0
        total= len(env.objects)
        env_list.append(env)
        for i, obj in enumerate(env.objects, 1):
            # dump_tree = obj.read_typetree()
            data = obj.read()
            name = getattr(data, 'm_Name', 'Unnamed asset') or "SpringNode"
            if isDir:
                assets.append((j , name, obj.type.name, obj.path_id, obj.byte_size))
            else:
                assets.append((name, obj.type.name, obj.path_id, obj.byte_size))
            progress_var.set(int((i / total) * 100))
            tree.update_idletasks()

    # 更新 AssetOperations 中的 env
    AssetbundleUtils.AssetOperations.env_list = env_list
    AssetbundleUtils.AssetOperations.list_window = list_window
    # 更新 PreviewAsset 中的 env
    AssetbundleUtils.PreviewAsset.env_list = env_list
    AssetbundleUtils.AssetOperations.PathIDIndex = 3 if isDir else 2
    
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

# 避免切至 Info 點選Mesh 切回 Preview 沒顯示成功
def on_tab_selected(event):
    selected_tab = event.widget.index(event.widget.select())
    if selected_tab == 1:  # 1 表示 Preview 分頁
        if selected_items and selected_items[-1][1].lower() == "mesh":
            obj_viewer.config(width=230, height=230)  # 顯示 obj_viewer
            obj_viewer.place(relx=0.5, rely=0.5, anchor="center")
            preview_label.config(text="")  # 讓 preview_label 不占空間
        else:
            obj_viewer.config(width=1, height=1)  # 縮小 obj_viewer 避免錯誤
            preview_label.place(relx=0.5, rely=0.5, anchor="center")  # 顯示 preview_label

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

    # 在這裡更新 AssetOperations 中的 selected_items
    AssetbundleUtils.AssetOperations.selected_items = selected_items

# 點擊事件
def on_item_selected(lang, tree, notebook):
    """當使用者點選項目時，取得該項目的資料"""
    global selected_items, preview_label, obj_viewer
    selected_items = []  # 清空舊選擇
    for item in tree.selection():
        item_values = tree.item(item, "values")
        if item_values:
            selected_items.append(item_values)
    
    # 在這裡更新 AssetOperations 中的 selected_items
    AssetbundleUtils.AssetOperations.selected_items = selected_items

    if selected_items:
        if isDir:
            i , name, asset_type, path_id, *_= selected_items[-1]
            i = int(i)
        else:
            name, asset_type, path_id, *_ = selected_items[-1]
            i = 0
        
        AssetbundleUtils.AssetOperations.indexFile = i
        AssetbundleUtils.PreviewAsset.indexFile = i
        update_entry(name_file_entry, os.path.basename( list_path[i] ))
        update_entry(name_entry , name)
        update_entry(path_id_entry, path_id)
        update_entry(type_entry, asset_type)

        if asset_type.lower() in ["texture2d", "sprite"]:
            image = AssetbundleUtils.PreviewAsset.preview_assets(path_id)
            if image:
                image = AssetbundleUtils.PreviewAsset.resize_image(image)
                img = ImageTk.PhotoImage(image)
                preview_label.config(image=img)
                preview_label.image = img
                obj_viewer.config(width=1, height=1)  # 縮到極小，避免未初始化而報錯
                preview_label.place(relx=0.5, rely=0.5, anchor="center")  # 置中顯示
                small_hint_text_label.place_forget()  # 隱藏提示文字
            else:
                preview_label.config(image="", text=lang["Preview_not_available"])
                obj_viewer.config(width=1, height=1)  # 縮到極小，避免未初始化而報錯
                small_hint_text_label.place_forget()  # 隱藏提示文字
        elif asset_type.lower() == "mesh":
            obj_data = AssetbundleUtils.PreviewAsset.preview_assets(path_id)
            if notebook.index(notebook.select()) == 1:  # Preview 分頁索引
                if obj_data:
                    small_hint_text_label.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-10)  # 顯示提示文字 # 左下角
                    obj_viewer.config(width=230, height=230)  # 確保大小正常
                    obj_viewer.pack(expand=True)
                    obj_viewer.load_obj_data(obj_data)
                    preview_label.pack_forget()
                else:
                    preview_label.config(image="", text=lang["Preview_not_available"])
                    obj_viewer.config(width=1, height=1)  # 縮到極小，避免未初始化而報錯
                    small_hint_text_label.place_forget()  # 隱藏提示文字

        else:
            preview_label.config(image="", text=lang["Preview_not_available"])
            obj_viewer.config(width=1, height=1)  # 縮到極小，避免未初始化而報錯
            preview_label.place(relx=0.5, rely=0.5, anchor="center")  # 置中顯示
            small_hint_text_label.place_forget()  # 隱藏提示文字

    else:
        # 如果沒有選擇項目，也要更新 AssetOperations 中的 selected_items
        AssetbundleUtils.AssetOperations.selected_items = selected_items

# 變更右側文字
def update_entry(entry, value):
    entry.config(state="normal")
    entry.delete("1.0", tk.END)
    entry.insert("1.0", value)
    entry.config(state="disabled")

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

def on_close():
    global list_window, selected_items
    selected_items = []  # 清空舊選擇
    
    if list_window:
        list_window.destroy()
        list_window = None

def save_and_exit():
    global list_window
    os.makedirs("./AssetbundleUtils/tmp",exist_ok=True)
    for i , path in enumerate(list_path, 0):
        name = os.path.basename( list_path[i] )
        env = env_list[i]
        with open(f"./AssetbundleUtils/tmp/{name}", "wb") as f:
            f.write(env.file.save("lz4"))
    if list_window:
        list_window.destroy()
        list_window = None


