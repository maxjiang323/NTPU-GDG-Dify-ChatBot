import requests
import os
import json
import time
from dotenv import load_dotenv
from pathlib import Path

# ================================
# 🔑 各知識庫環境變數設定
# ================================
load_dotenv()

DATASETS = {
    "school_admin": {
        "api_key": os.getenv("DIFY_API_KEY_SCHOOL_ADMIN"),
        "dataset_id": os.getenv("DIFY_DATASET_ID_SCHOOL_ADMIN")
    },
    "college_rules": {
        "api_key": os.getenv("DIFY_API_KEY_COLLEGE_RULES"),
        "dataset_id": os.getenv("DIFY_DATASET_ID_COLLEGE_RULES")
    },
    "phd_process": {
        "api_key": os.getenv("DIFY_API_KEY_PHD_PROCESS"),
        "dataset_id": os.getenv("DIFY_DATASET_ID_PHD_PROCESS")
    },
    "scholarship": {
        "api_key": os.getenv("DIFY_API_KEY_SCHOLARSHIP"),
        "dataset_id": os.getenv("DIFY_DATASET_ID_SCHOLARSHIP")
    },
    "research_admin": {
        "api_key": os.getenv("DIFY_API_KEY_RESEARCH_ADMIN"),
        "dataset_id": os.getenv("DIFY_DATASET_ID_RESEARCH_ADMIN")
    }
}

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ================================
# 📂 上傳資料夾，替換成要上傳的資料夾
# ================================
folder = Path(r"C:\Users\Max\Downloads\NTPU_Laws")


# ================================
# 📦 Dify 文件處理規則（改良版）
# ================================
process_rule = {
    "mode": "hierarchical",
    "rules": {
        "pre_processing_rules": [
            {"id": "remove_extra_spaces", "enabled": True},
            {"id": "remove_urls_emails", "enabled": True},
            {"id": "normalize_whitespace", "enabled": True}
        ],
        "segmentation": {
            "separator": "\n\n",
            "max_tokens": 600,
            "overlap_tokens": 50
        },
        "subchunk_segmentation": {
            "separator": "\n",
            "max_tokens": 256,
            "overlap_tokens": 20
        },
        "parent_mode": "paragraph"
    }
}

payload_dict = {
    "indexing_technique": "high_quality",
    "process_rule": process_rule,
    "doc_form": "hierarchical_model"
}


# ================================
# 🧠 Gemini 分類器（改良版）
# ================================
def classify_with_gemini(filename, file_path=None):

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash-lite:generateContent?key={GOOGLE_API_KEY}"

    # 讀取檔案前 2000 字
    head_text = ""

    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                head_text = f.read(2000)
        except:
            head_text = ""

    prompt = f"""
你是文件分類器。
請判斷此文件屬於哪一類，只回答英文代碼：

school_admin
college_rules
phd_process
scholarship
research_admin

檔名:
{filename}

文件開頭內容:
{head_text}
"""

    body = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(url, json=body)
    result = response.json()

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"].strip()

        valid = [
            "school_admin",
            "college_rules",
            "phd_process",
            "scholarship",
            "research_admin"
        ]

        if text in valid:
            return text

        return "school_admin"

    except:
        return "school_admin"


# ================================
# 📌 規則分類
# ================================
def rule_based_classify(filename):

    name = filename.lower()

    if "博士" in filename or "論文" in filename or "口試" in filename:
        return "phd_process"

    if "獎學金" in filename or "補助" in filename:
        return "scholarship"

    if "國科會" in filename or "研究" in filename or "產學" in filename:
        return "research_admin"

    if "學院" in filename or "系" in filename:
        return "college_rules"

    if "辦法" in filename or "要點" in filename or "管理" in filename:
        return "school_admin"

    return None


# ================================
# 🚀 上傳流程
# ================================
for file_path in folder.iterdir():

    if not file_path.is_file():
        continue

    filename = file_path.name

    print(f"\nProcessing: {filename}")

    # 1️⃣ 規則分類
    category = rule_based_classify(filename)

    # 2️⃣ 若規則無法判斷 → Gemini
    if category is None:
        print("Rule unclear → Using Gemini...")
        category = classify_with_gemini(filename, file_path)

    print(f"Final Category: {category}")

    dataset_info = DATASETS.get(category)

    if dataset_info is None:
        print("Unknown category. Skip.")
        continue

    api_key = dataset_info["api_key"]
    dataset_id = dataset_info["dataset_id"]

    if not api_key or not dataset_id:
        print("Missing env variable. Skip.")
        continue

    url = f"http://localhost/v1/datasets/{dataset_id}/document/create-by-file"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    with open(file_path, "rb") as f:

        files = {
            "file": (filename, f)
        }

        payload = {
            "data": json.dumps(payload_dict)
        }

        resp = requests.post(
            url,
            data=payload,
            files=files,
            headers=headers
        )

    print(resp.status_code)
    print(resp.text)

    time.sleep(3)