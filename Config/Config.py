import json
import os
import sys

def get_resource_path(filename):
    """
    獲取檔案的實際路徑，適用於開發環境和 PyInstaller 打包後的 EXE。
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)  # PyInstaller 內部打包後的路徑
    return os.path.abspath(filename)  # 開發環境直接返回絕對路徑


# 讀取設定
def load_settings():
    settings_path = get_resource_path("Settings.json")
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
                return settings.get("Language", "zh-tw")  # 預設語言 zh-tw
        except json.JSONDecodeError:
            print("Settings.json 格式錯誤，使用預設值。")
    return "zh-tw"

# 讀取語言包
def load_language(lang_code):
    lang_path = get_resource_path("lang.json")
    if os.path.exists(lang_path):
        try:
            with open(lang_path, "r", encoding="utf-8") as f:
                lang_data = json.load(f)
                return lang_data.get(lang_code, lang_data.get("zh-tw", {}))  # 預設 zh-tw
        except json.JSONDecodeError:
            print("lang.json 格式錯誤，使用空字典。")
    return {}

# 變更語言設置
def setting_languages(new_lang_code):
    settings_path = get_resource_path("Settings.json")
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
            settings["Language"] = new_lang_code  # 更新語言設定
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)  # 寫入 JSON
        except json.JSONDecodeError:
            print("Settings.json 格式錯誤，無法變更語言。")

# 重新載入設定
def reload_config():
    lang_code = load_settings()
    lang = load_language(lang_code)
    return lang, lang_code
