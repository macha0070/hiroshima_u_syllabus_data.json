# Hiroshima University Syllabus Search / 広島大学シラバス検索

This project provides a client-side search engine for Hiroshima University syllabus data using TF-IDF vectorization.  
本プロジェクトは、TF-IDFベクトル化を用いた広島大学シラバスデータのクライアントサイド検索エンジンを提供します。

## 📂 Data & Files / ファイル構成

- **`subject_details_main_2025-04-03.json`**  
  Raw syllabus data (scraper output).  
  スクレイピングされた生のシラバスデータです。

- **`preprocess001.py`**  
  **Data Processing Script**. It reads the raw JSON, performs morphological analysis (Janome), converts text to TF-IDF vectors, and saves the result with a vocabulary index.  
  **データ処理スクリプト**。生のJSONを読み込み、形態素解析（Janome）を行い、TF-IDFベクトルに変換して、辞書インデックスと共に保存します。

- **`syllabus_vectors.json`**  
  **Generated Data**. Contains the word vocabulary and a list of courses with their vector representations. This is used by the frontend.  
  **生成データ**。単語辞書と、各コースのベクトル表現を含むリストです。フロントエンドで使用されます。

- **`demo001.html`**  
  **Search Demo**. A modern, single-page search application. It loads `syllabus_vectors.json` and performs cosine similarity search entirely in the browser using JavaScript and `Intl.Segmenter`.  
  **検索デモ**。モダンなシングルページの検索アプリです。`syllabus_vectors.json` を読み込み、JavaScriptと `Intl.Segmenter` を使用してブラウザ内で完結するコサイン類似度検索を行います。

## 🚀 How to Run / 実行方法

### 1. Prerequisites / 前提条件
You need Python installed.  
Pythonがインストールされている必要があります。

```bash
pip install janome scikit-learn
```

### 2. Generate Vectors / ベクトルの生成
Run the preprocessing script to create the vector file.  
前処理スクリプトを実行して、ベクトルファイルを作成します。

```bash
python preprocess001.py
```
*Output: `syllabus_vectors.json`*

### 3. Start Search / 検索の開始
Simply open **`demo001.html`** in a modern web browser (Edge, Chrome, Safari).  
モダンなWebブラウザ（Edge, Chrome, Safari）で **`demo001.html`** を開くだけです。

**Note:** Since this uses `fetch()` to load the JSON file, you might need a local server due to browser CORS policies if it doesn't work by just double-clicking.  
**注意:** JSONファイルを `fetch()` で読み込むため、ダブルクリックで動かない場合はブラウザのCORSポリシーによりローカルサーバーが必要になる場合があります。

```bash
# Example: Start a simple server
python -m http.server
# Then access http://localhost:8000/demo001.html
```

## 🛠 Technology / 技術スタック

- **Backend (Preprocessing)**: Python, Janome (Tokenizer), Scikit-learn (TF-IDF)
- **Frontend**: HTML5, CSS3 (Modern UI), JavaScript (No frameworks)
- **Search Logic**: 
  - **Client-Side Tokenization**: `Intl.Segmenter` (Built-in browser API for Japanese text)
  - **Vector Search**: Cosine Similarity between user query vector and 10,000+ course vectors.

---
*Created by Antigravity Assistant*