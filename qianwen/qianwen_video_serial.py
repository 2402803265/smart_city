import serial  # type:ignore
import cv2
import base64
from openai import OpenAI
import threading
import time

# 串口配置
COM_PORT = "/dev/ttyUSB0"  # Linux设备串口
# COM_PORT = "COM7"        # Windows串口
BAUD_RATE = 9600
TIMEOUT = 5

# 串口助手类（添加了接收功能）
class SerialAssistant:
    def __init__(self, com_port=COM_PORT, baud_rate=BAUD_RATE, timeout=TIMEOUT):
        self.com_port = com_port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.ser = None
        self.last_received = None
        self.receiving = False
        self.receive_thread = None
        
        try:
            self.ser = serial.Serial(
                self.com_port,
                self.baud_rate,
                timeout=self.timeout
            )
            print(f"成功连接到串口 {self.com_port}")
            self.start_receiving()
        except serial.SerialException as e:
            print(f"串口打开失败: {e}")
    
    def start_receiving(self):
        """启动接收线程"""
        if self.ser and self.ser.is_open:
            self.receiving = True
            self.receive_thread = threading.Thread(target=self._receive_loop)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            print("串口接收线程已启动")
    
    def _receive_loop(self):
        """接收数据的循环"""
        while self.receiving:
            try:
                if self.ser.in_waiting > 0:
                    data = self.ser.readline().decode().strip()
                    if data:
                        self.last_received = data
                        print(f"串口收到: {data}")
            except Exception as e:
                print(f"串口接收错误: {e}")
            time.sleep(0.1)  # 避免过度占用CPU
    
    def check_received(self, target):
        """检查是否收到特定数据"""
        if self.last_received == target:
            self.last_received = None  # 重置
            return True
        return False
    
    def send_command(self, command):
        """发送命令到串口"""
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(command.encode())
                self.ser.flush()
                print(f"串口发送: {command}")
                return True
            except Exception as e:
                print(f"串口发送失败: {e}")
                return False
        else:
            print("串口未打开，无法发送数据！")
            return False
    
    def close(self):
        """关闭串口"""
        self.receiving = False
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1.0)
        
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("串口已关闭")

# 读取单帧图像并进行Base64编码
def read_frame_as_base64(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')

# 初始化OpenAI客户端
client = OpenAI(
    api_key="sk-ddcd1e783e694fe085fc7d21d262fb66",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 处理单帧图像
def process_frame(frame, client):
    text = "是否存在摆摊,只回答yes or no?"  # 在此处修改提示词
    base64_image = read_frame_as_base64(frame)
    
    completion = client.chat.completions.create(
        model="qwen-vl-max-latest", 
        messages=[
            {
                "role": "system",
                "content": [{"type": "text", "text": "You are a helpful assistant."}],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                    {"type": "text", "text": text},
                ],
            },
        ],
    )
    return completion.choices[0].message.content

# 处理实时视频流信息（使用串口接收'a'触发API访问）
def process_video_stream(camera_index=0):
    # 初始化串口助手
    serial_assistant = SerialAssistant()
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    results = []  # 存储模型反馈结果
    
    print("视频流已启动。等待串口发送 'a' 触发API访问,按 'q' 键退出")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 显示当前帧
        cv2.imshow('Video Stream', frame)
        
        # 检测串口是否收到'a'
        if serial_assistant.check_received('a'):
            print("检测到串口触发信号 'a'，开始处理当前帧...")
            result = process_frame(frame, client)
            results.append(result)
            print(f"AI分析结果: {result}")
            
            # 根据结果发送不同的串口命令
            if "yes" in result.lower():
                serial_assistant.send_command("T1")  # 发送命令1
            elif "no" in result.lower():
                serial_assistant.send_command("T2")  # 发送命令2
            else:
                print("无法识别的结果，不发送串口命令")
        
        # 检测键盘输入（仅用于退出）
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # q键退出
            break
    
    cap.release()
    cv2.destroyAllWindows()
    serial_assistant.close()  # 关闭串口
    return results
# 从本地视频文件抽帧并处理
def process_video(video_path, frame_rate=1):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    frame_count = 0
    results = []  # 存储模型反馈结果
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_rate == 0:
            result = process_frame(frame, client)
            # print(f"Frame {frame_count}: {result}")
            results.append(result)  # 将结果添加到列表中
        
        frame_count += 1
    print("all the result is over")
    cap.release()
    return results  # 返回所有结果


# 其余代码保持不变...
def main():
    # 配置参数
    rate = 20
    local_video_path = "D:/city_data/摆摊/1751322938.900309 - 副本.mp4"
    model_results_local = None
    
    def process_local_video():
        """处理本地视频并返回结果列表"""
        nonlocal model_results_local
        print(f"开始处理本地视频: {local_video_path} (采样率: {rate}帧/次)")
        model_results_local = process_video(local_video_path, frame_rate=rate)
        print(f"视频处理完成，共 {len(model_results_local)} 个结果")
        return model_results_local
    
    def query_frames(results):
        """查询特定帧的结果"""
        while True:
            print("\n输入 'q' 返回主菜单")
            frame_need = input("请输入要查询的帧号: ")
            
            if frame_need.lower() == 'q':
                print("返回主菜单")
                break
            
            try:
                frame_num = int(frame_need)
                
                if frame_num % rate == 0:
                    index = frame_num // rate
                    if 0 <= index < len(results):
                        res = results[index]
                        print(f"帧 {frame_num} 的结果: {res}")
                    else:
                        print(f"错误: 索引超出范围 ({index})，有效范围: 0-{len(results)-1}")
                else:
                    print(f"错误: 帧号必须是 {rate} 的倍数，您输入的是 {frame_num}")
            
            except ValueError:
                print("无效输入! 请输入数字或 'q'")
    
    # 主循环
    while True:
        print("\n" + "="*40)
        print("视频分析系统")
        print("="*40)
        print("1. 处理本地视频并查询帧结果")
        print("2. 处理实时视频流（串口触发）")
        print("3. 退出程序")
        print("="*40)
        
        choice = input("请选择操作 (1-3): ")
        
        if choice == '1':
            # 处理本地视频
            if model_results_local is None:
                model_results_local = process_local_video()
            
            # 查询帧结果
            query_frames(model_results_local)
        
        elif choice == '2':
            # 处理实时视频流（使用串口触发）
            process_stream = lambda: process_video_stream()
            process_stream()
        
        elif choice == '3':
            print("程序结束")
            break
        
        else:
            print("无效选择，请输入 1-3 之间的数字")

# 启动程序
if __name__ == "__main__":
    main()