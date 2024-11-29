import tkinter as tk

# 创建主窗口
root = tk.Tk()
root.title("动态列按钮示例")
root.geometry("400x200")

# 动态生成列和按钮
columns = 3  # 设置列数
buttons_per_column = 5  # 每列按钮数

for col in range(columns):
    # 创建列容器
    frame = tk.Frame(root)
    frame.pack(side="left", fill="y", expand=False)

    # 添加按钮到当前列
    for row in range(buttons_per_column):
        btn = tk.Button(frame, text=f"列{col+1} 按钮{row+1}")
        btn.pack(pady=5)

# 运行主循环
root.mainloop()
