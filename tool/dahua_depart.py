import cv2
import os

def extract_frames(video_path, output_folder):
    # 检查输出文件夹是否存在，如果不存在则创建
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("无法打开视频文件")
        return

    frame_count = 0
    while True:
        ret, frame = cap.read()

        if not ret:
            break

        # 生成帧文件名
        frame_filename = os.path.join(output_folder, f'frame_{frame_count:04d}.jpg')

        # 保存帧
        cv2.imwrite(frame_filename, frame)

        frame_count += 1

    # 释放视频捕获对象
    cap.release()
    print(f"共提取了 {frame_count} 帧图像")

if __name__ == "__main__":
    # 替换为你的视频文件路径
    video_path = "D:/city_data/1751324020.9424746.mp4"    #########
    # 替换为你想要保存帧的文件夹路径
    output_folder = "D:/city_jpg7"                            #########

    extract_frames(video_path, output_folder)