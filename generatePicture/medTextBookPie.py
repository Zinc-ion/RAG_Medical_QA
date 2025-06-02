import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 直接定义有数据的医学教科书（单位：MB）
book_names = [
    '免疫学', 
    'ICU主治医师手册', 
    '急症内科学', 
    '临床营养学',
    '内科鉴别诊断学', 
    '内科治疗指南', 
    '精神病学',
    '临床药物治疗学', 
    '药理学'
]

book_sizes = [
    41.7,    # 免疫学
    37.8,    # ICU主治医师手册
    84.2,    # 急症内科学
    4.65,    # 临床营养学
    76.8,    # 内科鉴别诊断学
    46.5,    # 内科治疗指南
    3.58,    # 精神病学
    4.23,    # 临床药物治疗学
    7.06     # 药理学
]

# 定义每本书对应的分类
book_categories = [
    '基础医学',    # 免疫学
    '临床医学',    # ICU主治医师手册
    '临床医学',    # 急症内科学
    '临床医学',    # 临床营养学
    '临床医学',    # 内科鉴别诊断学
    '临床医学',    # 内科治疗指南
    '临床医学',    # 精神病学
    '药学',        # 临床药物治疗学
    '药学'         # 药理学
]

# 计算百分比
total = sum(book_sizes)
percentages = [round((size/total)*100, 1) for size in book_sizes]

# 绘制高级饼图
plt.figure(figsize=(14, 10))

# 使用更丰富的配色方案
colors = plt.cm.tab20(range(len(book_names)))

# 确定哪些扇区需要使用引导线（小于5%的扇区）
small_sectors = [i for i, p in enumerate(percentages) if p < 5]
explode = [0.1 if i in small_sectors else 0 for i in range(len(book_names))]

# 绘制饼图 - 对小扇区使用引导线
wedges, _ = plt.pie(
    book_sizes,
    labels=None,  # 先不添加标签，后面手动添加
    colors=colors,
    autopct=None,  # 先不添加百分比，后面手动添加
    pctdistance=0.85,
    startangle=90,
    explode=explode,
    wedgeprops={
        'edgecolor': 'white',
        'linewidth': 1.2,
    }
)

# 手动添加标签和百分比，避免重叠
for i, wedge in enumerate(wedges):
    ang = (wedge.theta2 - wedge.theta1) / 2. + wedge.theta1
    x = np.cos(np.deg2rad(ang))
    y = np.sin(np.deg2rad(ang))
    
    # 只为大扇区添加标签和百分比（小于5%的扇区不添加标签）
    if i not in small_sectors:
        # 对于大扇区，直接在扇区上添加标签
        ha = 'left' if x < 0 else 'right'
        distance = 1.3  # 标签距离
        
        # 添加标签
        plt.annotate(
            book_names[i], 
            xy=(x, y),
            xytext=(x * distance, y * distance),
            fontsize=18,  # 增大字体
            fontweight='bold',
            ha=ha,
            va='center'
        )
        
        # 添加百分比
        plt.annotate(
            f"{percentages[i]}%", 
            xy=(x*0.7, y*0.7),  # 扇区内部点
            fontsize=18,  # 增大字体
            fontweight='bold',
            ha='center',
            va='center',
            color='white'
        )

# 添加图例，按分类组织
categories = set(book_categories)
category_colors = {'基础医学': '#ff9999', '临床医学': '#66b3ff', '药学': '#99ff99'}

# 创建分类图例
handles = []
labels = []

for category in categories:
    # 为每个分类创建一个图例项
    handles.append(plt.Rectangle((0,0), 1, 1, fc=category_colors[category]))
    labels.append(f"{category} ({sum([size for i, size in enumerate(book_sizes) if book_categories[i] == category]):.1f}MB)")

# 添加分类图例 - 放大字体和图例
category_legend = plt.legend(
    handles, 
    labels,
    title="学科分类",
    loc="upper left",
    bbox_to_anchor=(1, 1),
    frameon=True,
    facecolor='#f8f9fa',
    edgecolor='#dddddd',
    fontsize=18,  # 增大字体
    title_fontsize=18  # 增大标题字体
)
plt.gca().add_artist(category_legend)

# 添加书籍详情图例 - 放大字体和图例
book_legend = plt.legend(
    wedges,
    [f"{name}: {size:.1f}MB ({percentages[i]}%)" for i, (name, size) in enumerate(zip(book_names, book_sizes))],
    title="书籍详情",
    loc="upper left",
    bbox_to_anchor=(1, 0.7),
    frameon=True,
    facecolor='#f8f9fa',
    edgecolor='#dddddd',
    fontsize=18,  # 增大字体
    title_fontsize=18  # 增大标题字体
)

plt.title('医学教材内容分布', fontsize=20, pad=20, fontweight='bold')
plt.suptitle(f'总大小：{total:.1f}MB', y=0.95, fontsize=15)
plt.axis('equal')

# 添加数据来源注释
plt.annotate('数据来源：实际医学教科书大小统计', 
             xy=(1.0, -0.05),
             xycoords='axes fraction',
             fontsize=15,
             ha='right',
             color='#555555')

plt.tight_layout()
plt.savefig('medical_textbook_distribution.png', dpi=300, bbox_inches='tight')
plt.show()