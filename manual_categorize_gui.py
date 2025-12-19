"""
manual_categorize_gui.py
========================
Tkinterを使用したGUIツールです。
マウス操作で「総合科学部」の授業に領域・分野タグを付与できます。

機能:
- `integrated_arts_courses.json` を読み込みます
- 1件ずつ授業を表示します
- ボタンをクリックしてカテゴリ（領域・分野）を選択します
- 自動的に JSON ファイルを上書き保存します
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

FILE_PATH = "integrated_arts_courses.json"

# カテゴリ定義
CATEGORIES = {
    "総合科学部共通科目": ["人間科学分野", "自然科学分野", "社会科学分野"],
    "人間探究領域": ["人間文化", "言語コミュニケーション", "人間行動科学", "スポーツ健康科学"],
    "自然探求領域": ["生命科学", "数理情報科学", "物性科学", "自然環境科学"],
    "社会探究領域": ["地域研究", "越境文化", "現代社会システム"],
    "その他": ["専門外国語科目", "学際科目", "特別科目", "その他"]
}

class LabelingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Syllabus Categorizer")
        self.root.geometry("800x700")

        self.data = {}
        self.course_ids = []
        self.current_index = 0
        
        self.load_data()
        self.setup_ui()
        self.show_current_course()

    def load_data(self):
        if not os.path.exists(FILE_PATH):
            messagebox.showerror("Error", f"{FILE_PATH} not found!")
            self.root.destroy()
            return
        
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.course_ids = list(self.data.keys())
        print(f"Loaded {len(self.course_ids)} courses.")

    def save_data(self):
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print("Progress saved.")

    def setup_ui(self):
        # Header Info
        info_frame1 = ttk.Frame(self.root, padding=10)
        info_frame1.pack(fill=tk.X)
        
        self.lbl_progress = ttk.Label(info_frame1, text="0 / 0", font=("Arial", 12))
        self.lbl_progress.pack(side=tk.RIGHT)
        
        self.lbl_id = ttk.Label(info_frame1, text="ID: ", font=("Arial", 12, "bold"))
        self.lbl_id.pack(side=tk.LEFT)

        # Title
        self.lbl_title = ttk.Label(self.root, text="", font=("MS Gothic", 16, "bold"), wraplength=750)
        self.lbl_title.pack(pady=10)

        # Current Category Display
        self.lbl_current_cat = ttk.Label(self.root, text="Not Categorized", font=("MS Gothic", 12), foreground="blue")
        self.lbl_current_cat.pack(pady=5)

        # Content (Scrollable text for details)
        text_frame = ttk.Frame(self.root, padding=10)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.txt_details = tk.Text(text_frame, height=10, font=("MS Gothic", 10))
        self.txt_details.pack(fill=tk.BOTH, expand=True)

        # Buttons Area
        btn_frame = ttk.LabelFrame(self.root, text="Select Category (Click to Assign)", padding=10)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        # Create Layout for Buttons
        for cat, subcats in CATEGORIES.items():
            row_frame = ttk.Frame(btn_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            lbl = ttk.Label(row_frame, text=cat, width=20, font=("MS Gothic", 10, "bold"))
            lbl.pack(side=tk.LEFT)
            
            for sub in subcats:
                btn = ttk.Button(row_frame, text=sub, command=lambda c=cat, s=sub: self.assign_category(c, s))
                btn.pack(side=tk.LEFT, padx=2)

        # Navigation Area
        nav_frame = ttk.Frame(self.root, padding=10)
        nav_frame.pack(fill=tk.X)
        
        ttk.Button(nav_frame, text="<< Prev", command=self.prev_course).pack(side=tk.LEFT)
        ttk.Button(nav_frame, text="Next >>", command=self.next_course).pack(side=tk.RIGHT)
        ttk.Button(nav_frame, text="Jump to Unlabeled", command=self.jump_unlabeled).pack(side=tk.BOTTOM)

    def show_current_course(self):
        if not self.course_ids:
            return
        
        cid = self.course_ids[self.current_index]
        info = self.data[cid]

        self.lbl_progress.config(text=f"{self.current_index + 1} / {len(self.course_ids)}")
        self.lbl_id.config(text=f"ID: {cid}")
        self.lbl_title.config(text=info.get("授業科目名", "No Title"))
        
        # Details
        desc = info.get("授業の目標・概要等", "")
        self.txt_details.delete("1.0", tk.END)
        self.txt_details.insert("1.0", desc)
        
        # Current Category
        cat = info.get("領域", "-")
        sub = info.get("分野", "-")
        if cat != "-":
            self.lbl_current_cat.config(text=f"Current: {cat} / {sub}", foreground="green")
        else:
            self.lbl_current_cat.config(text="Not Categorized", foreground="red")

    def assign_category(self, cat, sub):
        cid = self.course_ids[self.current_index]
        self.data[cid]["領域"] = cat
        self.data[cid]["分野"] = sub
        self.save_data()
        self.show_current_course() # Update display to show green
        # Optional: Auto-advance
        self.next_course()

    def next_course(self):
        if self.current_index < len(self.course_ids) - 1:
            self.current_index += 1
            self.show_current_course()
        else:
            messagebox.showinfo("End", "This is the last course.")

    def prev_course(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_course()

    def jump_unlabeled(self):
        found = False
        for i, cid in enumerate(self.course_ids):
            if "領域" not in self.data[cid] or self.data[cid]["領域"] == "その他": # Assuming "その他" might be default from previous script
                 # If using previous script, "その他" might be populated. 
                 # Let's check if "分野" is missing.
                if "分野" not in self.data[cid]:
                    self.current_index = i
                    self.show_current_course()
                    found = True
                    break
        if not found:
            messagebox.showinfo("Info", "No unlabeled courses found (checked '分野' field).")

def main():
    root = tk.Tk()
    app = LabelingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
