import tkinter as tk

def on_select():
    print(f"Selected option: {selected_option.get()}")

# 创建主窗口
root = tk.Tk()
root.title("Radiobutton Example")

# 定义一个变量，绑定到所有 Radiobutton
selected_option = tk.StringVar(value="Option 1")  # 设置默认选项

# 创建单选按钮
options = ["Option 1", "Option 2", "Option 3"]
for option in options:
    tk.Radiobutton(root, text=option, variable=selected_option, value=option, command=on_select).pack(anchor="w")

# 运行主循环
root.mainloop()
