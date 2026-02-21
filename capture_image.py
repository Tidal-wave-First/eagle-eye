import cv2
import os
from datetime import datetime

def main():
    SAVE_DIR = "./captures"
    # 确保保存目录存在
    os.makedirs(SAVE_DIR, exist_ok=True)
    
    # 尝试打开摄像头 (0 通常是默认摄像头)
    cap = cv2.VideoCapture(0)
    
    # 可选：设置摄像头分辨率 (可根据需要调整)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("❌ 错误：无法打开摄像头，请检查设备连接。")
        return

    print("=" * 50)
    print("📸 高级图片捕捉工具已启动")
    print("👉 按 [SPACE] 保存当前画面")
    print("👉 按 [Q] 或 关闭窗口 退出")
    print("=" * 50)

    window_name = "Image Capture - Press SPACE to Save"
    saved_count = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ 摄像头帧捕获失败")
                break

            # 在画面上添加操作提示 (OSD)
            hint_text = "Space: Save | Q: Quit"
            cv2.putText(frame, hint_text, (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 显示已保存数量
            count_text = f"Saved: {saved_count}"
            cv2.putText(frame, count_text, (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            cv2.imshow(window_name, frame)
            
            # 等待键输入 (1ms 延迟)
            key = cv2.waitKey(1) & 0xFF

            # 检测是否点击了窗口关闭按钮
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break

            if key == ord(' '):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(SAVE_DIR, f"capture_{timestamp}.jpg")
                
                # 增加保存成功的异常处理
                if cv2.imwrite(filename, frame):
                    saved_count += 1
                    print(f"✅ 已保存：{filename}")
                else:
                    print("❌ 保存失败，请检查磁盘权限")

            elif key == ord('q'):
                break

    except KeyboardInterrupt:
        print("\n⚠️ 检测到强制中断 (Ctrl+C)")
    finally:
        # 确保无论如何都会释放资源
        cap.release()
        cv2.destroyAllWindows()
        print(f"👋 程序退出，本次共保存 {saved_count} 张图片。")

if __name__ == "__main__":
    # 检查依赖
    try:
        import cv2
    except ImportError:
        print("❌ 未找到 opencv-python 库，请先运行：pip install opencv-python")
        exit(1)
    
    main()
