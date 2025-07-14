import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import numpy as np
from services import init_population, evolve_population, generate_vase_jpg
from models import VaseCode, InitializePopulationRequest, UserScoresRequest, VaseImageResponse,EndRequest
from datetime import datetime  # 用于生成时间戳
import json  # 用于 JSON 操作

# 导入异步处理模块
import asyncio
from concurrent.futures import ProcessPoolExecutor
#import functools


# 启动方式：uvicorn main:app --reload --host 127.0.0.1 --port 8000
app = FastAPI()


# 设置日志等级为 WARNING 或更高
logging.basicConfig(level=logging.WARNING)

origins = [
    "http://localhost:3000",  # 对应React服务器
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 存储当前种群状态（可以替换为 Redis 或数据库）
current_population = []

# 初始化种群并生成 SVG 文件
# @app.post("/initialize/")
# async def initialize_population(request: InitializePopulationRequest):
#     global current_population
#     num_genes = request.num_genes
#     population_size = request.population_size
#
#     # 初始化种群
#     current_population = init_population(num_genes, population_size)
#
#     # 为每个个体随机分配容器节点
#     container_names = [f"container_{i}" for i in range(0, 15)]
#     np.random.shuffle(container_names)
#
#     # 保存初始化的二进制编码到数据库
#     # save_binary_to_node_mapping(current_population,container_names)
#
#     # 为每个种群成员生成 base64 编码的 SVG
#     new_base64_list = []
#     for idx, vase_code in enumerate(current_population):
#         jpg_base64 = generate_vase_jpg(vase_code, idx)
#         new_base64_list.append(jpg_base64)
#
#     return {
#         "message": "Population initialized successfully",
#         "jpg_base64": new_base64_list, #  返回 base64 编码的 SVG 列表
#         "population": current_population, # 返回二进制编码列表
#     }

@app.post("/initialize/")
async def initialize_population(request: InitializePopulationRequest):
    global current_population
    num_genes = request.num_genes
    population_size = request.population_size

    # 初始化种群
    current_population = init_population(num_genes, population_size)

    # 为每个个体随机分配容器节点
    container_names = [f"container_{i}" for i in range(0, 15)]
    np.random.shuffle(container_names)

    # 保存初始化的二进制编码到数据库
    # save_binary_to_node_mapping(current_population,container_names)

    # 使用异步生成 base64 编码的 SVG 列表
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as pool:
        tasks = [loop.run_in_executor(pool, generate_vase_jpg, vase_code, idx) for idx, vase_code in enumerate(current_population)]
        new_base64_list = await asyncio.gather(*tasks)

    return {
        "message": "Population initialized successfully",
        "jpg_base64": new_base64_list, #  返回 base64 编码的 SVG 列表
        "population": current_population, # 返回二进制编码列表
    }

# 根据用户评分迭代生成新一代种群并生成 SVG 文件
# @app.post("/evolve/")
# async def evolve_population_route(request: UserScoresRequest):  # 使用新的请求模型
#     global current_population
#     current_population = request.population
#     gaze_records = request.gaze_records  # 获取注视记录
#     selected_indices = request.selected_indices  # 获取选中索引
#
#     # ---------------- 新增：保存 本地的JSON 备份 ----------------
#     # 创建存储目录（如果不存在）
#     save_dir = "json_records"
#     os.makedirs(save_dir, exist_ok=True)
#
#     # 生成时间戳文件名（格式：YYYYMMDDHHMMSS.json）
#     current_time = datetime.now().strftime("%Y%m%d%H%M%S")
#     file_path = os.path.join(save_dir, f"{current_time}.json")
#
#     # 将请求数据序列化为 JSON 并保存
#     with open(file_path, "w", encoding="utf-8") as f:
#         # 使用 request.dict() 获取模型的字典数据，indent=2 美化格式
#         json.dump(request.dict(), f, ensure_ascii=False, indent=2)
#     # -----------------------------------------------------
#
#     # 这里可以添加对gaze_records的处理逻辑（如存储、分析等）
#     print("接收到的注视记录:", gaze_records)
#     print("用户选中的索引:", selected_indices)
#
#     # 原遗传算法逻辑（需要调整evolve_population参数）
#     new_population, elite_positions  = evolve_population(
#         gaze_records=gaze_records,  # 传递注视记录
#         selected_indices=selected_indices,  # 将选中索引作为精英保留
#         current_population=current_population
#     )
#
#     # 保存新种群的二进制编码到数据库
#     # save_binary_to_node_mapping(new_population)
#
#     # 生成新SVG...（保持原逻辑）
#     new_base64_list = []
#     for idx, vase_code in enumerate(new_population):
#         jpg_base64 = generate_vase_jpg(vase_code, idx)
#         new_base64_list.append(jpg_base64)
#
#     return {
#         "message": "Population evolved successfully",
#         "new_jpg": new_base64_list,
#         "new_population": new_population,
#         "elite_positions":elite_positions
#     }
@app.post("/evolve/")
async def evolve_population_route(request: UserScoresRequest):  # 使用新的请求模型
    global current_population
    current_population = request.population
    gaze_records = request.gaze_records  # 获取注视记录
    selected_indices = request.selected_indices  # 获取选中索引
    ratings= request.ratings

    # ---------------- 新增：保存 本地的JSON 备份 ----------------
    # 创建存储目录（如果不存在）
    save_dir = "json_records"
    os.makedirs(save_dir, exist_ok=True)

    # 生成时间戳文件名（格式：YYYYMMDDHHMMSS.json）
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = os.path.join(save_dir, f"{current_time}.json")

    # 将请求数据序列化为 JSON 并保存
    with open(file_path, "w", encoding="utf-8") as f:
        # 使用 request.dict() 获取模型的字典数据，indent=2 美化格式
        json.dump(request.dict(), f, ensure_ascii=False, indent=2)
    # -----------------------------------------------------

    # 这里可以添加对gaze_records的处理逻辑（如存储、分析等）
    print("接收到的注视记录:", gaze_records)
    print("用户选中的索引:", selected_indices)

    # 遗传算法逻辑
    new_population  = evolve_population(
        ratings=ratings,
        gaze_records=gaze_records,  # 传递注视记录
        selected_indices=selected_indices,  # 将选中索引作为精英保留
        current_population=current_population
    )

    # 保存新种群的二进制编码到数据库
    # save_binary_to_node_mapping(new_population)

    # 使用异步生成 base64 编码的 SVG 列表
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as pool:
        tasks = [loop.run_in_executor(pool, generate_vase_jpg, vase_code, idx) for idx, vase_code in enumerate(new_population)]
        new_base64_list = await asyncio.gather(*tasks)

    return {
        "message": "Population evolved successfully",
        "new_jpg": new_base64_list,
        "new_population": new_population,
        # "elite_positions":elite_positions
    }

@app.post("/end/")
async def end_experiment(request: EndRequest):
    # ---------------- 新增：保存 本地的JSON 备份 ----------------
    # 创建存储目录（如果不存在）
    save_dir = "json_records"
    os.makedirs(save_dir, exist_ok=True)

    # 生成时间戳文件名（格式：YYYYMMDDHHMMSS.json）
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    file_path = os.path.join(save_dir, f"{current_time}_end.json")

    # 将请求数据序列化为 JSON 并保存
    with open(file_path, "w", encoding="utf-8") as f:
        # 使用 request.dict() 获取模型的字典数据，indent=2 美化格式
        json.dump(request.dict(), f, ensure_ascii=False, indent=2)
    # -----------------------------------------------------

    print("接收到的终止信息:", request)
    return {
        "message": "Experiment ended successfully",
    }

# 获取 jpg 文件
@app.post("/generate-svg/")
def generate_svg(vase_code: VaseCode):
    # 调用服务函数生成 base64 编码的 SVG
    jpg_base64 = generate_vase_jpg(vase_code.code)
    return VaseImageResponse(jpg_base64=jpg_base64)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}