import os
import shutil
import random


def split_data(source_dir, target_dir1, target_dir2, ratio, move=False):
    """
    将源文件夹中的数据按比例分配到两个目标文件夹

    参数:
    source_dir: 源文件夹路径
    target_dir1: 目标文件夹1路径
    target_dir2: 目标文件夹2路径
    ratio: 分配到第一个文件夹的比例 (0-1之间)
    move: 是否移动文件 (False则复制文件)
    """
    # 验证比例有效性
    if not 0 <= ratio <= 1:
        raise ValueError("比例必须在0和1之间")

    # 创建目标文件夹
    os.makedirs(target_dir1, exist_ok=True)
    os.makedirs(target_dir2, exist_ok=True)

    # 获取源文件夹中的所有文件
    files = [f for f in os.listdir(source_dir)
             if os.path.isfile(os.path.join(source_dir, f))]

    # 打乱文件顺序确保随机分配
    random.shuffle(files)

    # 计算分割点
    split_index = int(len(files) * ratio)

    # 分配文件到第一个文件夹
    for file in files[:split_index]:
        src_path = os.path.join(source_dir, file)
        dst_path = os.path.join(target_dir1, file)

        if move:
            shutil.move(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)

    # 分配文件到第二个文件夹
    for file in files[split_index:]:
        src_path = os.path.join(source_dir, file)
        dst_path = os.path.join(target_dir2, file)

        if move:
            shutil.move(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)

    print(f"操作完成! 共处理 {len(files)} 个文件")
    print(f"分配到 {target_dir1}: {split_index} 个文件")
    print(f"分配到 {target_dir2}: {len(files) - split_index} 个文件")


# 示例使用
if __name__ == "__main__":
    # 配置路径和比例
    SOURCE_DIR = "D:/Users/lenovo/Desktop/比赛/基于大小模型的智慧城市监控系统/baitan/baitan_original"  # 源文件夹路径
    TARGET_DIR1 = "D:/Users/lenovo/Desktop/比赛/基于大小模型的智慧城市监控系统/baitan/baitan_train"  # 第一个目标文件夹
    TARGET_DIR2 = "D:/Users/lenovo/Desktop/比赛/基于大小模型的智慧城市监控系统/baitan/baitan_test"  # 第二个目标文件夹
    RATIO = 0.8  # 80%分配到train, 20%分配到test
    MOVE_FILES = False  # True=移动文件, False=复制文件

    # 执行分配
    split_data(SOURCE_DIR, TARGET_DIR1, TARGET_DIR2, RATIO, MOVE_FILES)