import importlib.util
import subprocess
import sys
import os
import cv2
import numpy as np
import gradio as gr
from PIL import Image
import tempfile

script_dir = os.path.dirname(os.path.abspath(__file__))
print("脚本所在目录:", script_dir)

# def ensure_package_installed(package_name, forced_install=False):
#     if forced_install:
#         subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
#         print(f"{package_name} 包已成功安装")
#         return
#     spec = importlib.util.find_spec(package_name)
#     if spec is None:
#         print(f"未找到 {package_name} 包，正在尝试自动安装...")
#         subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
#         print(f"{package_name} 包已成功安装")
#     else:
#         print(f"{package_name} 包已安装")

# def install_dependencies(deps, forced_install=False):
#     for dep in deps:
#         ensure_package_installed(dep, forced_install)

# dependencies = ["paddlex==3.0.0rc1", "paddlex[base]==3.0.0rc1"]
# install_dependencies(dependencies, forced_install=True)

from paddlex import create_model  # 必须在最后导入

# 加载模型
model = create_model(model_name='PicoDet-S', model_dir="C:/Users/lenovo/PaddleX/output/best_model/inference")

# 定义基础路径
base_path = r"D:\Users\lenovo\Desktop\competetion"

# 确保基础路径存在
if not os.path.exists(base_path):
    os.makedirs(base_path)

# 绘制函数
def draw_boxes_on_image(image_data, detection_results, output_path):
    # 将 PIL 图像转换为 OpenCV 格式
    image_np = np.array(image_data)[:, :, ::-1].copy()

    height, width = image_np.shape[:2]

    for result in detection_results:
        label = result.get('label', 'unknown')
        score = result.get('score', 0.0)
        coordinate = result.get('coordinate', [0, 0, 0, 0])

        if not isinstance(coordinate, (list, tuple)) or len(coordinate) != 4:
            continue

        x_min, y_min, x_max, y_max = map(int, coordinate)
        x_min = max(0, x_min)
        y_min = max(0, y_min)
        x_max = min(width, x_max)
        y_max = min(height, y_max)

        # 绘制边框
        cv2.rectangle(image_np, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)

        text = f"{label}: {score:.2f}"
        font_scale = 0.5
        thickness = 1
        text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        text_width, text_height = text_size

        # 默认显示在框上方，如果超出图像顶部，则改为框内部靠上
        text_x = x_min
        text_y = y_min - 5
        if text_y - text_height < 0:
            text_y = y_min + text_height + 5  # 移到框内

        # 添加文字背景
        cv2.rectangle(image_np, (text_x, text_y - text_height), (text_x + text_width, text_y), (0, 0, 255), -1)
        # 写文字
        cv2.putText(image_np, text, (text_x, text_y - 2), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

    cv2.imwrite(output_path, image_np)
    return output_path

# 预测函数
def predict_with_paddlex(image_data):
    # 保存上传的图像数据到临时文件
    temp_input_filename = "temp_input_image.jpg"
    temp_input_path = os.path.join(base_path, temp_input_filename)
    image_data.save(temp_input_path)

    if not os.path.exists(temp_input_path):
        return None, "❌ 输入图像不存在！"

    output = model.predict(temp_input_path, batch_size=1)
    results = []
    for res in output:
        for box in res.get('boxes', []):
            results.append(box)

    if not results:
        return None, "⚠️ 未检测到目标"

    # 输出路径在系统的临时目录中
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_output_file:
        output_path = temp_output_file.name
        try:
            draw_boxes_on_image(image_data, results, output_path)
        except Exception as e:
            return None, f"❌ 绘制检测框失败: {str(e)}"

    text_results = "\n".join(str(res) for res in results)
    return output_path, text_results

# Gradio 界面配置：先图片后文本
iface = gr.Interface(
    fn=predict_with_paddlex,
    inputs=gr.Image(type="pil", label="上传图片"),
    outputs=[
        gr.Image(type="filepath", label="标注后的图片"),  # 放在前面（上）
        gr.Textbox(label="检测结果")                    # 放在后面（下）
    ],
    title="PaddleX 目标检测",
    description="上传图片，自动运行 PaddleX PicoDet-S 目标检测，结果包括检测框和类别+置信度信息。"
)

# 运行 Gradio
if __name__ == "__main__":
    iface.launch()



