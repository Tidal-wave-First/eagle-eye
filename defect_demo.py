import cv2
import numpy as np
import csv
from datetime import datetime
import os
import time
import defect_report  # 导入日报模块，用于直接调用

# 用于控制日报更新频率
last_report_time = 0
REPORT_COOLDOWN = 10  # 秒

def align_images(template, target, max_features=500):
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    gray_target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create(max_features)
    kp1, des1 = orb.detectAndCompute(gray_template, None)
    kp2, des2 = orb.detectAndCompute(gray_target, None)
    if des2 is None or len(kp2) < 4:
        return None, 0
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)
    if len(matches) < 4:
        return None, 0
    good_matches = matches[:int(len(matches)*0.3)]
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1,1,2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1,1,2)
    H, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    if H is None:
        return None, 0
    h, w = gray_target.shape
    aligned = cv2.warpPerspective(template, H, (w, h))
    return aligned, len(good_matches)

def detect_defect(template_path, test_path, output_path="result.jpg"):
    global last_report_time
    template = cv2.imread(template_path)
    test = cv2.imread(test_path)
    if template is None or test is None:
        print("❌ 图片读取失败，检查路径")
        return
    aligned, match_count = align_images(template, test)
    if aligned is None:
        print(f"❌ 对齐失败，特征点匹配数：{match_count}")
        return
    gray_aligned = cv2.cvtColor(aligned, cv2.COLOR_BGR2GRAY)
    gray_test = cv2.cvtColor(test, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray_test, gray_aligned)
    _, thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    clean = cv2.morphologyEx(clean, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    defect_cnt = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 200:
            defect_cnt += 1
            x, y, w_box, h_box = cv2.boundingRect(cnt)
            cv2.rectangle(test, (x, y), (x+w_box, y+h_box), (0,0,255), 2)

    # 记录检测结果到CSV（仅当有缺陷时）
    if defect_cnt > 0:
        log_path = "./鹰眼记录.csv"
        file_exists = os.path.isfile(log_path)
        try:
            with open(log_path, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['时间', '测试图片路径', '缺陷数量'])
                writer.writerow([
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    test_path,
                    defect_cnt
                ])
            print("CSV写入成功")
            # 触发日报更新（带冷却）- 直接调用函数而非子进程
            current_time = time.time()
            if current_time - last_report_time > REPORT_COOLDOWN:
                defect_report.main()   # 直接调用日报生成函数
                last_report_time = current_time
        except Exception as e:
            print(f"CSV写入失败：{e}")

    label = f"Defect: {defect_cnt}" if defect_cnt > 0 else "OK"
    color = (0,0,255) if defect_cnt > 0 else (0,255,0)
    cv2.putText(test, label, (30,50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.putText(test, f"Matches: {match_count}", (30,100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)
    cv2.imwrite(output_path, test)
    print(f"✅ 检测完成，缺陷数：{defect_cnt}，结果已保存至 {output_path}")
    return defect_cnt

if __name__ == "__main__":
    detect_defect("template.jpg", "test.jpg", "result.jpg")