import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np  # Add NumPy import
# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
plt.rcParams['font.size'] = 18  # 设置默认字体大小

# ========== 数据准备 ==========
# 大类数据
main_categories = ['药学', '基础医学', '临床医学']
main_percent = [15.4, 31, 53.6]  # 单位：百分比

# 子类数据（占所属大类的比例）
sub_categories = {
    '药学': {
        '药物化学': 35,
        '药理学': 30,
        '药剂学': 25,
        '临床药学': 10
    },
    '基础医学': {
        '解剖学': 30,
        '生理学': 25,
        '病理学': 25,
        '生物化学': 20
    },
    '临床医学': {
        '内科': 40,
        '外科': 30,
        '妇产科': 15,
        '儿科': 10,
        '急诊科': 5
    }
}

# ========== 数据处理 ==========
# 计算子类全局占比
sub_data = []
colors = []
explode = []
labels = []

# 使用更专业的配色方案
pharmacy_colors = ['#FF6B6B', '#FF8E8E', '#FFA6A6', '#FFC2C2']  # 药学渐变色
basic_colors = ['#4E79A7', '#6B8EB8', '#86A0C5', '#A1B2D6']     # 基础医学渐变色
clinical_colors = ['#59A14F', '#76B26A', '#8FC185', '#A8D1A0', '#C3E1BD']  # 临床医学渐变色 - 增加一个颜色

# 药学子类
for i, (sub, ratio) in enumerate(sub_categories['药学'].items()):
    global_ratio = main_percent[0] * ratio / 100
    sub_data.append(global_ratio)
    labels.append(f"{sub}\n({global_ratio:.1f}%)")
    colors.append(pharmacy_colors[i])
    explode.append(0.02)

# 基础医学子类
for i, (sub, ratio) in enumerate(sub_categories['基础医学'].items()):
    global_ratio = main_percent[1] * ratio / 100
    sub_data.append(global_ratio)
    labels.append(f"{sub}\n({global_ratio:.1f}%)")
    colors.append(basic_colors[i])
    explode.append(0.02)

# 临床医学子类
for i, (sub, ratio) in enumerate(sub_categories['临床医学'].items()):
    global_ratio = main_percent[2] * ratio / 100
    sub_data.append(global_ratio)
    labels.append(f"{sub}\n({global_ratio:.1f}%)")
    colors.append(clinical_colors[i])
    explode.append(0.02)

# ========== 可视化实现 ==========
plt.figure(figsize=(18, 12), facecolor='white')  # 适当加宽画布

# 外层：子类细分饼图
wedges, texts = plt.pie(
    sub_data,
    labels=labels,  # 直接用labels
    labeldistance=1.18,  # 稍微拉远标签
    colors=colors,
    explode=explode,
    wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2),
    startangle=90,
    textprops={'fontsize':18, 'fontweight':'bold'}  # 不加bbox
)

# 移除手动添加标签和延长线的代码
# 内层：大类环形图
main_colors = ['#E63946', '#1D3557', '#2A9D8F']  # 更鲜明的对比色
inner_wedges, inner_texts = plt.pie(
    main_percent,
    labels=None,  # 先不添加标签，后面手动添加
    colors=main_colors,
    wedgeprops=dict(width=0.4, edgecolor='white', linewidth=3),
    startangle=90,
    radius=0.6
)

# 手动添加内层标签
for i, p in enumerate(inner_wedges):
    ang = (p.theta2 - p.theta1) / 2. + p.theta1
    x = np.cos(np.deg2rad(ang))
    y = np.sin(np.deg2rad(ang))
    
    # 添加大类标签
    plt.annotate(
        f"{main_categories[i]}\n{main_percent[i]}%",
        xy=(x*0.4, y*0.4),  # 内环中心位置
        ha='center',
        va='center',
        fontsize=18,  # 放大字体
        fontweight='bold',
        color='white'
    )

# 添加中心注释
plt.text(0, 0, "文献总量\n200篇",
         ha='center', va='center',
         fontsize=18, fontweight='bold',  # 放大字体
         bbox=dict(facecolor='white', alpha=0.9, boxstyle="round,pad=0.5", ec="gray"))

# 创建分组图例
from matplotlib.patches import Patch

legend_elements = []
legend_labels = []

# 药学图例组
legend_elements.append(Patch(facecolor=main_colors[0], edgecolor='white', label='药学'))
legend_labels.append(f"药学 ({main_percent[0]}%)")
for i, (sub, ratio) in enumerate(sub_categories['药学'].items()):
    global_ratio = main_percent[0] * ratio / 100
    legend_elements.append(Patch(facecolor=pharmacy_colors[i], edgecolor='white', label=sub))
    legend_labels.append(f"  {sub}: {global_ratio:.1f}%")

# 基础医学图例组
legend_elements.append(Patch(facecolor=main_colors[1], edgecolor='white', label='基础医学'))
legend_labels.append(f"\n基础医学 ({main_percent[1]}%)")
for i, (sub, ratio) in enumerate(sub_categories['基础医学'].items()):
    global_ratio = main_percent[1] * ratio / 100
    legend_elements.append(Patch(facecolor=basic_colors[i], edgecolor='white', label=sub))
    legend_labels.append(f"  {sub}: {global_ratio:.1f}%")

# 临床医学图例组
legend_elements.append(Patch(facecolor=main_colors[2], edgecolor='white', label='临床医学'))
legend_labels.append(f"\n临床医学 ({main_percent[2]}%)")
for i, (sub, ratio) in enumerate(sub_categories['临床医学'].items()):
    global_ratio = main_percent[2] * ratio / 100
    legend_elements.append(Patch(facecolor=clinical_colors[i], edgecolor='white', label=sub))
    legend_labels.append(f"  {sub}: {global_ratio:.1f}%")

# 添加美化后的图例
plt.legend(
    legend_elements,
    legend_labels,
    title="分类详情",
    loc="center left",
    bbox_to_anchor=(1.05, 0.5),  # 右移，确保完整显示
    fontsize=20,  # 放大字体
    title_fontsize=20,  # 放大标题字体
    frameon=True,
    facecolor='white',
    edgecolor='#dddddd',
    shadow=True
)

plt.title("医学文献分类细目分析",
          fontsize=24, pad=50, fontweight='bold', loc='center')

plt.axis('equal')

plt.subplots_adjust(top=0.80, bottom=0.12, right=0.78)  # top减小，bottom增大，整体下移

# # 添加数据来源注释
# plt.annotate('数据来源：医学文献统计分析 2023',
#              xy=(1.0, -0.05),
#              xycoords='axes fraction',
#              fontsize=10,
#              ha='right',
#              color='#555555')

# 保存高清图像
plt.savefig('medical_literature_distribution.png',
            dpi=300,
            bbox_inches='tight',
            facecolor='white')  # 这里改为纯白

plt.show()