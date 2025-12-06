import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib  # 日本語表示用ライブラリ
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# 1. ダミーデータの準備（総合科学部らしく、少しずつ重なり合う3分野を用意）
# 0-3: IT・データ系, 4-6: 心理・認知系, 7-9: 文化・文学系
courses = [
    {"title": "プログラミング基礎", "text": "Pythonを用いてデータ分析やアルゴリズムを実装し技術を習得する"},
    {"title": "人工知能概論", "text": "AI、機械学習、ディープラーニングの基礎と社会実装を学ぶ"},
    {"title": "データサイエンス", "text": "統計学と情報科学を用いてビッグデータを解析する手法"},
    {"title": "情報ネットワーク", "text": "インターネットの仕組みと通信プロトコル、セキュリティ"},
    
    {"title": "認知科学", "text": "人間の知覚や記憶、思考のメカニズムを情報処理の観点から探る"},
    {"title": "心理学概論", "text": "心と行動の科学。感情、発達、社会心理学の基礎"},
    {"title": "行動経済学", "text": "人間の心理的なバイアスが経済活動に与える影響を分析する"},
    
    {"title": "日本近代文学", "text": "夏目漱石や芥川龍之介の作品を通じ、近代の精神史を考察する"},
    {"title": "比較文化論", "text": "異なる文化間の接触と変容、グローバル化する社会の課題"},
    {"title": "言語学入門", "text": "言葉の構造や意味、社会における言語の役割を分析する"},
]

# 2. ベクトル化（Sentence-BERTで意味を数値に変換）
print("AIがシラバスを読んでいます...")
model = Sentence