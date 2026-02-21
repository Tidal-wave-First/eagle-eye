import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os

# 数值列清理函数（去除非法字符）
def clean_numeric(series):
    if series.dtype == 'object':
        cleaned = series.astype(str).str.replace(r'[^0-9.-]', '', regex=True)
        return pd.to_numeric(cleaned, errors='coerce')
    return series

# 自动检测常见列名
def auto_detect_columns(df):
    cols = {col.lower(): col for col in df.columns}
    detected = {'name': None, 'hours': None, 'rate': None, 'days': None, 'bonus': None}
    # 姓名列
    for name in ['姓名', '名字', '名称', 'name']:
        if name in cols:
            detected['name'] = cols[name]; break
    # 工时列
    for name in ['工时', '小时', '工作时长', 'hours']:
        if name in cols:
            detected['hours'] = cols[name]; break
    # 时薪列
    for name in ['时薪', '小时工资', 'rate', 'salary']:
        if name in cols:
            detected['rate'] = cols[name]; break
    # 出勤天数
    for name in ['出勤天数', '出勤', '工作天数', 'days']:
        if name in cols:
            detected['days'] = cols[name]; break
    # 奖金列
    for name in ['奖金', 'bonus', '奖励']:
        if name in cols:
            detected['bonus'] = cols[name]; break
    return detected

# 询问是否保存并退出
def ask_save_exit(root, df):
    if messagebox.askyesno("保存并退出", "是否保存当前数据并退出？\n(选“否”继续)"):
        save_file(df, root)
        root.deiconify()
        return True
    return False

# 保存文件对话框
def save_file(df, root):
    path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")])
    if not path: return False
    try:
        if path.endswith('.csv'):
            df.to_csv(path, index=False, encoding='utf-8-sig')
        else:
            df.to_excel(path, index=False)
        messagebox.showinfo("完成", f"文件已保存至：\n{path}")
        return True
    except Exception as e:
        messagebox.showerror("错误", f"保存失败：{str(e)}")
        return False

# 主处理流程
def process_file(root):
    root.withdraw()
    src = filedialog.askopenfilename(title="选择源文件",
                filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")])
    if not src:
        root.deiconify()
        return

    try:
        if src.endswith('.csv'):
            df = pd.read_csv(src, encoding='utf-8')
        else:
            df = pd.read_excel(src)
    except Exception as e:
        messagebox.showerror("错误", f"读取文件失败：{str(e)}")
        root.deiconify()
        return

    # 基础清洗
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()
    df = df.fillna('')
    for col in df.columns:
        cleaned = clean_numeric(df[col])
        if cleaned.notna().any():
            df[col] = cleaned
    messagebox.showinfo("完成", "数值列已自动清理。")

    detected = auto_detect_columns(df)

    # 排序处理
    if detected['name']:
        if messagebox.askyesno("排序", f"是否按姓名列（{detected['name']}）升序排序？"):
            df = df.sort_values(by=detected['name'], ascending=True)
            messagebox.showinfo("完成", "已排序")
        else:
            if ask_save_exit(root, df): return
            if messagebox.askyesno("手动排序", "是否手动指定排序列？"):
                cols = list(df.columns)
                col = simpledialog.askstring("手动排序", f"请输入列名：{', '.join(cols)}")
                if col and col in cols:
                    asc = messagebox.askyesno("排序方向", "升序吗？\n是→升序，否→降序")
                    df = df.sort_values(by=col, ascending=asc)
                    messagebox.showinfo("完成", f"已按 {col} 排序")
                else:
                    messagebox.showwarning("取消", "未指定有效列名，跳过排序")
    else:
        if messagebox.askyesno("未检测到姓名列", "是否手动指定排序列？"):
            cols = list(df.columns)
            col = simpledialog.askstring("手动排序", f"请输入列名：{', '.join(cols)}")
            if col and col in cols:
                asc = messagebox.askyesno("排序方向", "升序吗？")
                df = df.sort_values(by=col, ascending=asc)
                messagebox.showinfo("完成", f"已按 {col} 排序")
            else:
                messagebox.showwarning("取消", "跳过排序")
        else:
            if ask_save_exit(root, df): return

    # 最终保存
    if messagebox.askyesno("保存", "是否保存处理后的文件？"):
        save_file(df, root)
    else:
        if ask_save_exit(root, df): return

    root.deiconify()

# 创建主窗口
def main():
    root = tk.Tk()
    root.title("闪电数驿 - 数据清洗工具")
    root.geometry("300x150")

    btn = tk.Button(root, text="选择文件并处理", command=lambda: process_file(root))
    btn.pack(expand=True)

    root.mainloop()

if __name__ == "__main__":
    main()