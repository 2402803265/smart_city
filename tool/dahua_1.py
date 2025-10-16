import cv2
import datetime
import time
from tqdm import tqdm

class Camera_picture:
    def __init__(self):
        # 摄像头登录账号
        self.user = "admin"
        # 摄像头登录密码
        self.pwd = "ahpu0707"
        # 摄像头地址:端口
        self.ip = "192.168.68.55:554"
        # 截图存储位置
        self.file_path = r"D:\city_data\\"
        # 摄像头窗口名称
        self.name = "camera"
        self.video_path = r"D:\city_data\\"
        self.output_path = r"D:\city_data\\"
        # 要提取的帧数
        self.frame_count = 500

    def dahua(self):
        # channel：通道号，起始为 1。例如通道 2，则为 channel=2
        # subtype：码流类型，主码流为 0（即 subtype=0），辅码流为 1（即 subtype=1）。
        video_stream_path = f"rtsp://{self.user}:{self.pwd}@{self.ip}/cam/realmonitor?channel=1&subtype=0"
        cap = cv2.VideoCapture(video_stream_path)  # 连接摄像头
        print('IP 摄像头是否开启： {}'.format(cap.isOpened()))
        return cap

    def timing_screenshot(self):
        '''定时截图'''
        cap = self.dahua()
        if cap.isOpened():
            cv2.namedWindow(self.name, flags=cv2.WINDOW_FREERATIO)
            last_time = datetime.datetime.now()
            while True:
                ret, frame = cap.read()
                frame = cv2.resize(frame, (500, 300))
                cv2.imshow(self.name, frame)
                cur_time = datetime.datetime.now()
                name = self.file_path + str(time.time()) + ".jpg"
                if (cur_time - last_time).seconds >= 0.1:
                    cv2.imwrite(name, frame)  # 修正：使用已读取的 frame
                    last_time = cur_time
                    print("画面保存成功")
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()
        else:
            print("摄像头连接失败,请检查配置")

    def get_video_stream(self):
        '''获取视频流'''
        cap = self.dahua()
        if cap.isOpened():
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            # FourCC 是用于指定视频编解码器的 4 字节代码
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # 优化：使用更兼容的编解码器
            writer = cv2.VideoWriter(f"{self.file_path}{str(time.time())}.mp4", fourcc, fps, (width, height))
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                writer.write(frame)
                frame = cv2.resize(frame, (500, 300))
                cv2.imshow(self.name, frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()
        else:
            print("摄像头连接失败,请检查配置")

    def get_video_fps(self):
        """对一个视频进行分帧"""
        video = cv2.VideoCapture(self.video_path)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        interval = total_frames // self.frame_count
        frame_num = 0
        count = 0
        for _ in tqdm(range(total_frames)):  
            ret, frame = video.read()
            if not ret:
                break
            if frame_num % interval == 0:
                frame_filename = self.output_path + "/frame{:04d}.jpg".format(count)
                count += 1
                cv2.imwrite(frame_filename, frame)
            frame_num += 1
        video.release()


if __name__ == '__main__':
    run = Camera_picture()
    # run.timing_screenshot()
    run.get_video_stream()
    # run.manual_screenshot()
    # run.get_video_fps()