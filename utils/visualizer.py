import os
import json
from tkinter import Tk, Label, Button, filedialog, Frame, Canvas
from tkinter import BooleanVar, Checkbutton
from tkinter import StringVar, IntVar, Radiobutton
import matplotlib.pyplot as plt
import matplotlib.patches as pc
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import hydra
from omegaconf import DictConfig

# local
from .src import COCOSearch18


class VisualizerFrame:
    def __init__(self, root):
        # main frame
        self.main_frame = Frame(root)
        self.main_frame.pack(side="top", expand=True, fill="both")

        self.side_frame = Frame(root)
        self.side_frame.pack(side="bottom",fill="both")

        self.initial_frame = Frame(self.main_frame)
        self.initial_frame.pack(side="left", fill="y")

        self.condition_frame = Frame(self.main_frame)
        self.condition_frame.pack(side="left", fill="y")

        self.task_frame = Frame(self.main_frame)
        self.task_frame.pack(side="left", fill="y")

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



class Visualizer:
    def __init__(self, root: Tk, cfg: DictConfig):
        self.root = root

        self.cfg = cfg
        self.dataset = COCOSearch18(cfg)
        self.frame_init()

        # data
        self.current_image_index = 0
        self.threshold = 125

        
        self.display_image_and_gaze()


    def __getitem__(self, index):
        return self.dataset[index]


    def frame_init(self):
        self.root.title("Gaze Visualizer")
        self.frame = VisualizerFrame(self.root)

        # initial frame button init
        Button(self.frame.initial_frame, text="previous image", width=15, command=self.previous_image).pack()
        Button(self.frame.initial_frame, text="next image", width=15, command=self.next_image).pack()
        Button(self.frame.initial_frame, text="previous subject", width=15, command=self.previous_subject).pack()
        Button(self.frame.initial_frame, text="next subject", width=15, command=self.next_subject).pack()

        # condition frame radiobutton init
        self.selected_condition = StringVar(value=self.cfg.conditions[0])
        for condition in self.cfg.conditions:
            Radiobutton(self.frame.condition_frame, 
                        text=condition, 
                        variable=self.selected_condition, 
                        value=condition, 
                        command=self.on_select_condition).pack(anchor="w")

        # task frame radiobutton init
        self.selected_task = StringVar(value=self.cfg.categories[0])
        for task in self.cfg.categories:
            Radiobutton(self.frame.task_frame, 
                        text=task, 
                        variable=self.selected_task, 
                        value=task, 
                        command=self.on_select_task).pack(anchor="w")

        # subject frame radiobutton init
        self.selected_subject = IntVar(value=self.cfg.subjects[0])
        # StringVar(value=self.cfg.subjects[0])
        for subject in self.cfg.subjects:
            Radiobutton(self.frame.subject_frame, 
                        text=f"subject {subject}", 
                        variable=self.selected_subject, 
                        value=subject, 
                        command=self.on_select_subject).pack(anchor="w")

        # checkbutton frame button init
        self.deepgaze_status = BooleanVar(value=False)
        self.deepgaze_button = Checkbutton(self.frame.check_button_frame, text="DeepGaze Map", variable=self.deepgaze_status, command=self.toggle_deepgaze)
        self.deepgaze_button.pack(side="left", fill="x", pady=10)

        self.scanpaths_status = BooleanVar(value=False)
        self.scanpaths_button = Checkbutton(self.frame.check_button_frame, text="see all scanpaths", variable=self.scanpaths_status, command=self.toggle_scanpaths)
        self.scanpaths_button.pack(side="left", fill="x", pady=10)

        self.animation_status = BooleanVar(value=False)
        self.animation_button = Checkbutton(self.frame.check_button_frame, text="activate animation", variable=self.animation_status, command=self.toggle_animation)
        self.animation_button.pack(side="left", fill="x", pady=10)

        self.bbox_status = BooleanVar(value=False)
        self.bbox_button = Checkbutton(self.frame.check_button_frame, text="see bounding box", variable=self.bbox_status, command=self.toggle_bbox)
        self.bbox_button.pack(side="left", fill="x", pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.root.bind("<Up>", self.previous_image)
        self.root.bind("<Down>", self.next_image)
        self.root.bind("<Left>", self.previous_subject)
        self.root.bind("<Right>", self.next_subject)


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


    def on_select_condition(self):
        self.display_image_and_gaze()
        print(f"Selected option: {self.selected_condition.get()}")


    def on_select_task(self):
        self.display_image_and_gaze()
        print(f"Selected option: {self.selected_task.get()}")


    def on_select_subject(self):
        self.display_image_and_gaze()
        print(f"Selected option: {self.selected_subject.get()}")
        print(type(self.selected_subject.get()))


    def display_image_and_gaze(self):
        images = self[self.selected_condition.get()][self.selected_task.get()]
        if not images:
            self.frame.label.config(text="no images in current task object folder!")
            return

        for widget in self.frame.canvas.winfo_children():
            widget.destroy()
        self.frame.canvas.delete("all")

        image_path = images[self.current_image_index]
        img_name = os.path.basename(image_path)

        condition_str = "present" if self.selected_condition.get() == "TP" else "absent"
        gazes = [g for g in self.dataset.json if (g["condition"] == condition_str and g["task"] == self.selected_task.get() and g["name"] == img_name)]


        gaze = [g for g in gazes if (g["subject"] == self.selected_subject.get())]
        gaze = None if gaze == [None] else gaze

        if self.scanpaths_status.get():
            self.plot_gazes(image_path, gazes)
            correct = all([c["correct"] for c in gazes])
            self.frame.label.config(text=f"condition={self.selected_condition.get()},task object={self.selected_task.get()},image={img_name},subject=all, all_correct: {correct}")
        elif gaze:
            correct = gaze[0]["correct"]
            correct_prob = sum([c["correct"] for c in gazes]) / self.cfg.subject_number
            self.frame.label.config(text=f"condition={self.selected_condition.get()},task object={self.selected_task.get()},image={img_name},subject={self.selected_subject.get()}, correct: {correct}({correct_prob})")
            if self.animation_status.get():
                self.animate_gaze(image_path, gaze[0])
            else:
                self.plot_gazes(image_path, gaze)
        else:
            self.frame.label.config(text=f"no scanpaths found with subject {self.selected_subject.get()} searching for image: {img_name}")


    def plot_gazes(self, image_path, gazes):
        if hasattr(self, "ani") and self.ani.event_source is not None:
            self.ani.event_source.stop()

        for widget in self.frame.canvas.winfo_children():
            widget.destroy()
        self.frame.canvas.delete("all")
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

        self.canvas_widget = FigureCanvasTkAgg(self.fig, master=self.frame.canvas)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True)


    def animate_gaze(self, image_path, gaze):
        x_coords = gaze["X"]
        y_coords = gaze["Y"]
        durations = gaze["T"]

        for widget in self.frame.canvas.winfo_children():
            widget.destroy()
        self.frame.canvas.delete("all")

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
        self.current_image_index = (self.current_image_index - 1) % len(self[self.selected_condition.get()][self.selected_task.get()])
        self.display_image_and_gaze()


    def next_image(self, event=None):
        self.current_image_index = (self.current_image_index + 1) % len(self[self.selected_condition.get()][self.selected_task.get()])
        self.display_image_and_gaze()


    def previous_subject(self, event=None):
        index = 10 if self.selected_subject.get() == 1 else self.selected_subject.get() - 1
        self.selected_subject.set(index)
        self.display_image_and_gaze()


    def next_subject(self, event=None):
        index = 1 if self.selected_subject.get() == 10 else self.selected_subject.get() + 1
        self.selected_subject.set(index)
        self.display_image_and_gaze()


    def on_close(self):
        if hasattr(self, "ani") and self.ani.event_source is not None:
            self.ani.event_source.stop()
        
        if hasattr(self, "canvas_widget"):
            self.canvas_widget.get_tk_widget().destroy()
        
        self.root.quit()
        self.root.destroy()


@hydra.main(version_base=None, config_path="../config", config_name="config")
def debug_visualizer(cfg: DictConfig):
    root = Tk()
    app = Visualizer(root, cfg.dataset)
    root.mainloop()


if __name__ == "__main__":
    debug_visualizer()
