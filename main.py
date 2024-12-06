import os
import json
from tkinter import Tk, Label, Button, filedialog, Frame, Canvas, BooleanVar, Checkbutton
import matplotlib.pyplot as plt
import matplotlib.patches as pc
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import time

from utils import reach_milestone
from parameters import SUBJECT_NUMBER, SUBJECT_INDEX

class GazeVisualizer:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("Gaze Visualizer")

        # main frame
        self.main_frame = Frame(root)
        self.main_frame.pack(side="top", expand=True, fill="both")

        self.side_frame = Frame(root)
        self.side_frame.pack(side="bottom",fill="both")

        self.initial_frame = Frame(self.main_frame)
        self.initial_frame.pack(side="left", fill="y")

        self.condition_frame = Frame(self.main_frame)
        self.condition_frame.pack(side="left", fill="y")

        self.object_frame = Frame(self.main_frame)
        self.object_frame.pack(side="left", fill="y")

        self.subject_frame = Frame(self.main_frame)
        self.subject_frame.pack(side="left", fill="y")

        self.display_frame = Frame(self.main_frame)
        self.display_frame.pack(side="right", expand=True, fill="both")

        self.label = Label(self.display_frame, text="please select task type")
        self.label.pack()

        self.canvas = Canvas(self.display_frame)
        self.canvas.pack(fill="both", expand=True)

        self.check_button_frame = Frame(self.side_frame)
        self.check_button_frame.pack(side="left", fill="x", expand=True)

        Button(self.initial_frame, text="load data", width=15, command=self.load_data).pack()
        Button(self.initial_frame, text="previous image", width=15, command=self.previous_image).pack()
        Button(self.initial_frame, text="next image", width=15, command=self.next_image).pack()
        Button(self.initial_frame, text="previous subject", width=15, command=self.previous_subject).pack()
        Button(self.initial_frame, text="next subject", width=15, command=self.next_subject).pack()

        
        self.deepgaze_status = BooleanVar(value=False)
        self.deepgaze_button = Checkbutton(self.check_button_frame, text="DeepGaze Map", variable=self.deepgaze_status, command=self.toggle_deepgaze)
        self.deepgaze_button.pack(side="left", fill="x", pady=10)

        self.scanpaths_status = BooleanVar(value=False)
        self.scanpaths_button = Checkbutton(self.check_button_frame, text="see all scanpaths", variable=self.scanpaths_status, command=self.toggle_scanpaths)
        self.scanpaths_button.pack(side="left", fill="x", pady=10)

        self.animation_status = BooleanVar(value=False)
        self.animation_button = Checkbutton(self.check_button_frame, text="activate animation", variable=self.animation_status, command=self.toggle_animation)
        self.animation_button.pack(side="left", fill="x", pady=10)

        self.bbox_status = BooleanVar(value=False)
        self.bbox_button = Checkbutton(self.check_button_frame, text="see bounding box", variable=self.bbox_status, command=self.toggle_bbox)
        self.bbox_button.pack(side="left", fill="x", pady=10)
        

        self.subject = 0

        # data
        self.task_dirs = {}
        self.condition = None
        self.current_object = None
        self.current_image_index = 0
        self.gaze_data = []

        self.threshold = 125

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.root.bind("<Up>", self.previous_image)
        self.root.bind("<Down>", self.next_image)
        self.root.bind("<Left>", self.previous_subject)
        self.root.bind("<Right>", self.next_subject)

        self.time = time.time()


    def toggle_deepgaze(self):
        # print(self.deepgaze_status.get())
        pass

    def toggle_scanpaths(self):
        # print(self.scanpaths_status.get())
        if self.scanpaths_status.get():
            self.animation_button.config(state="disabled")
            self.animation_status.set(False)
        else:
            self.animation_button.config(state="normal")
        self.display_image_and_gaze()

    def toggle_animation(self):
        # print(self.animation_status.get())
        self.display_image_and_gaze()

    def toggle_bbox(self):
        # print(self.animation_status.get())
        self.display_image_and_gaze()    


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

        for widget in self.canvas.winfo_children():
            widget.destroy()
        self.canvas.delete("all")
        
        # 10 subjects
        for i in range(SUBJECT_NUMBER):
            Button(self.subject_frame, text=f"subject {SUBJECT_INDEX[i]}", command=lambda o=i: self.load_subject(o)).pack()

        self.current_object = task_object
        self.current_image_index = 0
        self.label.config(text=f"selected task: {task_object} from {self.condition}")


    def load_subject(self, subject):
        self.subject = subject
        self.display_image_and_gaze()
        # self.label.config(text=f"selected subject: {SUBJECT_INDEX[subject]} searching for {self.current_object} from {self.condition}")


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

        gazes = [g for g in self.gaze_data if (g["name"] == img_name and g["task"] == self.current_object)]
        gaze = [g for g in gazes if (g["subject"] == SUBJECT_INDEX[self.subject])]
        gaze = None if gaze == [None] else gaze

        if self.scanpaths_status.get():
            self.plot_gazes(image_path, gazes)
            correct = all([c["correct"] for c in gazes])
            self.label.config(text=f"condition={self.condition},task object={self.current_object},image={img_name},subject=all, all_correct: {correct}")
        elif gaze:
            correct = gaze[0]["correct"]
            correct_prob = sum([c["correct"] for c in gazes]) / SUBJECT_NUMBER
            self.label.config(text=f"condition={self.condition},task object={self.current_object},image={img_name},subject={SUBJECT_INDEX[self.subject]}, correct: {correct}({correct_prob})")
            if self.animation_status.get():
                self.animate_gaze(image_path, gaze[0])
            else:
                self.plot_gazes(image_path, gaze)
        else:
            self.label.config(text=f"no scanpaths found with subject {SUBJECT_INDEX[self.subject]} searching for image: {img_name}")


    def plot_gazes(self, image_path, gazes):
        if hasattr(self, "ani") and self.ani.event_source is not None:
            self.ani.event_source.stop()

        for widget in self.canvas.winfo_children():
            widget.destroy()
        self.canvas.delete("all")
        plt.close()
        self.fig, self.ax = plt.subplots()
        img = plt.imread(image_path)
        self.ax.imshow(img)
        self.ax.axis("off")

        for gaze in gazes:

            x_coords = gaze["X"]
            y_coords = gaze["Y"]
            durations = gaze["T"]

            points = self.ax.scatter(x_coords, y_coords, c=[], s=40)
            current_colors = ['yellow' if durations[i] < self.threshold else 'red' for i in range(len(x_coords))]
            points.set_color(current_colors)


            line, = self.ax.plot(x_coords, y_coords, 'b-', alpha=0.5)

        if self.bbox_status.get():
            bbox = gazes[0]["bbox"]
            bbox_x = bbox[0]
            bbox_y = bbox[1]
            self.ax.add_patch(pc.Rectangle((bbox_x, bbox_y), bbox[2], bbox[3], linewidth=2, edgecolor='blue', facecolor='none'))

        self.canvas_widget = FigureCanvasTkAgg(self.fig, master=self.canvas)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True)




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

        if self.bbox_status.get():
            bbox = gaze["bbox"]
            bbox_x = bbox[0]
            bbox_y = bbox[1]
            self.ax.add_patch(pc.Rectangle((bbox_x, bbox_y), bbox[2], bbox[3], linewidth=2, edgecolor='blue', facecolor='none'))

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
