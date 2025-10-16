import os
import shutil

# 源文件夹列表，可按需添加
source_folders = [
    "D:/Users/lenovo/Desktop/牵绳/dog1-ok",
    "D:/Users/lenovo/Desktop/牵绳/dog2-ok",
    "D:/Users/lenovo/Desktop/牵绳/dog3-ok",
    "D:/Users/lenovo/Desktop/牵绳/dog4-ok",
    "D:/Users/lenovo/Desktop/牵绳/dog5-ok",
    "D:/Users/lenovo/Desktop/牵绳/dog6-ok",
    "D:/Users/lenovo/Desktop/不牵绳/dog8_success",
    "D:/Users/lenovo/Desktop/不牵绳/dog9_success",
    "D:/Users/lenovo/Desktop/不牵绳/dog10_success",
    "D:/Users/lenovo/Desktop/不牵绳/dog11_success",
    "D:/Users/lenovo/Desktop/不牵绳/dog12_success",
    "D:/Users/lenovo/Desktop/不牵绳/dog13_success",
    "D:/Users/lenovo/Desktop/不牵绳/dog14_success",

]

# 目标文件夹，文件将被移动到这里
target_folder = "D:/Users/lenovo/Desktop/比赛/基于大小模型的智慧城市监控系统/data/dog/dog_original"
# 确保目标文件夹存在
os.makedirs(target_folder, exist_ok=True)

# 文件计数器，从0开始
counter = 0

# 遍历所有源文件夹
for source_folder in source_folders:
    if os.path.exists(source_folder):
        # 遍历源文件夹中的所有文件
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                # 获取文件扩展名
                file_ext = os.path.splitext(file)[1]
                # 生成新文件名，格式为city_data_count
                new_file_name = f'rubbish_{counter}{file_ext}'
                new_file_path = os.path.join(target_folder, new_file_name)
                # 移动并重命名文件
                shutil.move(file_path, new_file_path)
                counter += 1
    else:
        print(f'源文件夹 {source_folder} 不存在，请检查路径。')