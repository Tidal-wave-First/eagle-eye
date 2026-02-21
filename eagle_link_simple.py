import pandas as pd
import matplotlib.pyplot as plt
import os

INPUT_CSV = "/home/u13990/鹰眼记录.csv"
OUTPUT_EXCEL = "/home/u13990/缺陷日报.xlsx"
OUTPUT_CHART = "/home/u13990/缺陷趋势图.png"

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"❌ 找不到文件：{INPUT_CSV}")
        return

    df = pd.read_csv(INPUT_CSV, encoding='utf-8')
    if df.empty:
        print("⚠️ CSV 文件为空")
        return

    if '时间' not in df.columns or '缺陷数量' not in df.columns:
        print("❌ CSV 缺少 '时间' 或 '缺陷数量' 列")
        return

    df['时间'] = pd.to_datetime(df['时间'])
    df['日期'] = df['时间'].dt.date
    daily = df.groupby('日期')['缺陷数量'].sum().reset_index()
    daily.columns = ['日期', '缺陷总数']
    daily.to_excel(OUTPUT_EXCEL, index=False)
    print(f"✅ 日报已生成：{OUTPUT_EXCEL}")

    if len(daily) > 1:
        plt.figure(figsize=(10, 6))
        plt.plot(daily['日期'], daily['缺陷总数'], marker='o')
        plt.title('每日缺陷趋势')
        plt.xlabel('日期')
        plt.ylabel('缺陷总数')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(OUTPUT_CHART)
        plt.close()
        print(f"✅ 趋势图已生成：{OUTPUT_CHART}")
    else:
        print("ℹ️ 只有一天数据，不生成趋势图")

if __name__ == "__main__":
    main()
