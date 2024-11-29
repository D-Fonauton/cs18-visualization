import os
import json
from tkinter import Tk, Label, Button, filedialog, Frame, Canvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import time

from utils import reach_milestone
from parameters import SUBJECT_NUMBER

class GazeVisualizer:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("Gaze Visualizer")

        # main frame
        self.condition_frame = Frame(root)
        self.condition_frame.pack(side="left", fill="y")

        self.object_frame = Frame(root)
        self.object_frame.pack(side="left", fill="y")

        self.subject_frame = Frame(root)
        self.subject_frame.pack(side="left", fill="y")

        self.display_frame = Frame(root)
        self.display_frame.pack(side="right", expand=True, fill="both")

        self.label = Label(self.display_frame, text="请选择任务类型")
        self.label.pack()

        self.canvas = Canvas(self.display_frame)
        self.canvas.pack(fill="both", expand=True)


        Button(root, text="load data", width=15, command=self.load_data).pack()
        Button(root, text="previous image", width=15, command=self.previous_image).pack()
        Button(root, text="next image", width=15, command=self.next_image).pack()
        Button(root, text="previous subject", width=15, command=self.previous_subject).pack()
        Button(root, text="next subject", width=15, command=self.next_subject).pack()

        self.subject = 0

        # data
        self.task_dirs = {}
        self.condition = None
        self.current_object = None
        self.current_image_index = 0
        self.gaze_data = []

        self.threshold = 125

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.root.bind("<Left>", self.previous_image)
        self.root.bind("<Right>", self.next_image)

        self.time = time.time()


    def load_data(self):
        base_folder = filedialog.askdirectory(title="select COCO-Search18 dataset folder")
        if not base_folder:
            return

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

                # create condition button
                Button(self.condition_frame, text=task_type, command=lambda t=task_type: self.load_type(t)).pack()

        # load multiple json files
        json_paths = filedialog.askopenfilenames(title="select json files", filetypes=[("JSON Files", "*.json")])
        for json_path in json_paths:
            with open(json_path, 'r') as f:
                self.gaze_data.extend(json.load(f))
        self.label.config(text=f"loaded {len(self.gaze_data)} items")


    def load_type(self, condition):
        # clear
        for widget in self.object_frame.winfo_children():
            widget.destroy()

        self.condition = condition
        self.current_object = None
        self.current_image_index = 0

        # generate buttons
        for task_object in self.task_dirs[condition]:
            Button(self.object_frame, text=task_object, width = 12, command=lambda o=task_object: self.load_object(o)).pack()

        self.label.config(text=f"condition selected: {condition}")


    def load_object(self, task_object):
        for widget in self.subject_frame.winfo_children():
            widget.destroy()
        # 10 subjects
        for i in range(10):
            Button(self.subject_frame, text=f"subject {i}", command=lambda o=i: self.load_subject(o)).pack()

        self.current_object = task_object
        self.label.config(text=f"selected task: {task_object} from {self.condition}")


    def load_subject(self, subject):
        self.subject = subject
        self.display_image_and_gaze()
        self.label.config(text=f"selected subject: {subject} searching for {self.current_object} from {self.condition}")


    def display_image_and_gaze(self):
        if not self.condition or not self.current_object:
            self.label.config(text="please select condition and task object first!")
            return

        images = self.task_dirs[self.condition][self.current_object]
        if not images:
            self.label.config(text="no images in current task object folder!")
            return

        for widget in self.canvas.winfo_children():
            widget.destroy()
        self.canvas.delete("all")

        image_path = images[self.current_image_index]
        img_name = os.path.basename(image_path)

        gaze = next((g for g in self.gaze_data if (g["name"] == img_name and g["subject"] == self.subject)), None)
        if gaze:
            self.animate_gaze(image_path, gaze)
            self.label.config(text=f"condition={self.condition},task object={self.current_object},image={img_name},subject={self.subject}")
        else:
            self.label.config(text=f"no scanpaths found with subject {self.subject} searching for image: {img_name}")


    def animate_gaze(self, image_path, gaze):
        x_coords = gaze["X"]
        y_coords = gaze["Y"]
        durations = gaze["T"]

        for widget in self.canvas.winfo_children():
            widget.destroy()
        self.canvas.delete("all")

        plt.close()
        self.fig, self.ax = plt.subplots()
        img = plt.imread(image_path)
        self.ax.imshow(img)
        self.ax.axis("off")

        points = self.ax.scatter([], [], c=[], s=40)
        line, = self.ax.plot([], [], 'b-', alpha=0.5)

        def update(frame):
            # time.sleep(durations[frame] / 1000)
            # print(f'interval: {round((time.time()-self.time)*1000)}, duration: {durations[frame]}')
            # self.time = time.time()
            # milestone = reach_milestone(durations, frame)

            # if hasattr(self, "ani"):
                # self.ani.interval = durations[frame]
                # print(self.ani.event_source.interval)

            line.set_data(x_coords[:frame + 1], y_coords[:frame + 1])         
            current_colors = [
                'yellow' if durations[i] < self.threshold else 'red'
                for i in range(frame + 1)
            ]
            points.set_offsets(list(zip(x_coords[:frame + 1], y_coords[:frame + 1])))
            points.set_color(current_colors)

            return points, line
        
        self.ani = FuncAnimation(self.fig, update, frames=len(x_coords), interval=200, blit=True)

        self.canvas_widget = FigureCanvasTkAgg(self.fig, master=self.canvas)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True)


    def previous_image(self, event=None):
        if self.condition and self.current_object:
            images = self.task_dirs[self.condition][self.current_object]
            self.current_image_index = (self.current_image_index - 1) % len(images)
            self.display_image_and_gaze()


    def next_image(self, event=None):
        if self.condition and self.current_object:
            images = self.task_dirs[self.condition][self.current_object]
            self.current_image_index = (self.current_image_index + 1) % len(images)
            self.display_image_and_gaze()


    def previous_subject(self, event=None):
        if self.condition and self.current_object:
            self.subject = (self.subject - 1) % SUBJECT_NUMBER
            self.display_image_and_gaze()


    def next_subject(self, event=None):
        if self.condition and self.current_object:
            self.subject = (self.subject + 1) % SUBJECT_NUMBER
            self.display_image_and_gaze()


    def on_close(self):
        if hasattr(self, "ani") and self.ani.event_source is not None:
            self.ani.event_source.stop()
        
        if hasattr(self, "canvas_widget"):
            self.canvas_widget.get_tk_widget().destroy()
        
        self.root.quit()
        self.root.destroy()


if __name__ == "__main__":
    root = Tk()
    app = GazeVisualizer(root)
    root.mainloop()
