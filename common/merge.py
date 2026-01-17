import json
import glob
import os

# ==========================================
# 設定
# ==========================================

# 読み込むファイルのパターン
# "*" はワイルドカードです。「syllabus_」で始まり「.json」で終わる全ファイルを対象にします
# 例: syllabus_science.json, syllabus_law.json など
INPUT_PATTERN = "syllabus_*.json" 

# 出力するファイル名
OUTPUT_FILE = "all_syllabus_merged.json"

# ==========================================
# マージ処理
# ==========================================

def main():
    merged_data = []
    
    # 指定したパターンのファイル一覧を取得
    files = glob.glob(INPUT_PATTERN)
    
    if not files:
        print(f"パターン '{INPUT_PATTERN}' に一致するファイルが見つかりませんでした。")
        return

    print(f"マージ対象ファイル: {len(files)} 件")

    for file_path in files:
        # 出力ファイル自身が読み込み対象に含まれていたらスキップする（無限増殖防止）
        if os.path.basename(file_path) == OUTPUT_FILE:
            continue
            
        print(f"読み込み中: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # データがリスト（配列）であることを確認して追加
                if isinstance(data, list):
                    merged_data.extend(data)
                else:
                    print(f"警告: {file_path} の中身がリスト形式ではありません。スキップします。")
                    
        except json.JSONDecodeError:
            print(f"エラー: {file_path} はJSONとして読み込めませんでした。")
        except Exception as e:
            print(f"エラー: {file_path} の処理中に問題が発生しました: {e}")

    # 保存処理
    print(f"書き込み中... 総データ数: {len(merged_data)} 件")
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=4)
        print(f"完了！ '{OUTPUT_FILE}' に保存されました。")
    except Exception as e:
        print(f"保存エラー: {e}")

if __name__ == "__main__":
    main()