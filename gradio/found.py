import os

model_dir = "C:/Users/lenovo/PaddleX/output/best_model"
print("模型目录内容:")
for file in os.listdir(model_dir):
    print(f" - {file}")
    
    # 检查可能的配置文件
    if file.endswith(('.yml', '.yaml', '.json', '.config')):
        print(f"✅ 找到可能的配置文件: {file}")
        # 可以尝试使用这个文件