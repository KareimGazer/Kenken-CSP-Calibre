
import tkinter as tk                # python 3
from tkinter import font as tkfont  # python 3

from Benchmark import *
from Game import *


class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(
            family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        self.geometry("1000x700")
        # tells the root to not let the widgets inside it determine its size.
        self.pack_propagate(False)
        self.resizable(0, 0)  # makes the root window fixed in size.

        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, Benchmark):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Kenken Solver",
                         font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        solve_button = tk.Button(self, text="Solve A Puzzle !!!",
                                 command=lambda: controller.show_frame("PageOne"))
        bench_button = tk.Button(self, text="Analyze Performance",
                                 command=lambda: controller.show_frame("Benchmark"))
        solve_button.pack()
        bench_button.pack()


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
