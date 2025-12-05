import requests
from bs4 import BeautifulSoup
import json
import time
import re

# ==========================================
# 設定セクション
# ==========================================

# ベースとなるURL（共通部分）
# 例: https://momiji.hiroshima-u.ac.jp/syllabusHtml/2025_0101_AKY01001.html
# の場合、プレフィックスは "2025_0101_" となります。
# ※中間の "0101" や "13" などは学部や学期によって変わる可能性があります。
BASE_URL_TEMPLATE = "https://momiji.hiroshima-u.ac.jp/syllabusHtml/2025_0101_{}.html"

# スクレイピング結果の保存先
OUTPUT_FILE = "hiroshima_u_syllabus_data.json"

# 生成する科目コードの範囲設定
# 例: AKY01001 〜 AKY01020 までを探索する場合
CODE_PREFIX = "ADO"  # コードの頭文字
START_NUM = 1001     # 開始番号
END_NUM = 1010       # 終了番号（テスト用に小さくしています。必要に応じて増やしてください）


# 関数定義

def get_target_codes(prefix, start, end):
    """探索する科目コードのリストを生成する"""
    codes = []
    for i in range(start, end + 1):
        # 5桁埋め (例: 1 -> 00001, 1001 -> 01001) ※桁数は実際のルールに合わせて調整してください
        # ユーザー例の "AKY01001" は3文字+5桁と仮定します
        code = f"{prefix}{i:05d}"
        codes.append(code)
    return codes

def extract_syllabus_info(html_content, url):
    """HTMLから必要な情報を抽出する"""
    soup = BeautifulSoup(html_content, "html.parser")
    data = {
        "url": url,
        "course_name": "",      # 授業名
        "schedule": "",         # 授業計画
        "textbooks": "",        # 教科書・参考書
        "advice": ""            # 予習・復習へのアドバイス
    }

    # 授業名の取得（h1タグや特定のクラスなど、実際のHTMLに合わせて調整）
    # 多くの場合、タイトルやテーブルの一番上にあります
    try:
        # 例: <span class="course_name">...</span> などの場合
        # ここでは汎用的にタイトルタグから取得する例
        title_tag = soup.find("title")
        if title_tag:
             data["course_name"] = title_tag.text.strip()
    except:
        pass

    # テーブルの行(tr)を走査して対象の項目を探す
    rows = soup.find_all("tr")
    for row in rows:
        header = row.find(["th", "td"]) # 左側の項目名セル
        content = row.find("td")        # 右側の内容セル
        
        # contentがNoneの場合はスキップ（ヘッダーだけの行など）
        # また、headerとcontentが同じ要素の場合もスキップ
        if not header or not content or header == content:
            # thとtdが分かれている構造を想定して補正
            cells = row.find_all("td")
            if len(cells) >= 2:
                header = row.find("th") if row.find("th") else cells[0]
                content = cells[-1]
            else:
                continue

        header_text = header.get_text(strip=True)
        # 改行を残したい場合は get_text("\n", strip=True) を使用
        content_text = content.get_text("\n", strip=True)

        # キーワード判定（表記ゆれに対応するため部分一致）
        if "授業計画" in header_text:
            data["schedule"] = content_text
        elif "教科書" in header_text or "参考書" in header_text:
            data["textbooks"] = content_text
        elif "予習" in header_text and "復習" in header_text: # "予習・復習へのアドバイス"
            data["advice"] = content_text

    return data

def main():
    target_codes = get_target_codes(CODE_PREFIX, START_NUM, END_NUM)
    results = []
    
    print(f"探索開始: {len(target_codes)} 件のコードをチェックします...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for code in target_codes:
        url = BASE_URL_TEMPLATE.format(code)
        
        try:
            # 1. ページへのアクセス
            response = requests.get(url, headers=headers, timeout=10)
            
            # 2. ステータスコードのチェック
            if response.status_code == 404:
                print(f"[SKIP] 404 Not Found: {code}")
                # 存在しない場合は即座に次へ（負荷軽減のため短いsleepは入れる）
                time.sleep(0.5) 
                continue
            
            elif response.status_code == 200:
                print(f"[FOUND] データ抽出中...: {code}")
                response.encoding = response.apparent_encoding # 文字化け対策
                
                # 3. データ抽出
                extracted_data = extract_syllabus_info(response.text, url)
                # 科目コードもデータに追加
                extracted_data["code"] = code
                results.append(extracted_data)
                
                # 成功時はサーバーに優しく待機時間を長めに
                time.sleep(1.0)
                
            else:
                print(f"[ERROR] Status {response.status_code}: {url}")
                time.sleep(1.0)

        except Exception as e:
            print(f"[EXCEPTION] {code}: {e}")
            time.sleep(1.0)

    # 4. JSONへの保存
    if results:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print(f"\n完了！ {len(results)} 件のデータを {OUTPUT_FILE} に保存しました。")
    else:
        print("\n有効なデータが見つかりませんでした。URLパターンやコード範囲を確認してください。")

if __name__ == "__main__":
    main()