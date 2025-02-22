import json, os


# 讀取設定
def load_settings():
    if os.path.exists("Settings.json"):
        with open("Settings.json", "r", encoding="utf-8") as f:
            settings = json.load(f)
            return settings.get("Language", "zh-tw")  # 預設語言 zh-tw
    return "zh-tw"

# 讀取語言包
def load_language(lang_code):
    if os.path.exists("lang.json"):
        with open("lang.json", "r", encoding="utf-8") as f:
            lang_data = json.load(f)
            return lang_data.get(lang_code, lang_data["zh-tw"])  # 預設 zh-tw
    return {}

# 變更語言設置
def setting_languages(new_lang_code):
    if os.path.exists("Settings.json"):
        with open("Settings.json", "r", encoding="utf-8") as f:
            settings = json.load(f)
        settings["Language"] = new_lang_code  # 更新語言設定
        with open("Settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)  # 寫入 JSON

# 重新載入設定
def reload_config():
    lang_code = load_settings()
    lang = load_language(lang_code)
    return lang, lang_code
