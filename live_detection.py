import cv2
import time
import os
import traceback
import sys
from datetime import datetime

# ========== 配置 ==========
CAMERA_ID = 0
TEMPLATE_PATH = "template.jpg"
TEMP_TEST_PATH = "temp_test.jpg"
RESULT_PATH = "live_result.jpg"
DETECT_INTERVAL = 1.0  # 检测间隔 (秒)
LOG_PATH = "crash.log"
# =========================

def setup_logging():
    """配置日志文件"""
    # 使用 'a' 模式追加日志，避免覆盖历史记录
    return open(LOG_PATH, "a", encoding="utf-8")

def log(msg, file_handle):
    """统一日志打印"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg)
    file_handle.write(full_msg + "\n")
    file_handle.flush()

def main():
    log_file = None
    cap = None
    
    try:
        log_file = setup_logging()
        log("🚀 启动实时检测...", log_file)
        
        # 1. 预检查文件
        if not os.path.exists(TEMPLATE_PATH):
            log(f"❌ 错误：找不到模板文件 {TEMPLATE_PATH}", log_file)
            sys.exit(1)
            
        # 2. 导入检测模块
        try:
            from defect_demo import detect_defect
            log("✅ 检测模块加载成功", log_file)
        except ImportError as e:
            log(f"❌ 无法导入 defect_demo 模块：{e}", log_file)
            sys.exit(1)
        
        # 3. 打开摄像头
        cap = cv2.VideoCapture(CAMERA_ID)
        # 尝试设置摄像头分辨率（可选，根据实际硬件调整）
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        if not cap.isOpened():
            log("❌ 无法打开摄像头", log_file)
            sys.exit(1)
        log("✅ 摄像头已打开", log_file)
        
        last_detect_time = 0
        frame_count = 0
        fps_start_time = time.time()
        fps = 0
        window_name = "Live Detection - Press Q to exit"
        last_defect_cnt = 0  # 缓存上一次检测结果，避免画面闪烁
        
        while True:
            ret, frame = cap.read()
            if not ret:
                log("❌ 无法获取画面", log_file)
                break
            
            # FPS 计算
            frame_count += 1
            current_time = time.time()
            if current_time - fps_start_time >= 1.0:
                fps = frame_count
                frame_count = 0
                fps_start_time = current_time
            
            # 在画面上显示 FPS 和提示
            cv2.putText(frame, f"FPS: {fps}", (frame.shape[1]-120, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
            cv2.putText(frame, "Press Q to quit", (10, frame.shape[0]-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
            
            # 自动检测 (非阻塞优化建议：如果 detect_defect 很慢，建议移入线程)
            if current_time - last_detect_time > DETECT_INTERVAL:
                try:
                    cv2.imwrite(TEMP_TEST_PATH, frame)
                    defect_cnt = detect_defect(TEMPLATE_PATH, TEMP_TEST_PATH, RESULT_PATH)
                    if defect_cnt is not None:
                        last_defect_cnt = defect_cnt # 缓存结果
                    else:
                        # 如果返回 None，保持显示上一次的结果或显示 0
                        pass 
                except Exception as detect_err:
                    log(f"⚠️ 检测过程发生错误：{detect_err}", log_file)
                    # 检测失败不中断主程序，继续运行
                
                last_detect_time = current_time
            
            # 显示检测结果 (使用缓存值，避免检测间隙数字消失)
            cv2.putText(frame, f"Defects: {last_defect_cnt}", (50, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 3)
            
            cv2.imshow(window_name, frame)
            
            # 检查 Q 键 (等待时间稍微增加一点有助于降低 CPU 占用，但不要超过检测间隔)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                log("👋 按 Q 键退出", log_file)
                break
            
            # 检查窗口是否被关闭
            try:
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    log("窗口被关闭，退出", log_file)
                    break
            except:
                pass
        
    except Exception as e:
        if log_file:
            log("="*50, log_file)
            log("❌ 发生未捕获的异常:", log_file)
            log(str(e), log_file)
            log("\n堆栈信息:", log_file)
            log(traceback.format_exc(), log_file)
            log("="*50, log_file)
        else:
            print(f"Critical Error (Log file not ready): {e}")
        sys.exit(1)
        
    finally:
        # 确保资源无论如何都会被释放
        if cap is not None:
            cap.release()
        cv2.destroyAllWindows()
        if log_file:
            log("👋 程序正常退出", log_file)
            log_file.close()

if __name__ == "__main__":
    main()
