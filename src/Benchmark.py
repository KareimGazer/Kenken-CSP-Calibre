# performance analyze
import tkinter as tk                # python 3
from tkinter import font as tkfont  # python 3
from tkinter import filedialog, messagebox, ttk
import csv
from turtle import width
import kenken


class Benchmark(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # Frame for TreeView
        file_frame = tk.LabelFrame(self, text="Performance Data")
        file_frame.place(height=400, width=1000)

        # Treeview Widget
        self.tv1 = ttk.Treeview(file_frame)
        # set the height and width of the widget to 100% of its container (file_frame).
        self.tv1.place(relheight=1, relwidth=1)

        # command means update the yaxis view of the widget
        treescrolly = tk.Scrollbar(
            file_frame, orient="vertical", command=self.tv1.yview)
        # command means update the xaxis view of the widget
        treescrollx = tk.Scrollbar(
            file_frame, orient="horizontal", command=self.tv1.xview)
        # assign the scrollbars to the Treeview Widget
        self.tv1.configure(xscrollcommand=treescrollx.set,
                           yscrollcommand=treescrolly.set)
        # make the scrollbar fill the x axis of the Treeview widget
        treescrollx.pack(side="bottom", fill="x")
        # make the scrollbar fill the y axis of the Treeview widget
        treescrolly.pack(side="right", fill="y")

        # Frame for open file dialog
        control_frame = tk.LabelFrame(self, text="Configure")
        control_frame.place(height=200, width=500, rely=0.65, relx=0.23)

        return_button = tk.Button(control_frame, text="Go to the start page",
                                  command=lambda: controller.show_frame("StartPage"))
        return_button.place(rely=0.9, relx=0.9)
        return_button.pack()

        # check boxes
        self.BT_var = tk.IntVar()
        check_BT = tk.Checkbutton(
            control_frame, text="BT", variable=self.BT_var)
        check_BT.place(rely=0.2, relx=0.10)

        self.FC_var = tk.IntVar()
        check_FC = tk.Checkbutton(
            control_frame, text="FC", variable=self.FC_var)
        check_FC.place(rely=0.2, relx=0.20)

        self.MAC_var = tk.IntVar()
        check_AC = tk.Checkbutton(
            control_frame, text="AC", variable=self.MAC_var)
        check_AC.place(rely=0.2, relx=0.30)

        self.MRV_var = tk.IntVar()
        check_AC = tk.Checkbutton(
            control_frame, text="MRV", variable=self.MRV_var)
        check_AC.place(rely=0.4, relx=0.10)

        self.LCV_var = tk.IntVar()
        check_AC = tk.Checkbutton(
            control_frame, text="LCV", variable=self.LCV_var)
        check_AC.place(rely=0.4, relx=0.20)

        # box
        size_label = ttk.Label(control_frame, text="Max board size")
        size_label.place(rely=0.2, relx=0.5)

        board_size_widget = tk.Entry(control_frame)
        board_size_widget.place(rely=0.3, relx=0.50)
        self.board_size = board_size_widget

        # box
        iters_label = ttk.Label(control_frame, text="iterations number")
        iters_label.place(rely=0.4, relx=0.5)

        board_size_widget = tk.Entry(control_frame)
        board_size_widget.place(rely=0.5, relx=0.50)
        self.iters_num = board_size_widget

        run_button = tk.Button(control_frame, text="Analyze Performance",
                               command=lambda: self.print_info())
        run_button.place(height=50, width=150, rely=0.65, relx=0.40)

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
            # inserts each list into the treeview. For parameters see https://docs.python.org/3/library/tkinter.ttk.html#tkinter.ttk.Treeview.insert
            self.tv1.insert("", "end", values=row)
        return None

    def print_info(self):
        size, iters_num = int(self.board_size.get()), int(
            self.iters_num.get())

        is_mrv, is_lcv = self.MRV_var.get(), self.LCV_var.get()
        is_BT, is_FC, is_MAC = self.BT_var.get(), self.FC_var.get(), self.MAC_var.get()

        algorithms = kenken.configure_algorithms(
            is_mrv, is_lcv, is_BT, is_FC, is_MAC)
        kenken.gather_info(size, iters_num, "kenken.csv", algorithms)
        print("data ready to be loaded")
        self.Load_excel_data()
