import json
import numpy as np
from itertools import product

def cosine_distance(a, b):
    a = np.array(a)
    b = np.array(b)
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 1
    return 1 - (dot_product / (norm_a * norm_b))

def calculate_average_replacement_distance(data):
    remove_operations = []
    add_operations = []
    distances = []

    for record in data:
        if record["operation"] == "remove":
            remove_operations.append(record["vasecode"])
        elif record["operation"] == "add":
            add_operations.append(record["vasecode"])
            if remove_operations:
                # 计算所有可能的配对距离
                all_distances = []
                for remove_code, add_code in product(remove_operations, add_operations):
                    dist = cosine_distance(remove_code, add_code)
                    all_distances.append(dist)
                # 取最小距离
                min_distance = min(all_distances)
                distances.append(min_distance)
                remove_operations = []
                add_operations = []

    if distances:
        average_distance = np.mean(distances)
        return average_distance
    else:
        return None

# 读取 JSON 文件
file_path = 'c:/Users/KATVR/Downloads/design_operation_logs_2025-07-14T14_00_56.373Z.json'
with open(file_path, 'r') as file:
    data = json.load(file)

# 计算平均替换距离
average_distance = calculate_average_replacement_distance(data)
if average_distance is not None:
    print(f"平均替换距离: {average_distance}")
else:
    print("未找到替代操作对，无法计算平均替换距离。")