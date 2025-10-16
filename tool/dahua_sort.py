import os
import shutil
import cv2

# 原图片文件夹路径
source_folder = "D:/Users/lenovo/Desktop/dog_no/dog11_jpg"

# 分类文件夹配置，可按需添加或修改
category_folders = {
    '1': "D:/Users/lenovo/Desktop/dog_no/dog11_success",
    '2': "D:/Users/lenovo/Desktop/dog_no/dog11_default"
}

# 确保分类文件夹存在
for folder in category_folders.values():
    os.makedirs(folder, exist_ok=True)

# 获取原文件夹中的所有图片文件
image_files = [f for f in os.listdir(source_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

for image_file in image_files:
    image_path = os.path.join(source_folder, image_file)
    # 读取图片
    image = cv2.imread(image_path)
    cv2.imshow('Image', image)

    while True:
        key = cv2.waitKey(0)
        if chr(key) in category_folders:
            # 移动图片到对应的分类文件夹
            shutil.move(image_path, os.path.join(category_folders[chr(key)], image_file))
            break
        elif key == 27:  # 按ESC键跳过当前图片
            break

    cv2.destroyAllWindows()