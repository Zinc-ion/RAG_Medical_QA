import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 模拟错误类型数据
error_labels = ['术语混淆', '长文本冗余', '知识更新延迟', '其他']
error_ratio = [52, 28, 15, 5]  # 单位：百分比

# 绘制饼图
plt.figure(figsize=(8, 6))
colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99']
explode = (0.1, 0, 0, 0)  # 突出显示术语混淆

plt.pie(error_ratio,
        labels=error_labels,
        autopct='%1.1f%%',
        colors=colors,
        explode=explode,
        startangle=90,
        shadow=True,
        textprops={'fontsize':12})

plt.title('难负例类型分布 (N=5000)', fontsize=20, pad=20)
plt.axis('equal')  # 保证饼图为正圆形
plt.tight_layout()
plt.savefig('error_type_pie.png', dpi=300)
plt.show()