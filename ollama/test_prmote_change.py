import cv2
import time
from ollama import Client
import base64
import numpy as np
import json
import os

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
                'content': '是否存在摆摊行为?如果存在,标记出摆摊行为在图像中的位置,以json格式输出,包含image_num,result,location三个键值.其中image_num是图像编号,result是检测结果(yes/no),location是摆摊位置的坐标信息(格式为[{"x": x1, "y": y1, "width": w, "height": h}]或空数组[])',
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
            try:
                # 尝试解析模型返回的JSON格式结果
                parsed_result = json.loads(result)
                parsed_result['image_num'] = frame_count  # 添加图像编号
                results.append(parsed_result)  # 将结果添加到列表中
            except json.JSONDecodeError:
                # 如果不是JSON格式，解析为简单的yes/no响应
                result_lower = result.strip().lower()
                if result_lower == 'yes':
                    parsed_result = {
                        'image_num': frame_count,
                        'result': 'yes',
                        'location': []
                    }
                    results.append(parsed_result)
                elif result_lower == 'no':
                    parsed_result = {
                        'image_num': frame_count,
                        'result': 'no',
                        'location': []
                    }
                    results.append(parsed_result)
                else:
                    # 如果无法解析为yes/no，也尝试查找JSON格式部分
                    # 搜索可能的JSON结构
                    start_idx = result.find('{')
                    end_idx = result.rfind('}')
                    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                        json_str = result[start_idx:end_idx+1]
                        try:
                            parsed_result = json.loads(json_str)
                            parsed_result['image_num'] = frame_count  # 添加图像编号
                            results.append(parsed_result)
                        except json.JSONDecodeError:
                            print(f"无法解析模型返回结果: {result}")
                            parsed_result = {
                                'image_num': frame_count,
                                'result': 'unknown',
                                'location': []
                            }
                            results.append(parsed_result)
                    else:
                        print(f"无法解析模型返回结果: {result}")
                        parsed_result = {
                            'image_num': frame_count,
                            'result': 'unknown',
                            'location': []
                        }
                        results.append(parsed_result)
        
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
    
    frame_count = 0
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
            try:
                # 尝试解析模型返回的JSON格式结果
                parsed_result = json.loads(result)
                parsed_result['image_num'] = frame_count  # 添加图像编号
                results.append(parsed_result)
            except json.JSONDecodeError:
                # 如果不是JSON格式，解析为简单的yes/no响应
                result_lower = result.strip().lower()
                if result_lower == 'yes':
                    parsed_result = {
                        'image_num': frame_count,
                        'result': 'yes',
                        'location': []
                    }
                    results.append(parsed_result)
                elif result_lower == 'no':
                    parsed_result = {
                        'image_num': frame_count,
                        'result': 'no',
                        'location': []
                    }
                    results.append(parsed_result)
                else:
                    # 如果无法解析为yes/no，也尝试查找JSON格式部分
                    # 搜索可能的JSON结构
                    start_idx = result.find('{')
                    end_idx = result.rfind('}')
                    if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                        json_str = result[start_idx:end_idx+1]
                        try:
                            parsed_result = json.loads(json_str)
                            parsed_result['image_num'] = frame_count  # 添加图像编号
                            results.append(parsed_result)
                        except json.JSONDecodeError:
                            print(f"无法解析模型返回结果: {result}")
                            parsed_result = {
                                'image_num': frame_count,
                                'result': 'unknown',
                                'location': []
                            }
                            results.append(parsed_result)
                    else:
                        print(f"无法解析模型返回结果: {result}")
                        parsed_result = {
                            'image_num': frame_count,
                            'result': 'unknown',
                            'location': []
                        }
                        results.append(parsed_result)
            frame_count += 1
           
        elif key == ord('q'):  # q键退出
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return results


def save_results_to_json(results, filename):
    """将结果保存为JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"结果已保存到文件: {filename}")


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
        
        # 保存本地视频结果到JSON文件
        output_filename = f"local_video_results_{int(time.time())}.json"
        save_results_to_json(model_results_local, output_filename)
        
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
                        print(f"帧 {frame_num} 的结果: {json.dumps(res, indent=2, ensure_ascii=False)}")
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
        
        # 保存实时视频流结果到JSON文件
        output_filename = f"stream_results_{int(time.time())}.json"
        save_results_to_json(model_results_stream, output_filename)
        
        return model_results_stream
    
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
            final_json = process_stream()
        
        elif choice == '3':
            print("程序结束")
            break
        
        else:
            print("无效选择，请输入 1-3 之间的数字")

# 启动程序
if __name__ == "__main__":
    main()



