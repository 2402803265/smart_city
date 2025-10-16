import cv2
import time
from ollama import Client
import base64
import numpy as np

def process_frame(frame, client):
    """处理单帧图像并返回结果"""
    # 将帧转换为base64编码的字符串
    _, buffer = cv2.imencode('.jpg', frame)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    
    response = client.chat(
        model='qwen2.5vl:3b',
        messages=[
            {
                'role': 'user',
                'content': '是否存在摆摊行为? 只回答yes或no',                
                'images': [image_base64],
            }
        ],
    )
    return response.message.content


# 从本地视频文件抽帧并处理
def process_video(video_path, frame_rate=1):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    client = Client()  # 创建客户端实例
    frame_count = 0
    results = []  # 存储模型反馈结果
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_rate == 0:
            result = process_frame(frame, client)  # 传递client
            results.append(result)  # 将结果添加到列表中
        
        frame_count += 1
    print("all the result is over")
    cap.release()
    return results  # 返回所有结果


# 处理实时视频流信息
def process_video_stream(camera_index=0):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    client = Client()  # 创建客户端实例
    results = []  # 存储模型反馈结果
    
    print("视频流已启动。按 'a' 键处理当前帧，按 'q' 键退出")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 显示当前帧（无结果文本）
        cv2.imshow('Video Stream', frame)
        
        # 检测按键输入
        key = cv2.waitKey(1) & 0xFF
        if key == ord('a'):  # a键触发处理
            result = process_frame(frame, client)  # 传递client
            results.append(result)
           
        elif key == ord('q'):  # q键退出
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return results


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
    
    def process_stream():
        """处理实时视频流"""
        print(f"开始处理实时视频流")
        model_results_stream = process_video_stream()
        
        # 统计结果
        count_yes_stream = 0
        count_no_stream = 0
        for i, res in enumerate(model_results_stream):
            if res == 'yes':
                count_yes_stream += 1
            else:
                count_no_stream += 1
        
        # 输出最终结果
        print(f"\n实时视频流分析完成 (总处理数: {len(model_results_stream)})")
        print(f"'yes' 数量: {count_yes_stream} | 'no' 数量: {count_no_stream}")
        if count_yes_stream >= count_no_stream:
            print("实时视频流最终结果: yes")
        else:
            print("实时视频流最终结果: no")
    
    # 主循环
    while True:
        print("\n" + "="*40)
        print("视频分析系统")
        print("="*40)
        print("1. 处理本地视频并查询帧结果")
        print("2. 处理实时视频流")
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
            # 处理实时视频流
            process_stream()
        
        elif choice == '3':
            print("程序结束")
            break
        
        else:
            print("无效选择，请输入 1-3 之间的数字")

# 启动程序
if __name__ == "__main__":
    main()



