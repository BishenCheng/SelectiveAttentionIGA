import numpy as np
from pyDOE import lhs


# 融合设计知识的初始化（4维拉丁超立方采样）
# def initialize_vase_code(num_genes=32,num_solutions=16):
#     # 生成4维拉丁超立方采样样本
#     samples = lhs(4, samples=num_solutions,criterion='maximin')
#     vase_code = []
#
#     for sample in samples:
#         binary_parts = []
#         for x in sample:
#             # 将参数映射到0-255的整数
#             value = int(x * 255)
#             # 转换为8位二进制字符串（填充前导零）
#             binary_str = format(value, '08b')  # 例如：0 -> '00000000'
#             binary_parts.append(binary_str)
#
#         # 拼接四个设计区域的二进制字符串，形成32位完整编码
#         full_binary = ''.join(binary_parts)  # 例如：'00000000000000000000000000000000'
#         full_binary_list = [int(bit) for bit in full_binary] # 列表化
#
#         vase_code.append(full_binary_list)
#
#     return vase_code  # 返回16个32位二进制编码的解


# 初始化vase_code列表（均匀）32维LHS
# def initialize_vase_code(num_genes=32, num_solutions=16):
#
#     # 使用拉丁超立方采样生成均匀分布的随机二进制解
#     samples = lhs(num_genes, samples=num_solutions, criterion='center')
#     vase_code = (samples * 2).astype(int).tolist()
#
#     return vase_code


# 初始化vase_code列表（随机）
def initialize_vase_code(num_genes=32, num_solutions=16):
    vase_code = []
    for _ in range(num_solutions):
        vase_code.append(np.random.randint(2, size=num_genes).tolist())

    return vase_code



# # 适应度函数（旧方法：基于用户评分）
# def fitness_func(user_scores):
#     def inner_fitness(ga_instance, solution, solution_idx):
#         return user_scores[solution_idx] # 避免使用全局变量。
#     return inner_fitness



# 选择函数___sigmoid选择___
def sigmoid(x, steepness=1.0, shift=0.0):
    return 1 / (1 + np.exp(-steepness * (x - shift)))

def sigmoid_selection(population, fitness_values, num_parents_mating):
    """
    自定义父代选择函数：基于 Sigmoid 的非线性选择。

    参数:
    - population: 种群数组（二维列表或 NumPy 数组）
    - fitness_values: 每个个体的适应度值（列表或 NumPy 数组）
    - num_parents_mating: 需要选择的父代数量
    - steepness: Sigmoid 曲线的陡峭程度
    - shift: Sigmoid 曲线的偏移量

    返回:
    - parent_indices: 被选中父代的索引列表
    """

    # 1. 将适应度值通过 Sigmoid 函数转换为选择概率
    fitness_sigmoid = [sigmoid(f, steepness=1.0, shift=0.0) for f in fitness_values]

    # 2. 归一化为概率分布
    total = sum(fitness_sigmoid)
    if total == 0:
        # 避免除以零，当所有适应度值为零时，随机选择
        probabilities = [1.0 / len(fitness_values)] * len(fitness_values)
    else:
        probabilities = [f / total for f in fitness_sigmoid]

    # 3. 根据概率选择父代（允许重复选择）
    parent_indices = np.random.choice(len(population), size=num_parents_mating, p=probabilities, replace=True)

    return parent_indices


# 变异函数
def mutation(offspring_crossover, ga_instance):
    mutation_rate = ga_instance.mutation_probability
    for idx in range(len(offspring_crossover)):
        for gene_idx in range(ga_instance.num_genes):
            r = np.random.rand()
            if r < mutation_rate:
                offspring_crossover[idx][gene_idx] = 1 - offspring_crossover[idx][gene_idx]
    return offspring_crossover

# 交叉函数
def crossover(parents, offspring_size, ga_instance):
    offspring_crossover = []
    intersect_rate = ga_instance.crossover_probability
    intersect_point = [3, 6, 9, 11, 14, 17, 20, 23, 25, 27, 29]
    
    # 确保生成足够数量的后代
    while len(offspring_crossover) < offspring_size[0]:
        parent1_idx, parent2_idx = np.random.choice(len(parents), 2, replace=False)
        random_val = np.random.rand()
        if intersect_rate > random_val:
            point = intersect_point[np.random.choice(len(intersect_point))]
            offspring1 = np.concatenate((parents[parent1_idx][:point], parents[parent2_idx][point:])).tolist()
            offspring2 = np.concatenate((parents[parent2_idx][:point], parents[parent1_idx][point:])).tolist()
            offspring_crossover.extend([offspring1, offspring2])
        else:
            offspring1 = parents[parent1_idx].copy().tolist()
            offspring2 = parents[parent2_idx].copy().tolist()
            offspring_crossover.extend([offspring1, offspring2])
    
    # 截断或填充到所需数量
    offspring_crossover = offspring_crossover[:offspring_size[0]]
    
    # 将列表转换为numpy数组
    offspring_crossover = np.array(offspring_crossover)
    return offspring_crossover