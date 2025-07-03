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
    #from Gaze_Graph import attention_rank, build_graph
    global attention_scores,new_population, previous_elite_solutions

    # 0.1. 计算注意力分数
    # G = build_graph(gaze_records)
    # G = build_graph(gaze_records)  # 构造字典结构
    # attention_scores = attention_rank(G,current_population,alpha_post=0.7, alpha_pre=0.7, beta_factor=1.0, max_iter=10, tol=1e-6)

    # 0.2. 在attention_rank的scores基础上定义评分函数
    def fitness_func(ga_instance, solution, solution_idx):

        return attention_scores.get(solution_idx, 0.0)

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
    elite_individuals = [current_population[i] for i in selected_indices[:num_elites]]

    #  0.4. 设置GA主函数
    # 显式设置 crossover_probability 参数
    crossover_probability = 0.7
    # 显式设置 mutation_probability 参数
    mutation_probability = 0.1
    ga_instance = pygad.GA(
        num_generations=1,
        num_parents_mating=8,
        initial_population=current_population,
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
    # ga_instance.run()
    # new_population = ga_instance.population.tolist()

    #___保留精英方法___

    #  1. 精英方案数量
    num_elites = min(len(selected_indices), 3)

    # 2. 保留用户选择的精英方案
    new_population= [current_population[i] for i in selected_indices[:num_elites]]

    # 3. 计算精英方案的位置
    remaining_individuals = len(current_population) - num_elites
    # total_length = len(current_population)
    elite_positions = generate_valid_positions(num_elites, remaining_individuals)

    # 4. 运行 PyGAD 生成新的后代种群
    ga_instance.run()
    offspring_population = ga_instance.population.tolist()
    new_population = offspring_population.copy()  # 用后代填充初始种群，再将精英方案替换到计算好的目标位置上

    # # 5. 将 PyGAD 生成的个体补充到新种群中
    # new_population.extend(offspring_population[:remaining_individuals])

    # 5. 插入精英方案，为了眼动仪控制精英方案之间的距离！=[1,4]
    for idx, pos in enumerate(elite_positions):
        if idx < len(selected_indices) and pos < remaining_individuals:
            new_population[pos] = elite_individuals[idx]

    global previous_elite_solutions  # 再次确保声明为全局变量
    previous_elite_solutions.append(elite_individuals)
    if len(previous_elite_solutions) > 3:
        previous_elite_solutions.pop(0)  # 保持最多两代数据

    # 判断是否连续两代精英方案完全一致
    if len(previous_elite_solutions) == 3:
        gen1, gen2, gen3 = previous_elite_solutions

        # (必要条件)每一代都有3个精英方案
        if len(gen1) == 3 and len(gen2) == 3 and len(gen3) == 3:
            # 将每个方案转为 tuple 并构建成 set 进行比较
            def to_set(generation):
                return set(tuple(ind) for ind in generation)



            set1 = to_set(gen1)
            set2 = to_set(gen2)
            set3 = to_set(gen3)

            # 认知收敛条件1
            if set1 == set2 == set3:
                print("✅ 实验终止条件满足：连续三代有3个相同的精英方案（顺序无关）")
                return [], elite_positions

            # 认知收敛条件2
            # 三代内任意两个方案的余弦距离 < 0.1
            # all_gens = [gen1, gen2, gen3]
            # for gen in all_gens:
            #     # 确保每个世代至少有一个方案可以与其他世代比较
            #     if len(gen) > 0:
            #         distances = calculate_cosine_distances(all_gens)
            #         if all(d < 0.1 for d in distances):
            #             print("✅ 实验终止条件满足：连续三代内发生的修改的余弦距离小于0.1")
            #             return [], elite_positions

    return new_population, elite_positions

# 生成 vase_code 的 SVG
def generate_vase_jpg(vase_code, idx=0):
    # 调用可视化函数生成 base64 编码的 SVG
    jpg_base64 = vis_vase3D(vase_code, idx)

    return jpg_base64

