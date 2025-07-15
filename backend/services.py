from Bezier_Visual import vis_vase3D
from IGA import initialize_vase_code
import pygad
from Gaze_Graph import cosine_distance

# 初始化种群
def init_population(num_genes, population_size):

    return initialize_vase_code(num_genes=num_genes, num_solutions=population_size)

previous_elite_solutions = [] # 存储历史精英方案

# 用户评分反馈 & 迭代新一代___目前采用的是一种混合精英选择方法___
def evolve_population(gaze_records, selected_indices,current_population):
    from IGA import crossover, mutation,sigmoid_selection
    from Gaze_Graph import attention_rank, build_graph
    global attention_scores,new_population, previous_elite_solutions

    # 0.1. 计算注意力分数
    # G = build_graph(gaze_records)
    G = build_graph(gaze_records)  # 构造字典结构
    attention_scores = attention_rank(G,current_population,alpha_post=0.7, alpha_pre=0.7, beta_factor=1.0, max_iter=10, tol=1e-6)

    # 分离选中和未选中的索引
    unselected_indices = [i for i in range(len(current_population)) if i not in selected_indices]

    # 按 attention_scores 对选中和未选中的索引进行排序
    sorted_selected_indices = sorted(selected_indices, key=lambda idx: attention_scores.get(idx, 0.0), reverse=True)
    sorted_unselected_indices = sorted(unselected_indices, key=lambda idx: attention_scores.get(idx, 0.0), reverse=True)

    # 合并排序后的索引
    sorted_indices = sorted_selected_indices + sorted_unselected_indices

    # 根据排序后的索引重新排列种群
    sorted_population = [current_population[i] for i in sorted_indices]

    # 0.2. 在attention_rank的scores基础上定义评分函数
    def fitness_func(ga_instance, solution, solution_idx):
        return attention_scores.get(sorted_indices[solution_idx], 0.0)

    # 0.3.生成符合要求的精英位置逻辑！=[1,4] ---
    def generate_valid_positions(num, total):
        """
        生成间隔不为1和4的位置列表，
        - total是剩余的个体数量。
        - num是需要的位置数量。
        """
        valid = []
        candidate = 0
        while len(valid) < num and candidate < total:
            # 检查当前候选位置是否与已选位置冲突
            conflict = any(abs(candidate - p) in (1, 4) for p in valid)
            if not conflict:
                valid.append(candidate)
            candidate += 1
        return valid[:num]  # 确保不超过需要的数量

    # 新增：保留用户选择的精英方案（最多3个）
    num_elites = min(len(selected_indices), 3)
    elite_individuals = [sorted_population[i] for i in range(num_elites)]

    #  0.4. 设置GA主函数
    # 显式设置 crossover_probability 参数
    crossover_probability = 0.7
    # 显式设置 mutation_probability 参数
    mutation_probability = 0.1
    ga_instance = pygad.GA(
        num_generations=1,
        num_parents_mating=8,
        initial_population=sorted_population,
        num_genes=32,
        fitness_func = fitness_func,
        parent_selection_type="rank",
        mutation_type=mutation,# 后续修改一下
        crossover_type=crossover,
        crossover_probability=crossover_probability,
        mutation_probability=mutation_probability,
        keep_parents=0 # 设置为0，使用手动保留。
    )

    # ___传统方法___
    ga_instance.run()
    new_population = ga_instance.population.tolist()

    #                     return [], elite_positions

    # return new_population, elite_positions
    return new_population

# 生成 vase_code 的 SVG
def generate_vase_jpg(vase_code, idx=0):
    # 调用可视化函数生成 base64 编码的 SVG
    jpg_base64 = vis_vase3D(vase_code, idx)

    return jpg_base64

