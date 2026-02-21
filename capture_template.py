import cv2
cap = cv2.VideoCapture(0)
print("按空格键拍照保存为 template.jpg，按 q 退出")
while True:
    ret, frame = cap.read()
    cv2.imshow("Capture Template", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord(' '):
        cv2.imwrite("template.jpg", frame)
        print("✅ 已保存 template.jpg")
    elif key == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()