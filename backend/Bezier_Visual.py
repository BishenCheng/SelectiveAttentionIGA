import matplotlib
matplotlib.use('Agg')  # AGG模式下不需要显示窗口
import numpy as np
import matplotlib.pyplot as plt
from geomdl import BSpline
from geomdl import utilities
import logging
import svgwrite
import base64
from io import BytesIO,StringIO

# 设置日志等级为 WARNING 或更高
logging.basicConfig(level=logging.WARNING)

# 获取花瓶点
def get_point(vase_code):
    # 确保 vase_code 是一个一维的 numpy 数组
    vase_code = np.array(vase_code).flatten()
    
    # 初始化花瓶点坐标矩阵 (2行9列)
    vase_point = np.zeros((2, 9))
    
    # point_3 的横纵坐标,-Python是从0开始数的
    vase_point[0, 2] = 0.05 * (vase_code[6] * 4 + vase_code[7] * 2 + vase_code[8]) + 2.5
    vase_point[1, 2] = 5.6
     
    # point_1 的横纵坐标
    vase_point[0, 0] = 0.03 * vase_point[0, 2] * (vase_code[0] * 4 + vase_code[1] * 2 + vase_code[2]) + 0.78 * vase_point[0, 2]
    vase_point[1, 0] = 6
    
    # point_2 的横纵坐标
    vase_point[0, 1] = (vase_point[0, 0] + vase_point[0, 2]) / 2
    vase_point[1, 1] = 0.01 * (vase_code[3] * 4 + vase_code[4] * 2 + vase_code[5]) + 5.9
    
    # point_5 的横纵坐标
    vase_point[0, 4] = vase_point[0, 2]
    vase_point[1, 4] = 0.2 * (vase_code[14] * 4 + vase_code[15] * 2 + vase_code[16]) + 4.1
    
    # point_4 的横纵坐标
    vase_point[0, 3] = 0.01 * vase_point[0, 2] * (vase_code[9] * 2 + vase_code[10]) + 1.01 * vase_point[0, 2]
    vase_point[1, 3] = (0.1 * (vase_code[11] * 4 + vase_code[12] * 2 + vase_code[13]) + 0.2) * (vase_point[1, 2] - vase_point[1, 4]) + vase_point[1, 4]
    
    # point_7 的横纵坐标
    vase_point[0, 6] = vase_point[0, 2]
    vase_point[1, 6] = 0.16 * (vase_code[23] * 2 + vase_code[24])
    
    if vase_point[1, 6] > 0:
        # point_6 的纵坐标
        vase_point[1, 5] = (0.05 * (vase_code[20] * 4 + vase_code[21] * 2 + vase_code[22]) + 0.6) * (vase_point[1, 4] - vase_point[1, 6]) + vase_point[1, 6]
    else:
        vase_point[1, 5] = (0.1 * (vase_code[20] * 4 + vase_code[21] * 2 + vase_code[22]) + 0.15) * (vase_point[1, 4] - vase_point[1, 6]) + vase_point[1, 6]
        
    # point_6 的横坐标
    vase_point[0, 5] = (0.08 * (vase_code[17] * 4 + vase_code[18] * 2 + vase_code[19]) + 0.2) * vase_point[0, 2]
    
    # point_9 的横纵坐标
    vase_point[0, 8] = (0.007 * (vase_code[29] * 4 + vase_code[30] * 2 + vase_code[31]) + 0.92) * vase_point[0, 2]
    vase_point[1, 8] = 0
    
    # point_8 的横纵坐标
    vase_point[0, 7] = 0.01 * (vase_code[25] * 2 + vase_code[26]) * vase_point[0, 6] + vase_point[0, 6]
    vase_point[1, 7] = 0.2 * (vase_code[27] * 2 + vase_code[28]) * vase_point[1, 6] + 0.2 * vase_point[1, 6]

    # 将结果转换为列表形式，每个点为[x, y, 0]
    points = [list(vase_point[:, i]) + [0] for i in range(9)]
    
    return points

# 绘制花瓶轮廓为SVG的代码
def vis_vaseSVG(vase_code, idx):
    # 获取控制点（保留原始比例）
    points = [[p[0], p[1]] for p in get_point(vase_code)]  # 忽略 z 坐标

    # 设置偏移量用于居中显示
    offset_x, offset_y = 100, 50

    # 设置画布大小
    canvas_width, canvas_height = 800, 800

    def apply_offset(pt):
        scale = 100
        x = pt[0] * scale + offset_x
        y = canvas_height - pt[1] * scale + offset_y
        return (x, y)

    dwg = svgwrite.Drawing(size=(canvas_width, canvas_height), viewBox="0 0 800 800", preserveAspectRatio="xMidYMid meet")

    # 构建原始路径
    path_data = [
        f"M {apply_offset(points[0])[0]} {apply_offset(points[0])[1]}",
        f"Q {apply_offset(points[1])[0]} {apply_offset(points[1])[1]}, {apply_offset(points[2])[0]} {apply_offset(points[2])[1]}",
        f"Q {apply_offset(points[3])[0]} {apply_offset(points[3])[1]}, {apply_offset(points[4])[0]} {apply_offset(points[4])[1]}",
        f"Q {apply_offset(points[5])[0]} {apply_offset(points[5])[1]}, {apply_offset(points[6])[0]} {apply_offset(points[6])[1]}",
        f"Q {apply_offset(points[7])[0]} {apply_offset(points[7])[1]}, {apply_offset(points[8])[0]} {apply_offset(points[8])[1]}"
    ]
    dwg.add(dwg.path(d=" ".join(path_data), stroke='black', fill='none', stroke_width=3))

    # 计算镜像点（在原始坐标系中镜像）
    mirror_center_x = points[2][0]
    mirrored_points = []
    for p in points:
        mirrored_x = 2 * mirror_center_x - p[0] + 0.7  # 镜像 + 小偏移
        mirrored_y = p[1]
        mirrored_points.append([mirrored_x, mirrored_y])

    # 构建镜像路径
    mirrored_path_data = [
        f"M {apply_offset(mirrored_points[0])[0]} {apply_offset(mirrored_points[0])[1]}",
        f"Q {apply_offset(mirrored_points[1])[0]} {apply_offset(mirrored_points[1])[1]}, "
        f"{apply_offset(mirrored_points[2])[0]} {apply_offset(mirrored_points[2])[1]}",
        f"Q {apply_offset(mirrored_points[3])[0]} {apply_offset(mirrored_points[3])[1]}, "
        f"{apply_offset(mirrored_points[4])[0]} {apply_offset(mirrored_points[4])[1]}",
        f"Q {apply_offset(mirrored_points[5])[0]} {apply_offset(mirrored_points[5])[1]}, "
        f"{apply_offset(mirrored_points[6])[0]} {apply_offset(mirrored_points[6])[1]}",
        f"Q {apply_offset(mirrored_points[7])[0]} {apply_offset(mirrored_points[7])[1]}, "
        f"{apply_offset(mirrored_points[8])[0]} {apply_offset(mirrored_points[8])[1]}"
    ]
    dwg.add(dwg.path(d=" ".join(mirrored_path_data), stroke='black', fill='none', stroke_width=3))

    # 绘制连接线 P1-P1' 和 P9-P9'
    dwg.add(dwg.line(start=apply_offset(points[0]), end=apply_offset(mirrored_points[0]),
                    stroke='black', stroke_width=3))
    dwg.add(dwg.line(start=apply_offset(points[8]), end=apply_offset(mirrored_points[8]),
                    stroke='black', stroke_width=3))

    # 将 SVG 内容写入内存中的文本缓冲区
    buffer = StringIO()  # 使用 StringIO 创建文本缓冲区
    dwg.write(buffer)
    svg_content = buffer.getvalue().encode('utf-8')  # 将字符串编码为字节

    # 将 SVG 内容转换为 base64 编码
    svg_base64 = base64.b64encode(svg_content).decode('utf-8')

    return svg_base64

# 示例调用
# vase_code_example = [0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0]
# vis_vaseSVG(vase_code_example, 0)


def vis_vase3D(vase_code,idx):
    # 获取花瓶点
    points = get_point(vase_code)
    # 镜像点集沿着y轴，并确保在原有曲线的右边且对称
    max_x = max(p[0] for p in points)
    mirrored_points = [[2 * max_x - px - 1 , py , pz] for px, py, pz in points]

    # 创建一个新的贝塞尔曲线实例,设置曲线次数为3 (因为有9个控制点),设置控制点
    original_curve = BSpline.Curve()
    original_curve.degree = 3
    original_curve.ctrlpts = mirrored_points


    offset_x = -1.15  # 瓶子的外径偏移，在-1到-1.4之间比较好
    # 调整控制点的 x 坐标
    original_curve.ctrlpts = [(p[0] + offset_x, p[1]) for p in original_curve.ctrlpts]
    original_curve.knotvector = utilities.generate_knot_vector(original_curve.degree, len(original_curve.ctrlpts)) # 自动生成节点向量

    # 评估曲线上的点
    original_curve.evaluate()
    curve_points = np.array(original_curve.evalpts)

    # 旋转曲线点以创建曲面
    theta = np.linspace(0, 2 * np.pi, 100)
    x = np.outer(curve_points[:, 0], np.cos(theta))
    y = np.outer(curve_points[:, 1], np.ones_like(theta))
    z = np.outer(curve_points[:, 0], np.sin(theta))

    # 创建一个新的图形
    fig = plt.figure(figsize=(2.4, 3))
    ax = fig.add_subplot(111, projection='3d')
    ax.view_init(elev=15, azim=45)

    # 绘制曲面，转一下角度
    x_new = x
    y_new = -z
    z_new = y

    ax.set_box_aspect([np.ptp(x_new), np.ptp(y_new), np.ptp(z_new)])

    surf = ax.plot_surface(x_new, y_new, z_new,color = 'white', alpha=1,linewidth=0)

    # 移除坐标轴
    ax.set_axis_off()
    ax.grid(False)
    plt.subplots_adjust(left=0, right=1, bottom=0, top=1)

    # 将图像保存到内存缓冲区
    buffer = BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0,transparent=True) # transparent=True.需要导出成PNG
    plt.close(fig)

    # 将 SVG 内容转换为 base64 编码
    # svg_content = buffer.getvalue().encode('utf-8')
    # svg_base64 = base64.b64encode(svg_content).decode('utf-8')

    # 将 JPG 内容转换为 base64 编码
    jpg_content = buffer.getvalue()
    jpg_base64 = base64.b64encode(jpg_content).decode('utf-8')

    return jpg_base64
# 示例调用
# vase_code_example = [0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0]
# a=vis_vase3D(vase_code_example,1)
# print(a)
# c2 = [0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0]
# vis_vase2D(c2)