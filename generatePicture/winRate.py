import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
plt.rcParams['font.size'] = 12  # 设置默认字体大小


# 方法名称
methods = [
    "双通道检索",
    "仅低阶检索",
    "仅高阶检索"
]

# NaiveRAG 与三种检索方式的得分
naive_scores = [35.2, 42.4, 40.0]
other_scores = [64.8, 57.6, 60.0]

x = np.arange(len(methods))  # x轴刻度
width = 0.35  # 柱宽

fig, ax = plt.subplots(figsize=(10, 7), facecolor='white')

# 绘制柱状图
rects1 = ax.bar(x - width/2, naive_scores, width, label='NaiveRAG', color='#4E79A7')
rects2 = ax.bar(x + width/2, other_scores, width, label='对比方法', color='#F28E2B')

# 添加数值标签
for rect in rects1 + rects2:
    height = rect.get_height()
    ax.annotate(f'{height:.1f}%',
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 6),
                textcoords="offset points",
                ha='center', va='bottom',
                fontsize=13, fontweight='bold')

# 设置坐标轴和标题
ax.set_ylabel('得分 (%)', fontsize=15)
ax.set_title('NaiveRAG与不同检索方式得分对比', fontsize=18, pad=20, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(methods, fontsize=14)
ax.legend(fontsize=14)
ax.set_ylim(0, 100)

plt.tight_layout()
plt.savefig('retrieval_compare_bar.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()