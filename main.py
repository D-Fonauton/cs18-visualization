import os
import json
from tkinter import Tk, Label, Button, filedialog, Frame, Canvas
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

class GazeVisualizer:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("扫视轨迹可视化")

        # 主界面布局
        self.type_frame = Frame(root)
        self.type_frame.pack(side="left", fill="y")

        self.object_frame = Frame(root)
        self.object_frame.pack(side="left", fill="y")

        self.display_frame = Frame(root)
        self.display_frame.pack(side="right", expand=True, fill="both")

        self.label = Label(self.display_frame, text="请选择任务类型")
        self.label.pack()

        self.canvas = Canvas(self.display_frame)
        self.canvas.pack(fill="both", expand=True)

        # 数据
        self.task_dirs = {}
        self.current_type = None
        self.current_object = None
        self.current_image_index = 0
        self.gaze_data = []

        self.threshold = 125  # 停留时间阈值（毫秒）

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)



    def load_data(self):
        # 选择数据文件夹
        base_folder = filedialog.askdirectory(title="选择数据文件夹")
        if not base_folder:
            return


        # 遍历任务类型和任务对象
        for task_type in os.listdir(base_folder):
            type_path = os.path.join(base_folder, task_type)
            if os.path.isdir(type_path):
                self.task_dirs[task_type] = {}
                for task_object in os.listdir(type_path):
                    object_path = os.path.join(type_path, task_object)
                    if os.path.isdir(object_path):
                        images = [os.path.join(object_path, f) for f in os.listdir(object_path) if f.endswith('.jpg')]
                        if images:
                            self.task_dirs[task_type][task_object] = images

                # 创建任务类型按钮
                Button(self.type_frame, text=task_type, command=lambda t=task_type: self.load_type(t)).pack()

        # 加载多个JSON文件
        json_paths = filedialog.askopenfilenames(title="选择扫视轨迹JSON文件", filetypes=[("JSON Files", "*.json")])
        for json_path in json_paths:
            with open(json_path, 'r') as f:
                self.gaze_data.extend(json.load(f))
        self.label.config(text=f"已加载 {len(self.gaze_data)} 条扫视数据")


    def load_type(self, task_type):
        # 清空对象按钮
        for widget in self.object_frame.winfo_children():
            widget.destroy()

        self.current_type = task_type
        self.current_object = None
        self.current_image_index = 0

        # 根据任务类型生成任务对象按钮
        for task_object in self.task_dirs[task_type]:
            Button(self.object_frame, text=task_object, command=lambda o=task_object: self.load_object(o)).pack()

        self.label.config(text=f"已选择任务类型: {task_type}")


    def load_object(self, task_object):
        self.current_object = task_object
        self.current_image_index = 0
        self.display_image_and_gaze()


    def display_image_and_gaze(self):
        if not self.current_type or not self.current_object:
            self.label.config(text="请先选择任务类型和对象")
            return

        # 当前任务对象的图片列表
        images = self.task_dirs[self.current_type][self.current_object]
        if not images:
            self.label.config(text="任务无图片")
            return

        # 清空 Canvas 内容
        for widget in self.canvas.winfo_children():
            widget.destroy()
        self.canvas.delete("all")

        image_path = images[self.current_image_index]
        img_name = os.path.basename(image_path)

        # 查找对应的扫视数据
        gaze = next((g for g in self.gaze_data if g["name"] == img_name), None)
        if gaze:
            self.animate_gaze(image_path, gaze)
        else:
            self.label.config(text=f"未找到 {img_name} 的扫视数据")


    def animate_gaze(self, image_path, gaze):
        # 提取坐标和停留时间
        x_coords = gaze["X"]
        y_coords = gaze["Y"]
        durations = gaze["T"]

        # 清空 Canvas 内容
        for widget in self.canvas.winfo_children():
            widget.destroy()
        self.canvas.delete("all")


        # 创建 Matplotlib 图
        fig, ax = plt.subplots()
        img = plt.imread(image_path)
        ax.imshow(img)
        ax.axis("off")  # 隐藏坐标轴
        points, = ax.plot([], [], 'ro', markersize=5)  # 注视点
        line, = ax.plot([], [], 'b-', alpha=0.5)  # 连线


        # 更新函数
        def update(frame):
            if frame < len(x_coords):
                line.set_data(x_coords[:frame + 1], y_coords[:frame + 1])
                points.set_data(x_coords[:frame + 1], y_coords[:frame + 1])
                # 标记停留时间低于阈值的注视点
                if durations[frame] < self.threshold:
                    ax.plot(x_coords[frame], y_coords[frame], 'yo', markersize=8)

            return points, line


        # 创建动画
        self.ani = FuncAnimation(fig, update, frames=len(x_coords), interval=200, blit=True)

        # 嵌入到 Tkinter Canvas 中
        canvas_widget = FigureCanvasTkAgg(fig, master=self.canvas)
        canvas_widget.draw()
        canvas_widget.get_tk_widget().pack(fill="both", expand=True)


    def previous_image(self):
        # 切换到上一张图片
        if self.current_type and self.current_object:
            images = self.task_dirs[self.current_type][self.current_object]
            self.current_image_index = (self.current_image_index - 1) % len(images)
            self.display_image_and_gaze()


    def next_image(self):
        # 切换到下一张图片
        if self.current_type and self.current_object:
            images = self.task_dirs[self.current_type][self.current_object]
            self.current_image_index = (self.current_image_index + 1) % len(images)
            self.display_image_and_gaze()


    def on_close(self):
        # 停止动画
        if hasattr(self, "ani"):
            self.ani.event_source.stop()
        
        # 清理 Matplotlib 图形
        if hasattr(self, "canvas_widget"):
            self.canvas_widget.get_tk_widget().destroy()
        
        # 退出 Tkinter 主循环
        self.root.quit()
        self.root.destroy()


if __name__ == "__main__":
    root = Tk()
    app = GazeVisualizer(root)
    Button(root, text="加载数据", command=app.load_data).pack()
    Button(root, text="上一张", command=app.previous_image).pack()
    Button(root, text="下一张", command=app.next_image).pack()
    root.mainloop()
