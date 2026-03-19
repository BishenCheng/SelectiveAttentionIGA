import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
from Bezier_Visual import get_point


# 余弦距离 = 1 - 余弦相似度
def cosine_distance(v1, v2):
    points1 = get_point(v1)
    points2 = get_point(v2)

    vec1 = np.array(points1).flatten() # 展平，二维数组——列表。
    vec2 = np.array(points2).flatten()

    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 1.0
    similarity = np.dot(vec1, vec2) / (norm1 * norm2)
    return 1.0  - similarity

def build_graph(records):
    """
    构建有向加权多重图。

    参数:
    - records: 包含眼动记录的列表，每个记录是 GazeRecord 对象。
    """
    G = nx.MultiDiGraph()
    for record in records:
        G.add_edge(
            record.source_container,
            record.target_container,
            key=record.timestamp,
            duration_weight=record.duration_weight,
            is_selected=record.is_selected
        )
    return G


# 本文主旨算法：Attention Rank，针对注视轨迹的有向多重图排序，
def attention_rank(G, population,alpha_post=0.8, alpha_pre=0.7, beta_factor=1.0, max_iter=10, tol=1e-6):
    """
    计算AttentionRank中心性值。

    参数:
    - G: 由build_graph生成的MultiDiGraph
    - alpha_post: 出边传播衰减因子 (0 < alpha_post < 1)
    - alpha_pre: 入边传播衰减因子 (0 < alpha_pre < 1)
    - beta_factor: 初始节点的度中心性放大系数
    - max_iter: 最大迭代次数
    - tol: 收敛阈值（中心性变化小于该值则停止迭代）

    返回:
    - C: 字典，键为节点名，值为中心性值
    """

    # 步骤1: 初始化中心性值为0——必须选一个方案
    C = {node: 0.0 for node in G.nodes}

    # 找出所有被选中的节点（is_selected=True的边的目标节点）——改成精英方案？
    selected_nodes = set()
    for u, v, k, data in G.edges(keys=True, data=True):
        if data["is_selected"]:
            selected_nodes.add(v)

    # 步骤2: 设置初始节点的度中心性（β）
    for node in selected_nodes:
        degree = G.out_degree(node) + G.in_degree(node)  # 总度数
        C[node] = beta_factor * (degree / (G.number_of_nodes() - 1))  # 归一化度中心性

    # 步骤3: 迭代计算传播中心性
    for _ in range(max_iter):
        C_new = C.copy()
        delta = 0.0  # 收敛判断变量

        # 出边传播（α_post）
        for u, v, k, data in G.edges(keys=True, data=True):
            weight = data["duration_weight"]  # 注视时间
            alpha = alpha_post ** (1 + len(nx.shortest_path(G, u, v)))  # 路径长度惩罚
            C_new[v] += C[u] * weight * alpha

        # 入边传播（α_pre）
        for u, v, k, data in G.edges(keys=True, data=True):
            # 反向边：v -> u
            if G.has_edge(v, u):
                for rev_k in G[v][u]:
                    rev_data = G[v][u][rev_k]

                    # 获取 source_container 和 target_container 的基因编码
                    # population = records["population"]
                    source_gene = population[v]
                    target_gene = population[u]

                    # 计算距离衰减（余弦距离）
                    distance = cosine_distance(source_gene, target_gene)
                    alpha = alpha_pre ** (1 + len(nx.shortest_path(G, v, u)))  # 路径长度惩罚
                    C_new[u] += C[v] * distance * alpha

        # 计算中心性变化
        for node in C:
            delta += abs(C_new[node] - C[node])
        C = C_new

        if delta < tol:
            break

    # 获取所有值并计算最小值和最大值
    values = np.array(list(C.values()))
    C_min = values.min()
    C_max = values.max()

    # 映射到 1-10 范围内（默认为1）
    C_mapped = {key: 1.0 + 9.0 * (value - C_min) / (C_max - C_min) for key, value in C.items()}

    return C_mapped
# SA Centerality
def a_rank_dual_alpha(G: nx.MultiDiGraph, 
                        alpha_gaze: float = 0.1, 
                        alpha_select: float = 0.75):
    """
    计算双Alpha中心性，区分“注视”和“选择”行为。

    此模型为两种行为路径设置不同的影响力衰减系数，以更精确地建模认知过程。
    - "注视"路径 (探索性): 使用较小的alpha_gaze，影响力衰减快。
    - "选择"路径 (确定性): 使用较大的alpha_select，影响力衰减慢，路径依赖性强。

    Args:
        G (nx.MultiDiGraph): 包含注视行为的有向多重图。
                               边属性应包含 'duration_weight' 和 'selected_indces' (bool)。
        alpha_gaze (float, optional): "注视"行为路径的衰减系数。默认为 0.1。
        alpha_select (float, optional): "选择"行为路径的衰减系数。默认为 0.85。

    Returns:
        dict: 一个字典，映射每个方案(节点ID)到其原始（未归一化）的重要性得分。
    """
    # --- 步骤 0: 初始化 ---
    if not G.nodes():
        return {}

    nodes = sorted(list(G.nodes()))
    n_nodes = len(nodes)
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    # --- 步骤 1: 构建基础吸引力向量 e (基于入度) ---
    in_degrees = np.array([G.in_degree(n) for n in nodes], dtype=float)
    total_in_degree = np.sum(in_degrees)
    if total_in_degree > 0:
        e_vec = in_degrees / total_in_degree
    else:
        e_vec = np.ones(n_nodes) / n_nodes

    # --- 步骤 2: 分别构建 "注视" 和 "选择" 的影响力矩阵 ---
    A_gaze = np.zeros((n_nodes, n_nodes), dtype=float)
    A_select = np.zeros((n_nodes, n_nodes), dtype=float)

    for u, v, data in G.edges(data=True):
        u_idx, v_idx = node_to_idx[u], node_to_idx[v]
        duration = data.get('duration_weight', 0.0)
        # 假设您的属性名为 'selected_indces'
        is_selection = data.get('selected_indces', False)

        if is_selection:
            A_select[u_idx, v_idx] += duration
        else:
            A_gaze[u_idx, v_idx] += duration
            
    # --- 步骤 3: 分别对两个矩阵进行列归一化 ---
    # 归一化 A_gaze
    gaze_col_sums = A_gaze.sum(axis=0)
    gaze_col_sums[gaze_col_sums == 0] = 1
    A_gaze_norm = A_gaze / gaze_col_sums
    
    # 归一化 A_select
    select_col_sums = A_select.sum(axis=0)
    select_col_sums[select_col_sums == 0] = 1
    A_select_norm = A_select / select_col_sums

    # --- 步骤 4: 求解双Alpha线性方程 ---
    # M = I - alpha_gaze * A_gaze.T - alpha_select * A_select.T
    I = np.identity(n_nodes)
    M = I - alpha_gaze * A_gaze_norm.T - alpha_select * A_select_norm.T

    try:
        scores_vec = np.linalg.solve(M, e_vec)
    except np.linalg.LinAlgError:
        print("警告: 双Alpha模型矩阵是奇异的。返回基础吸引力得分。")
        scores_vec = e_vec

    # --- 步骤 5: 格式化输出 ---
    final_scores = {node: score for node, score in zip(nodes, scores_vec)}

    return final_scores

def minmax_scale(scores_array: np.ndarray) -> np.ndarray:
    """
    使用 NumPy 实现 Min-Max 归一化，将分数缩放到 [0, 1] 区间。

    Args:
        scores_array (np.ndarray): 包含原始分数的 NumPy 数组。

    Returns:
        np.ndarray: 归一化后的分数数组。
    """
    min_val = np.min(scores_array)
    max_val = np.max(scores_array)

    # 处理所有值都相同（分母为0）的边缘情况
    if max_val == min_val:
        return np.zeros_like(scores_array, dtype=float)

    return (scores_array - min_val) / (max_val - min_val)

def hub_rank(G: nx.MultiDiGraph,
             records: dict,
             centrality_type: str = 'composite_eigenvector',
             delta: float = 0.5,
             alpha_pagerank: float = 0.85):
    """
    根据指定的权重类型和中心性算法，计算方案的重要性得分。

    Args:
        G (nx.MultiDiGraph): 包含注视行为的有向多重图。
        records (dict): 包含语义编码 'population' 的字典。
        centrality_type (str): 指定要计算的中心性类型。可选值:
            - 'duration_in_degree':   基于注视时长的加权入度。
            - 'semantic_in_degree':   基于语义相似度的加权入度。
            - 'eigenvector_centrality': 纯拓扑的特征向量中心性 (不加权)。
            - 'semantic_freq_eigenvector': 频率调制的语义特征向量中心性 (权重 = 频率 * 相似度)。
            - 'duration_eigenvector':    基于注视时长的加权特征向量中心性。
            - 'composite_eigenvector': (新增)基于复合权重(时长+次数)的特征向量中心性。
            - delta (float): 用于'composite_eigenvector'，平衡时长和次数的权重。
            默认为 'semantic_in_degree'。

    Returns:
        dict: 一个字典，映射每个方案(节点ID)到其归一化的最终重要性得分。
    """
    if not G.nodes():
        return {}

    nodes = sorted(list(G.nodes()))
    

    # --- 步骤 1: 构建一个带多种预计算权重的简单有向图 H ---
    # H = nx.DiGraph()
    # H.add_nodes_from(nodes)
    #
    # similarity_matrix = np.zeros((len(semantic_vectors), len(semantic_vectors)))
    # for i in range(len(semantic_vectors)):
    #     for j in range(i, len(semantic_vectors)):
    #         vec_i, vec_j = semantic_vectors[i], semantic_vectors[j]
    #         sim = 0.0 if np.all(vec_i == 0) or np.all(vec_j == 0) else 1 - cosine(vec_i, vec_j)
    #         similarity_matrix[i, j] = similarity_matrix[j, i] = sim
    #
    # for u, v in G.edges():
    #     if not H.has_edge(u, v):
    #         total_duration = sum(data.get('duration_weight', 0.0) for data in G.get_edge_data(u, v).values())
    #         semantic_sim = similarity_matrix[u, v]
    #         count = G.number_of_edges(u, v)
    #         # 新增的“频率调制语义权重”
    #         semantic_freq_weight = count * semantic_sim
    #         H.add_edge(u, v,
    #                    duration_weight=total_duration,
    #                    semantic_weight=semantic_sim,
    #                    semantic_freq_weight=semantic_freq_weight)
    # --- 步骤 1: 构建一个带多种预计算权重的简单有向图 H ---
    # (此部分逻辑不变)
    H = nx.DiGraph()
    H.add_nodes_from(nodes)

    # --- 预计算所有边的时长和次数，用于后续归一化 ---
    edge_metrics = {}
    for u, v in G.edges():
        if (u, v) not in edge_metrics:
            total_duration = sum(data.get('duration_weight', 0.0)
                                 for data in G.get_edge_data(u, v).values())
            count = G.number_of_edges(u, v)
            edge_metrics[(u,v)] = {'duration': total_duration, 'count': count}

    # 提取所有时长和次数用于归一化
    all_durations = np.array([m['duration'] for m in edge_metrics.values()])
    all_counts = np.array([m['count'] for m in edge_metrics.values()])

    norm_durations = minmax_scale(all_durations)
    norm_counts = minmax_scale(all_counts)

    # 将归一化后的值放回字典
    for i, (u, v) in enumerate(edge_metrics.keys()):
        edge_metrics[(u, v)]['norm_duration'] = norm_durations[i]
        edge_metrics[(u, v)]['norm_count'] = norm_counts[i]

    # 将权重添加到图H
    for (u, v), metrics in edge_metrics.items():
        composite_weight = delta * metrics['norm_duration'] + (1 - delta) * metrics['norm_count']
        H.add_edge(u, v,
                   duration_weight=metrics['duration'],
                   composite_weight=composite_weight)



    # --- 步骤 2: 根据 centrality_type 计算中心性 ---
    scores = {node: 0.0 for node in nodes}

    if centrality_type == 'duration_in_degree':
        for node in nodes:
            scores[node] = H.in_degree(node, weight='duration_weight')

    elif centrality_type == 'eigenvector_centrality':
        # 不使用任何权重，纯粹基于连接拓扑
        try:
            # 在原始多重图 G 上计算，nx 会自动将平行边数量作为权重
            scores = nx.eigenvector_centrality_numpy(G)
        except TypeError:
            # 回退机制，应对小图问题
            try:
                scores = nx.eigenvector_centrality(G, max_iter=1000)
            except Exception:
                scores = {node: 0.0 for node in nodes}


    elif centrality_type == 'duration_eigenvector':
        # 新增的类型：使用注视时长作为权重计算特征向量中心性
        try:
            scores = nx.eigenvector_centrality_numpy(H, weight='duration_weight')
        except TypeError:
            try:
                scores = nx.eigenvector_centrality(H, weight='duration_weight', max_iter=1000)
            except Exception:
                scores = {node: 0.0 for node in nodes}


    elif centrality_type == 'composite_eigenvector':
        # 新增类型：使用复合权重计算EC
        try:
            scores = nx.eigenvector_centrality_numpy(H, weight='composite_weight')
        except Exception:
            scores = {node: 0.0 for node in nodes}

    else:
        raise ValueError("无效的 'centrality_type'。")

    

    # --- 步骤 3: 归一化并返回结果 ---
    raw_scores = np.array([scores.get(n, 0.0) for n in nodes])
    normalized_scores_arr = minmax_scale(raw_scores)
    final_scores = {node: score for node, score in zip(nodes, normalized_scores_arr.flatten())}

    return final_scores

# \alpha 中心性，节点的“基础吸引力”和“影响力传播”
def a_rank(G: nx.MultiDiGraph, alpha: float = 0.85):
    """
    计算基于Alpha中心性的方案重要性得分。

    该模型融合了节点的“基础吸引力”（由访问次数定义）和节点间的“影响力传播”（由注视时长定义）。
    它实现了 x = (I - alpha * A_T)^-1 * e 的计算，其中：
    - e: 基于节点入度（访问次数）的基础吸引力向量。
    - A: 基于总注视时长的加权邻接矩阵，代表影响力传播路径。
    - alpha: 影响力衰减系数，控制路径依赖的程度。

    Args:
        G (nx.MultiDiGraph): 包含注视行为的有向多重图。
                               其边应有 'duration_weight' 属性。
        alpha (float, optional): 影响力衰减系数，默认为 0.1。
                                 一个较小的值会更侧重于节点自身的基础吸引力。

    Returns:
        dict: 一个字典，映射每个方案(节点ID)到其原始（未归一化）的重要性得分。
    """
    # --- 步骤 0: 初始化和健壮性检查 ---
    if not G.nodes():
        return {}

    nodes = sorted(list(G.nodes()))
    n_nodes = len(nodes)
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    # --- 步骤 1: 构建基础吸引力向量 e (基于入度/访问次数) ---
    degrees = np.array([G.degree(n) for n in nodes], dtype=float)

    # 对 e 进行归一化，使其成为一个概率分布（和为1）
    total_degree = np.sum(degrees)
    if total_degree > 0:
        e_vec = degrees / total_degree
    else:
        # 如果图中没有边，则所有节点吸引力均等
        e_vec = np.ones(n_nodes) / n_nodes

    # --- 步骤 2: 构建影响力传播矩阵 A (基于总注视时长) ---
    # 使用numpy构建矩阵比networkx的中间图更高效
    A = np.zeros((n_nodes, n_nodes), dtype=float)
    for u, v, data in G.edges(data=True):
        # 将u,v映射到矩阵索引
        u_idx, v_idx = node_to_idx[u], node_to_idx[v]
        duration = data.get('duration_weight', 0.0)
        # 注意：邻接矩阵 A[i, j] 代表从 i 到 j 的边
        A[u_idx, v_idx] += duration

    # 对 A 进行列归一化，消除绝对时长带来的尺度偏差
    # 这使得模型更稳健，alpha的作用更纯粹
    col_sums = A.sum(axis=0)
    # 防止除以零
    col_sums[col_sums == 0] = 1
    A_norm = A / col_sums

    # --- 步骤 3: 求解 Alpha Centrality 线性方程 ---
    # 我们要求解 (I - alpha * A_norm.T) * x = e
    # 这是形如 M * x = b 的线性方程组
    I = np.identity(n_nodes)
    M = I - alpha * A_norm.T

    try:
        # 使用np.linalg.solve求解，比直接求逆更稳定、更高效
        scores_vec = np.linalg.solve(M, e_vec)
    except np.linalg.LinAlgError:
        # 如果矩阵M是奇异的（通常在alpha设置不当或图结构特殊时发生）
        # 返回一个基于基础吸引力的得分作为回退
        print("警告: 矩阵是奇异的，无法求解Alpha Centrality。返回基础吸引力得分。")
        scores_vec = e_vec

    # --- 步骤 4: 格式化输出，不进行归一化 ---
    # 将计算出的得分向量映射回节点ID
    final_scores = {node: score for node, score in zip(nodes, scores_vec)}

    return final_scores
# 可视化
def visualize_gaze_graph(G):
    """
    可视化眼动图，节点按4x4网格布局，边的透明度与权重相关。
    修改点：当两节点间存在多条边时，使用不同弧度的曲线绘制，避免边重叠
    """
    # 1. 生成 4x4 网格布局的节点坐标
    pos = {}
    for i in range(16):  # i即为容器的整数索引（0-15）
        x = i % 4  # 列
        y = 3- (i // 4)  # 行
        pos[i] = (x, y)  # 修改点：节点键改为整数

    # 2. 提取边的权重并归一化（逻辑不变）
    edges = list(G.edges(data=True))
    weights = [data["duration_weight"] for u, v, data in edges]
    min_weight = min(weights)
    max_weight = max(weights)
    alphas = [(w - min_weight) / (max_weight - min_weight) for w in weights]

    # 3. 创建画布（逻辑不变）
    plt.figure(figsize=(10, 10))

    # 4. 绘制节点（节点标签为整数索引）
    # 计算度中心性（逻辑不变）
    out_centrality = nx.out_degree_centrality(G)
    in_centrality = nx.in_degree_centrality(G)
    degree_centrality = {node: out_centrality[node] + in_centrality[node] for node in G.nodes}

    # 计算总入边注视时间（逻辑不变）
    node_in_duration = defaultdict(int)
    for u, v, data in G.edges(data=True):
        node_in_duration[v] += data["duration_weight"]

    # 归一化节点大小和透明度（逻辑不变）
    max_size = 2500
    min_size = 500
    node_sizes = [min_size + (degree_centrality[node] * (max_size - min_size)) for node in G.nodes]

    max_alpha_duration = max(node_in_duration.values(), default=1)
    node_alphas = [node_in_duration[node] / max_alpha_duration if node in node_in_duration else 0.5 for node in G.nodes]

    node_colors = [(0.8, 0.6, 1, alpha) for alpha in node_alphas]

    # 绘制节点（节点键为整数，标签自动显示为整数）
    nx.draw_networkx_nodes(
        G,
        pos,
        node_size=node_sizes,
        node_color=node_colors,
        label="Container"
    )

    # 5. 绘制边（逐个处理，支持多重边）
    # 新增多边统计逻辑
    edges = list(G.edges(data=True))
    edge_counts_total = defaultdict(int)
    for u, v, data in edges:
        edge_counts_total[(u, v)] += 1  # 统计每个节点对的边数量

    edge_positions = defaultdict(int)  # 跟踪各节点对的边绘制顺序

    # 修改边绘制逻辑
    for i, (u, v, data) in enumerate(edges):
        alpha = alphas[i]
        total = edge_counts_total[(u, v)]
        current_pos = edge_positions[(u, v)]
        edge_positions[(u, v)] += 1

        # 多边时启用曲线绘制
        if total >= 2:
            # 动态计算弧度（交替正负方向）
            rad = 0.2 * (current_pos + 1) * (-1 if current_pos % 2 else 1)
            connectionstyle = f'arc3,rad={rad}'
        else:
            connectionstyle = 'arc3'  # 单边保持直线

        nx.draw_networkx_edges(
            G,
            pos,
            edgelist=[(u, v)],
            width=5,
            alpha=alpha,
            edge_color="green",
            arrows=True,
            arrowsize=15,
            connectionstyle=connectionstyle  # 添加曲线样式参数
        )

    # 6. 添加节点标签
    nx.draw_networkx_labels(G, pos, font_size=20,font_color="black", font_family="sans-serif",font_weight="heavy")

    # 7. 图形设置
    plt.title("Eye Movement Graph with 4x4 Grid Layout", fontsize=14)
    plt.axis("off")  # 隐藏坐标轴
    plt.tight_layout()
    plt.show()


