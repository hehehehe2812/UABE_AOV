from PIL import Image

"""
這是所有 檢視資產 邏輯集
"""

# These global variables are assumed to be defined in the main script
# and will be accessed and modified here.
env_list= None  # UnityPy environment, to be set from the main script
indexFile = 0
# 檢視 assets
def preview_assets(path_id):
    global env_list  , indexFile
    for obj in env_list[indexFile].objects:
        if str(obj.path_id) == path_id:
            data = obj.read()
            if obj.type.name.lower() in ["texture2d", "sprite"]:
                return data.image  # 回傳影像
            elif obj.type.name.lower() == "mesh":
                return data.export()  # 回傳 .obj 格式
    return None


def resize_image(image, max_width=230):
    width, height = image.size
    scale = min(max_width / width, max_width / height)
    new_size = (int(width * scale), int(height * scale))
    return image.resize(new_size, Image.Resampling.LANCZOS)
