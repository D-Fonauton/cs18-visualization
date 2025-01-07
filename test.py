import matplotlib.pyplot as plt
import numpy as np

# 示例数据
np.random.seed(0)
data = np.random.normal(loc=0.5, scale=0.1, size=1000)

# 绘制直方图
plt.hist(data, bins=30, color='black', edgecolor='black', alpha=0.7)

# 添加花括号标注
x_start = 0.3
x_end = 0.5
y_start = 50  # 在y轴上的起始位置，可以根据需要调整
y_end = y_start+2

# 绘制花括号，使用plot方法绘制线条
plt.plot([x_start, x_start], [y_start, y_end], color="black", lw=2)
plt.plot([x_end, x_end], [y_start, y_end], color="black", lw=2)
plt.plot([x_start, x_end], [y_end, y_end], color="black", lw=2)

# 添加文本标签
plt.text((x_start + x_end) / 2, y_end + 10, 'class A', horizontalalignment='center', fontsize=12)

# 显示图像
plt.show()
