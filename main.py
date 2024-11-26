import os
import json
from tkinter import Tk, Label, Button, filedialog, Frame
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class GazeVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("扫视轨迹可视化")

        # 主界面布局
        self.task_frame = Frame(root)
        self.task_frame.pack(side="left", fill="y")

        self.display_frame = Frame(root)
        self.display_frame.pack(side="right", expand=True, fill="both")

        self.label = Label(self.display_frame, text="请选择任务文件夹")
        self.label.pack()

        self.previous_button = Button(self.display_frame, text="上一张", command=self.previous_image)
        self.previous_button.pack(side="left")

        self.next_button = Button(self.display_frame, text="下一张", command=self.next_image)
        self.next_button.pack(side="right")

        # 数据
        self.task_dirs = {}
        self.current_task = None
        self.current_image_index = 0
        self.gaze_data = {}

        self.threshold = 100  # 停留时间阈值（毫秒）

    def load_data(self):
        # 选择数据文件夹
        base_folder = filedialog.askdirectory(title="选择数据文件夹")
        if not base_folder:
            return

        # 遍历任务文件夹
        for task_name in os.listdir(base_folder):
            task_path = os.path.join(base_folder, task_name)
            if os.path.isdir(task_path):
                images = [os.path.join(task_path, f) for f in os.listdir(task_path) if f.endswith('.jpg')]
                if images:
                    self.task_dirs[task_name] = images
                    # 创建任务按钮
                    Button(self.task_frame, text=task_name, command=lambda t=task_name: self.load_task(t)).pack()

        # 加载JSON文件
        json_path = filedialog.askopenfilename(title="选择扫视轨迹JSON文件", filetypes=[("JSON Files", "*.json")])
        if json_path:
            with open(json_path, 'r') as f:
                self.gaze_data = json.load(f)
            self.label.config(text="JSON数据已加载")

    def load_task(self, task_name):
        # 加载任务的第一张图片
        self.current_task = task_name
        self.current_image_index = 0
        self.display_image_and_gaze()

    def display_image_and_gaze(self):
        if self.current_task is None:
            self.label.config(text="请先选择任务")
            return

        # 当前任务的图片列表
        images = self.task_dirs[self.current_task]
        if not images:
            self.label.config(text="任务无图片")
            return

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

        # 显示图片和动画
        fig, ax = plt.subplots()
        img = plt.imread(image_path)
        ax.imshow(img)
        points, = ax.plot([], [], 'ro', markersize=5)  # 注视点
        line, = ax.plot([], [], 'b-', alpha=0.5)  # 连线

        def update(frame):
            if frame < len(x_coords):
                line.set_data(x_coords[:frame + 1], y_coords[:frame + 1])
                points.set_data(x_coords[:frame + 1], y_coords[:frame + 1])
                if durations[frame] < self.threshold:
                    ax.plot(x_coords[frame], y_coords[frame], 'yo', markersize=8)

            return points, line

        ani = FuncAnimation(fig, update, frames=len(x_coords), interval=200, blit=True)
        plt.title(f"任务: {self.current_task} 图片: {os.path.basename(image_path)}")
        plt.show()

    def previous_image(self):
        # 切换到上一张图片
        if self.current_task is not None:
            self.current_image_index = (self.current_image_index - 1) % len(self.task_dirs[self.current_task])
            self.display_image_and_gaze()

    def next_image(self):
        # 切换到下一张图片
        if self.current_task is not None:
            self.current_image_index = (self.current_image_index + 1) % len(self.task_dirs[self.current_task])
            self.display_image_and_gaze()

if __name__ == "__main__":
    root = Tk()
    app = GazeVisualizer(root)
    Button(root, text="加载数据", command=app.load_data).pack()
    root.mainloop()
