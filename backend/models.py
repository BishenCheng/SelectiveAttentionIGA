from pydantic import BaseModel
from typing import List, Optional

class VaseCode(BaseModel):
    code: List[int]

class InitializePopulationRequest(BaseModel):
    num_genes: int = 32
    population_size: int = 16

# GazeRecord 类，保证其完整性。
class GazeRecord(BaseModel):
    timestamp: str  # ISO格式时间戳
    source_container: int
    target_container: int  # 格式示例：2
    duration_weight: float  # 毫秒
    is_selected: bool  # 是否发生了选择行为 

# 用于调用的 UserScoresRequest 模型
class UserScoresRequest (BaseModel):
    population: List[List[int]]  # 当前种群的二进制编码
    gaze_records: List[GazeRecord]  # 完整的眼动交互记录
    selected_indices: List[int]  # 从 GazeRecord 中 is_selected=True 的记录提取的目标容器索引（例如 "container_2" → 2）
    ratings: List[int]  # 用户对每个容器的评分

class VaseImageResponse(BaseModel):
    jpg_base64: str  # 存储 base64 编码的 jpg字符串

