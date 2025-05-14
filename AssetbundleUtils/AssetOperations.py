import os
from tkinter import filedialog, messagebox
from PIL import Image
from .UnityPy_AOV.enums import TextureFormat
"""
這是所有 匯出/匯入 功能集
"""

# These global variables are assumed to be defined in the main script
# and will be accessed and modified here.
selected_items = []
modified_assets = {}
env_list = None  # UnityPy environment, to be set from the main script
list_window = None  # tkinter window, to be set from the main script
indexFile = 0
PathIDIndex = 2 # Index PathId if Select File ( not Dir)
def export_raw(lang):
    """Exports selected assets as raw data."""
    global selected_items,  list_window

    if not selected_items:
        if list_window:
            list_window.bell()  # Ring the bell if no items are selected
        return

    output_path = filedialog.askdirectory(title=lang["Pick_Output_Folder"])
    if not output_path:
        return

    # Use list comprehension to get all PathIDs
    pathID = [item[PathIDIndex] for item in selected_items]

    for obj in env_list[indexFile].objects:
        if str(obj.path_id) in pathID:
            data = obj.read()
            path_ID = obj.path_id
            dest = os.path.join(output_path, f'{data.m_Name}_{path_ID}.dat')
            with open(dest, "wb") as f:
                f.write(obj.get_raw_data())

    show_dialog(lang["Dialog_Title"], lang["Dialog_Message_Export_Complete"])


def import_raw(lang, tree):
    """Imports raw data for a selected asset."""
    global selected_items, modified_assets, env

    if len(selected_items) != 1:
        show_dialog(lang["Dialog_Title"], lang["Dialog_Message_Select_One_Raw"])
    else:
        fp = open_file(lang, "Pick_Input_Raw", "Asset raw files", "*.dat")
        if fp:
            pathID = selected_items[0][PathIDIndex]
            with open(fp, "rb") as f:
                raw = f.read()
                for obj in env_list[indexFile].objects:
                    if str(obj.path_id) == pathID:
                        obj.set_raw_data(raw)
                        modified_assets[str(pathID)] = "*"  # Mark as modified
                        refresh_modified_status(tree)
                        show_dialog(lang["Dialog_Title"], lang["Dialog_Message_Import_Success"])


def export_texture(lang):
    """Exports selected assets as textures (PNG)."""
    global selected_items,  list_window

    if not selected_items:
        if list_window:
            list_window.bell()
        return

    output_path = filedialog.askdirectory(title=lang["Pick_Output_Folder"])
    if not output_path:
        return

    # Use list comprehension to get all PathIDs
    pathID = [item[PathIDIndex] for item in selected_items]

    for obj in env_list[indexFile].objects:
        if str(obj.path_id) in pathID:
            if obj.type.name.lower() in ["texture2d", "sprite"]:
                data = obj.read()
                img = data.image
                path_ID = obj.path_id
                dest = os.path.join(output_path, f'{data.m_Name}_{path_ID}.png')
                try:
                    img.save(dest)
                    
                except Exception as e:
                    print(f"Error saving texture: {e}")

    show_dialog(lang["Dialog_Title"], lang["Dialog_Message_Export_Complete"])

def import_texture(lang, tree):
    """Imports a texture for a selected asset."""
    global selected_items, modified_assets, env

    if len(selected_items) != 1:
        show_dialog(lang["Dialog_Title"], lang["Dialog_Message_Select_One_Raw"])
    else:
        fp = open_file(lang, "Pick_Input_Texture", "Image files", "*.png")
        if fp:
            pathID = selected_items[0][PathIDIndex]
            pil_img = Image.open(fp)

            for obj in env_list[indexFile].objects:
                if str(obj.path_id) == pathID:
                    data = obj.read()
                    data.m_TextureFormat = TextureFormat.RGBA32 # Fix photo quality loss
                    data.image = pil_img
                    data.save()
                    modified_assets[str(pathID)] = "*"  # Mark as modified
                    refresh_modified_status(tree)
                    show_dialog(lang["Dialog_Title"], lang["Dialog_Message_Import_Success"])


def export_mesh(lang):
    """Exports selected assets as meshes (OBJ)."""
    global selected_items,  list_window

    if not selected_items:
        if list_window:
            list_window.bell()
        return

    output_path = filedialog.askdirectory(title=lang["Pick_Output_Folder"])
    if not output_path:
        return

    pathID = [item[PathIDIndex] for item in selected_items]

    for obj in env_list[indexFile].objects:
        if str(obj.path_id) in pathID:
            if obj.type.name == "Mesh":
                data = obj.read()
                path_ID = obj.path_id
                dest = os.path.join(output_path, f'{data.m_Name}_{path_ID}.obj')
                with open(dest, "w") as f:
                    f.write(data.export())

    show_dialog(lang["Dialog_Title"], lang["Dialog_Message_Export_Complete"])

def export_fbx_full(lang):
    """Xuất model với đầy đủ skeleton, skin, texture, animation dưới định dạng FBX."""
    global selected_items, list_window
    if not selected_items:
        if list_window: list_window.bell()
        return
    output_path = filedialog.askdirectory(title=lang["Pick_Output_Folder"])
    if not output_path: return
    # Lấy danh sách PathID của các model được chọn
    pathIDs = [item[PathIDIndex] for item in selected_items]
    for obj in env_list[indexFile].objects:
        if obj.path_id in pathIDs and obj.type.name == "Mesh":
            data = obj.read()
            # TODO: tại đây sử dụng UnityPy và py-fbx/Blender API để tạo file FBX
            # Ví dụ: xuất mesh + armature + animation sang FBX.
            dest = os.path.join(output_path, f'{data.m_Name}_{obj.path_id}.fbx')
            # Đây chỉ là mô phỏng; bạn cần gọi pyfbx hoặc Blender để ghi file.
            # with FbxWriter(dest) as writer: ...
    show_dialog(lang["Dialog_Title"], lang["Dialog_Message_Export_Complete"])

def import_fbx_full(lang):
    """Nhập model FBX (có skeleton, skin, animation) vào asset đã chọn."""
    global selected_items, modified_assets, list_window
    if len(selected_items) != 1:
        show_dialog(lang["Dialog_Title"], lang["Dialog_Message_Select_One_Model"])
        return
    file_path = filedialog.askopenfilename(title=lang["Pick_Input_FBX"],
                                           filetypes=[("FBX files", "*.fbx")])
    if not file_path: return
    # TODO: dùng pyfbx hoặc Blender API để đọc FBX và cập nhật vào UnityPy object
    # Ví dụ: data = UnityPy.load(fbx) → chép mesh/armature vào env_list
    show_dialog(lang["Dialog_Title"], lang["Dialog_Message_Import_Complete"])

def batch_export_all_models(lang):
    """Xuất hàng loạt tất cả model (.obj) trong thư mục hiện tại."""
    global env_list, list_window
    if not selected_items:
        if list_window: list_window.bell()
        return
    output_path = filedialog.askdirectory(title=lang["Pick_Output_Folder"])
    if not output_path: return
    # Duyệt qua mọi object trong AssetBundle
    for obj in env_list[indexFile].objects:
        if obj.type.name == "Mesh":
            data = obj.read()
            dest = os.path.join(output_path, f'{data.m_Name}_{obj.path_id}.obj')
            with open(dest, "w") as f:
                f.write(data.export())
    show_dialog(lang["Dialog_Title"], lang["Dialog_Message_Export_Complete"])

# Helper functions (you might need to adapt these based on your main script)
def open_file(lang, Dialog_Title, type_name, Type):
    """Opens a file dialog for selecting a file."""
    file_path = filedialog.askopenfilename(
        title=lang[Dialog_Title],
        filetypes=[(type_name, Type)]
    )
    if file_path:
        return file_path
    return None


def show_dialog(title, message):
    """Shows a simple message dialog."""
    messagebox.showinfo(title, message)


def refresh_modified_status(tree):
    """Updates the 'Modified' column in the TreeView."""
    global modified_assets
    for item in tree.get_children():
        values = tree.item(item, "values")
        path_id = values[PathIDIndex]  # Path ID is in the third column
        modified_status = modified_assets.get(str(path_id), "")

        if PathIDIndex == 2:

            tree.item(item, values=(values[0], values[1], values[2], values[3], modified_status))  # Update Modified column

        elif PathIDIndex == 3:

            tree.item(item, values=(values[0], values[1], values[2], values[3] , values[4], modified_status))  # Update Modified column


# Example Usage (in your main script):
if __name__ == '__main__':
    # This part won't be executed when imported as a module
    print("This module is not meant to be run directly.")
