from tkinter import Tk, Label, Frame, Canvas
import pickle
from tkinter import IntVar, BooleanVar, Radiobutton, Checkbutton
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from math import comb
import numpy as np


# local
from .scores import Scores

class HistoFrame:
    def __init__(self, root):
        self.main_frame = Frame(root)
        self.main_frame.pack(side="top", expand=True, fill="both")

        self.side_frame = Frame(root)
        self.side_frame.pack(side="bottom", expand=True, fill="both")
        
        self.select_frame = Frame(self.main_frame)
        self.select_frame.pack(side="left")

        self.subject1_frame = Frame(self.select_frame)
        self.subject1_frame.pack(side="left")

        self.subject2_frame = Frame(self.select_frame)
        self.subject2_frame.pack(side="left")

        self.plot_frame = Frame(self.main_frame)
        self.plot_frame.pack(side="right", expand=True, fill="both")

        self.label = Label(self.plot_frame, text="histogram plot")
        self.label.pack()

        self.canvas = Canvas(self.plot_frame)
        self.canvas.pack(fill="both", expand=True)


class Histogram:
    def __init__(self, root: Tk, file):
        self.root = root
        
        with open(file, "rb") as f:
            self.files = pickle.load(f)
        
        self.current_file = Scores()
        self.current_file = self.files[0]
        self.subject_number = 10

        self.frame_init()
        self.plot()


    def frame_init(self):
        self.root.title("Histogram Plot")
        self.frame = HistoFrame(self.root)
        # condition frame radiobutton init
        self.selected_subject1 = IntVar(value=0)


        for index in range(self.subject_number):
            Radiobutton(self.frame.subject1_frame, 
                                text=f"subject {index + 1}", 
                                variable=self.selected_subject1, 
                                value=index, 
                                command=self.on_select_subject).pack(anchor="w")

        """
        self.rb1 = [Radiobutton(self.frame.subject1_frame, 
                                text=f"subject {index + 1}", 
                                variable=self.selected_subject1, 
                                value=index, 
                                command=self.on_select_subject) for index in range(self.subject_number)]
        for rb in self.rb1:
            rb.pack(anchor="w")
        """

        # task frame radiobutton init
        self.selected_subject2 = IntVar(value=1)

        for index in range(self.subject_number):
            Radiobutton(self.frame.subject2_frame, 
                                text=f"subject {index + 1}", 
                                variable=self.selected_subject2, 
                                value=index, 
                                command=self.on_select_subject).pack(anchor="w")

        """
        self.rb2 = [Radiobutton(self.frame.subject2_frame, 
                                text=f"subject {index + 1}", 
                                variable=self.selected_subject2, 
                                value=index, 
                                command=self.on_select_subject) for index in range(self.subject_number)]
        for rb in self.rb2:
            rb.pack(anchor="w")
        """

        self.overall_status = BooleanVar(value=False)
        self.overall_button = Checkbutton(self.frame.side_frame, text="overall", variable=self.overall_status, command=self.toggle_overall)
        self.overall_button.pack(side="left", fill="x", pady=10)

        # rb2[self.selected_subject1.get()].config(state="disabled")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)


    def on_select_subject(self):
        subject1 = self.selected_subject1.get()
        subject2 = self.selected_subject2.get()

        def combination_rank(n, r, combination):
            digit1, digit2 = combination
            sort = []
            for index1 in range(1, n):
                for index2 in range(index1 + 1, n + 1):
                    sort.append(f"{index1:02d}{index2:02d}")

            return int(np.where(np.array(sort) == f"{digit1+1:02d}{digit2+1:02d}")[0])

        
        if subject1 == subject2:
            self.frame.label.config(text="subject1 must be different from subject2!")
            return
        elif subject1 > subject2:
            subject1, subject2 = subject2, subject1
        self.current_file = self.files[combination_rank(self.subject_number, 2, (subject1, subject2))]
        self.plot()    


    def toggle_overall(self):
        if self.overall_status.get():
            self.current_file = Scores()
            for index in range(len(self.files)):
                i, s = self.files[index].get_all()
                self.current_file.concatenate(i, s)
            self.plot()


    def plot(self):
        for widget in self.frame.canvas.winfo_children():
            widget.destroy()
        self.frame.canvas.delete("all")
        plt.close()

        self.fig, self.ax = plt.subplots()

        # data = self.current_file.get_all_score()
        data = []
        for index in range(18):
            data.append(self.current_file.get_category_score(index))

        # self.ax.hist(data, bins=30, color='black')
        self.ax.boxplot(data)
        mylabel = ["bottle","bowl","car","chair","clock","cup","fork","keyboard","knife","laptop","microwave","mouse","oven","potted plant","sink","stop sign","toilet","tv"]
        self.ax.set_xticks([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],mylabel)

        self.frame.label.config(text="Normal Distribution")

        self.canvas_widget = FigureCanvasTkAgg(self.fig, master=self.frame.canvas)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill="both", expand=True)


    def on_close(self):
        if hasattr(self, "canvas_widget"):
            self.canvas_widget.get_tk_widget().destroy()
        
        self.root.quit()
        self.root.destroy()
        