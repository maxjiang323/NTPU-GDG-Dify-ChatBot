import requests
import os
import json

# ==================== 設定區 ====================
# 【可以改這裡】修改以下變數來改變爬蟲行為：

# API 端點
API_URL = 'https://api-carrier.ntpu.edu.tw/strapi'

# 下載基礎 URL
DOWNLOAD_BASE_URL = 'https://cms-carrier.ntpu.edu.tw'

# 下載文件儲存的目錄
DOWNLOAD_DIR = './NTPU_Laws'

# 【可以改這裡】每批抓取的文件數（最大 100）
BATCH_SIZE = 10

# 【可以改這裡】要抓取多少筆文件（改成 float('inf') 表示抓取全部）
# 例如：改成 20 就只抓前 20 筆；改成 float('inf') 就抓全部
TOTAL_LIMIT = 10

# ===============================================

# 建立下載目錄
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# GraphQL 查詢函式
def get_documents(start=0, limit=100):
    """
    向 NTPU API 查詢法規文件
    
    參數：
        start (int): 起始位置（第幾筆開始）
        limit (int): 要取多少筆
    
    回傳：
        list: 文件清單，如果查詢失敗回傳空列表
    """
    # 建立 GraphQL 查詢語句
    graphql_query = {
        "query": f"""{{
            documents(
                sort: "createdAt:desc"
                start: {start}
                limit: {limit}
                where: {{
                    lang: "zh"
                    tags_contains: "法規"
                }}
            ) {{
                _id
                createdAt
                name
                tags
                lang
                site
                file {{
                    url
                    name
                    mime
                }}
            }}
        }}"""
    }
    
    # 發送 POST 請求
    response = requests.post(API_URL, json=graphql_query)
    
    # 檢查回應是否成功
    if response.status_code == 200:
        return response.json().get('data', {}).get('documents', [])
    else:
        print(f"查詢失敗，狀態碼：{response.status_code}")
        return []

# 下載前 N 個文件
def download_all_documents():
    """
    下載指定數量的文件
    會根據 TOTAL_LIMIT 變數決定要下載多少筆
    """
    total_documents = 0
    batch_num = 0
    
    # 持續循環直到達到下載限制或沒有更多文件
    while total_documents < TOTAL_LIMIT:
        # 計算這一批的起始位置
        start = batch_num * BATCH_SIZE
        
        print(f"\n正在抓取第 {batch_num + 1} 批次 (start={start}, limit={BATCH_SIZE})...")
        
        # 調用 API 查詢文件
        documents = get_documents(start=start, limit=BATCH_SIZE)
        
        # 如果沒有取到任何文件，表示已到達結尾
        if not documents:
            print("沒有更多文件了")
            break
        
        # 遍歷每個文件進行下載
        for doc in documents:
            # 檢查是否達到下載限制
            if total_documents >= TOTAL_LIMIT:
                break
            
            # 取得文件資訊
            file_info = doc.get('file')
            if not file_info:
                continue
            
            # 組合完整的下載 URL
            file_url = DOWNLOAD_BASE_URL + file_info['url']
            # 取得文件名稱
            file_name = file_info['name']
            # 組合本地儲存路徑
            file_path = os.path.join(DOWNLOAD_DIR, file_name)
            
            try:
                # 列印下載進度
                print(f"下載中: {file_name}...", end=" ")
                
                # 發送 GET 請求下載檔案
                pdf_response = requests.get(file_url)
                
                # 檢查下載是否成功
                if pdf_response.status_code == 200:
                    # 將檔案寫入本地
                    with open(file_path, 'wb') as f:
                        f.write(pdf_response.content)
                    print("✓ 成功")
                    total_documents += 1
                else:
                    print(f"✗ 失敗 (狀態碼: {pdf_response.status_code})")
            except Exception as e:
                # 捕捉任何錯誤並顯示
                print(f"✗ 錯誤: {e}")
        
        # 準備下一批
        batch_num += 1
    
    # 顯示最終結果
    print(f"\n完成！總共下載 {total_documents} 個文件")

if __name__ == "__main__":
    download_all_documents()
    