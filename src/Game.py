# performance analyze
import tkinter as tk                # python 3
from tkinter import font as tkfont  # python 3
from tkinter import filedialog, messagebox, ttk
import csv
import csp
import kenken


class Game(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Frame for TreeView
        grid_frame = tk.LabelFrame(self, text="Game Grid")
        grid_frame.place(height=480, width=1000)

        self.width = 450

        self.canvas = tk.Canvas(
            grid_frame, width=self.width, height=self.width, borderwidth=0, highlightthickness=0)
        self.canvas.pack()

        # self.draw_canvas()

        # Frame for open file dialog
        control_frame = tk.LabelFrame(self, text="Controls")
        control_frame.place(height=200, width=500, rely=0.7, relx=0.23)

        # radio buttons
        self.algorithm = tk.StringVar(control_frame, "BT")
        check_BT = tk.Radiobutton(control_frame, text="BT", variable=self.algorithm,
                                  value='BT', indicator=1)
        check_BT.place(rely=0.2, relx=0.1)

        check_FC = tk.Radiobutton(control_frame, text='FC', variable=self.algorithm,
                                  value='FC', indicator=1)
        check_FC.place(rely=0.2, relx=0.2)

        check_AC = tk.Radiobutton(control_frame, text='MAC', variable=self.algorithm,
                                  value='MAC', indicator=1)
        check_AC.place(rely=0.2, relx=0.3)

        # check box
        self.MRV_var = tk.IntVar()
        check_AC = tk.Checkbutton(
            control_frame, text="MRV", variable=self.MRV_var)
        check_AC.place(rely=0.4, relx=0.10)

        self.LCV_var = tk.IntVar()
        check_AC = tk.Checkbutton(
            control_frame, text="LCV", variable=self.LCV_var)
        check_AC.place(rely=0.4, relx=0.20)

        # int box
        size_label = ttk.Label(control_frame, text="Max board size")
        size_label.place(rely=0.2, relx=0.5)

        self.board_size_widget = tk.Entry(control_frame)
        self.board_size_widget.place(rely=0.3, relx=0.50)
        # self.board_size = int(board_size_widget.get())

        # buttons
        return_button = tk.Button(control_frame, text="Go to the start page",
                                  command=lambda: controller.show_frame("StartPage"))
        return_button.place(rely=0.9, relx=0.9)
        return_button.pack()

        gen_button = tk.Button(control_frame, text="Generate Board",
                               command=lambda: self.draw_canvas())
        gen_button.place(height=50, width=150, rely=0.65, relx=0.15)

        sol_button = tk.Button(control_frame, text="Solve Puzzel",
                               command=lambda: self.solve())
        sol_button.place(height=50, width=150, rely=0.65, relx=0.50)

    def draw_canvas(self):
        self.rows = int(self.board_size_widget.get())
        self.cellwidth = int(self.width / self.rows)
        self.rect = {}
        self.cells = {}
        for column in range(self.rows):
            for row in range(self.rows):
                x1 = column*self.cellwidth
                y1 = row * self.cellwidth
                x2 = x1 + self.cellwidth
                y2 = y1 + self.cellwidth
                self.rect[row, column] = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill="white", tags="rect", outline='gray')
                # indexed the same way as kenken
                self.cells[column, row] = [x1, y1, x2, y2]
        self.size, self.cliques = kenken.generate(self.rows)

        for clique in self.cliques:
            elements = clique[0]
            operation = clique[1]
            limit = clique[2]
            for element in elements:
                x1, y1, x2, y2 = self.cells[element[0]-1, element[1]-1]
                # . operation may mean written cell
                if operation != '.':
                    self.canvas.create_text(
                        (x1+25, y1+15), text=str(limit)+' '+operation)
                else:
                    self.canvas.create_text((x1+25, y1+15), text=str(limit))

    def solve(self):
        kenken_puzzel = kenken.Kenken(self.size, self.cliques)
        algorithm = kenken.get_algorithm(
            self.MRV_var.get(), self.LCV_var.get(), self.algorithm.get())
        assignments = algorithm(kenken_puzzel)  # to be modified
        for assigment in assignments:
            locations = assigment
            values = assignments[assigment]
            # print(list(zip(locations, values)))
            for location, value in (list(zip(locations, values))):
                x1, y1, x2, y2 = self.cells[location[0]-1, location[1]-1]
                center = ((x1+x2)/2), ((y1+y2)/2)
                self.canvas.create_text(
                    (center[0], center[1]), text=str(value))

    def get_data(self):
        with open('kenken.csv', newline='') as csvfile:
            data_list = csv.reader(csvfile)
            return list(data_list)

    def clear_data(self):
        self.tv1.delete(*self.tv1.get_children())
        return None

    def Load_excel_data(self):
        self.clear_data()
        data_list = self.get_data()

        self.tv1["column"] = data_list[0]
        self.tv1["show"] = "headings"
        for column in self.tv1["columns"]:
            # let the column heading = column name
            self.tv1.heading(column, text=column)

        for row in data_list[1:]:
            self.tv1.insert("", "end", values=row)
        return None

    def print_info(self):
        print("data ready to be loaded")
        self.Load_excel_data()
