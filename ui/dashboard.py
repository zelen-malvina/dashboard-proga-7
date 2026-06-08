import tkinter as tk

from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

import pandas as pd

import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)

from processing.df_proc import (
    preprocess_data,
    create_heatmap_data,
    get_numeric_columns,
    get_categorical_columns,
    apply_filters
)

from ui.charts import (
    draw_chart
)

from utils.file_loader import (
    load_csv_file,
    detect_column_types,
    get_file_info
)

from utils.threading_tools import (
    ThreadManager
)


class DashboardApp:

    def __init__(self):

        self.df_raw = None
        self.df_work = None
        self._loading = False

        self.thread_manager = ThreadManager()

        self.root = tk.Tk()

        self.root.title(
            "Интерактивный аналитический дашборд"
        )

        self.root.geometry(
            "1400x900"
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )

        plt.rcParams[
            "font.sans-serif"
        ] = [
            "Arial",
            "DejaVu Sans"
        ]

        plt.rcParams[
            "axes.unicode_minus"
        ] = False

        self.fig = plt.Figure(
            figsize=(10, 6),
            dpi=100
        )

        self.create_variables()

        self.create_layout()

    def create_variables(self):

        self.chart_var = tk.StringVar(
            value="Линейный"
        )

        self.x_var = tk.StringVar()

        self.y_var = tk.StringVar()

        self.category_var = tk.StringVar(
            value="Все"
        )

        self.agg_var = tk.StringVar(
            value="sum"
        )

        self.smoothing_var = tk.BooleanVar(
            value=False
        )

        self.info_var = tk.StringVar(
            value="Файл не загружен"
        )

    def create_layout(self):

        self.notebook = ttk.Notebook(
            self.root
        )

        self.notebook.pack(
            fill=tk.BOTH,
            expand=True
        )

        self.chart_tab = ttk.Frame(
            self.notebook
        )

        self.data_tab = ttk.Frame(
            self.notebook
        )

        self.notebook.add(
            self.chart_tab,
            text="Графики"
        )

        self.notebook.add(
            self.data_tab,
            text="Данные"
        )

        self.create_chart_tab()

        self.create_data_tab()

    def create_chart_tab(self):

        self.control_frame = tk.Frame(
            self.chart_tab
        )

        self.control_frame.pack(
            fill=tk.X,
            padx=10,
            pady=5
        )

        self.plot_frame = tk.Frame(
            self.chart_tab,
            relief=tk.SUNKEN,
            bd=1
        )

        self.plot_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=10,
            pady=5
        )

        self.create_controls()

        self.canvas = FigureCanvasTkAgg(
            self.fig,
            master=self.plot_frame
        )

        self.canvas.get_tk_widget().pack(
            fill=tk.BOTH,
            expand=True
        )

        self.toolbar = NavigationToolbar2Tk(
            self.canvas,
            self.plot_frame
        )

        self.toolbar.update()

        self.toolbar.pack(
            side=tk.TOP,
            fill=tk.X
        )

    def create_controls(self):

        self.load_btn = tk.Button(
            self.control_frame,
            text="Загрузить CSV",
            command=self.load_csv
        )

        self.load_btn.grid(
            row=0,
            column=0,
            padx=5,
            pady=5
        )

        tk.Label(
            self.control_frame,
            text="Тип графика"
        ).grid(
            row=0,
            column=1
        )

        self.chart_combo = ttk.Combobox(
            self.control_frame,
            textvariable=self.chart_var,
            state="readonly",
            width=15
        )

        self.chart_combo["values"] = [
            "Линейный",
            "Столбчатый",
            "Точечный",
            "HeatMap",
            "Гистограмма",
            "BoxPlot"
        ]

        self.chart_combo.grid(
            row=0,
            column=2,
            padx=5
        )

        tk.Label(
            self.control_frame,
            text="X"
        ).grid(
            row=0,
            column=3
        )

        self.x_combo = ttk.Combobox(
            self.control_frame,
            textvariable=self.x_var,
            state="readonly",
            width=20
        )

        self.x_combo.grid(
            row=0,
            column=4,
            padx=5
        )

        tk.Label(
            self.control_frame,
            text="Y"
        ).grid(
            row=0,
            column=5
        )

        self.y_combo = ttk.Combobox(
            self.control_frame,
            textvariable=self.y_var,
            state="readonly",
            width=20
        )

        self.y_combo.grid(
            row=0,
            column=6,
            padx=5
        )

        tk.Label(
            self.control_frame,
            text="Категория"
        ).grid(
            row=0,
            column=7
        )

        self.category_combo = ttk.Combobox(
            self.control_frame,
            textvariable=self.category_var,
            state="readonly",
            width=20
        )

        self.category_combo.grid(
            row=0,
            column=8,
            padx=5
        )

        tk.Checkbutton(
            self.control_frame,
            text="Сглаживание",
            variable=self.smoothing_var
        ).grid(
            row=0,
            column=9,
            padx=5
        )

        tk.Label(
            self.control_frame,
            text="Агрегация"
        ).grid(
            row=1,
            column=0
        )

        ttk.Radiobutton(
            self.control_frame,
            text="Sum",
            variable=self.agg_var,
            value="sum"
        ).grid(
            row=1,
            column=1
        )

        ttk.Radiobutton(
            self.control_frame,
            text="Mean",
            variable=self.agg_var,
            value="mean"
        ).grid(
            row=1,
            column=2
        )

        ttk.Radiobutton(
            self.control_frame,
            text="Median",
            variable=self.agg_var,
            value="median"
        ).grid(
            row=1,
            column=3
        )

        tk.Button(
            self.control_frame,
            text="Обновить",
            command=self.refresh_async
        ).grid(
            row=1,
            column=8,
            padx=5
        )

        tk.Button(
            self.control_frame,
            text="Экспорт",
            command=self.export_plot
        ).grid(
            row=1,
            column=9,
            padx=5
        )

        tk.Label(
            self.control_frame,
            textvariable=self.info_var
        ).grid(
            row=2,
            column=0,
            columnspan=10,
            sticky="w"
        )

    def create_data_tab(self):

        self.tree = ttk.Treeview(
            self.data_tab
        )

        self.tree.pack(
            fill=tk.BOTH,
            expand=True
        )

    def load_csv(self):

        if self._loading:
            return

        filepath = filedialog.askopenfilename(
            filetypes=[
                ("CSV files", "*.csv")
            ]
        )

        if not filepath:
            return

        self._loading = True
        self.load_btn.config(state=tk.DISABLED)
        self.info_var.set("Загрузка файла...")

        future = self.thread_manager.run_task(
            self._load_csv_worker,
            filepath
        )

        self.root.after(
            100,
            lambda: self.check_load_future(
                future
            )
        )

    def _load_csv_worker(
            self,
            filepath
    ):

        df_raw = load_csv_file(filepath)
        df_work = preprocess_data(df_raw)
        info = get_file_info(df_work)

        numeric_columns = get_numeric_columns(df_work)
        all_columns = df_work.columns.tolist()
        categorical_columns = get_categorical_columns(df_work)

        category_values = ["Все"]

        if categorical_columns:
            column = categorical_columns[0]
            series = (
                df_work[column]
                .astype(str)
            )

            if series.nunique() > 100:
                unique_values = (
                    series
                    .value_counts()
                    .head(100)
                    .index
                    .tolist()
                )
            else:
                unique_values = (
                    series
                    .unique()
                    .tolist()
                )

            category_values.extend(unique_values)

        return {
            "df_raw": df_raw,
            "df_work": df_work,
            "info": info,
            "all_columns": all_columns,
            "numeric_columns": numeric_columns,
            "category_values": category_values
        }

    def check_load_future(
            self,
            future
    ):

        if future.done():

            self._loading = False
            self.load_btn.config(state=tk.NORMAL)

            try:
                result = future.result()
                self.on_csv_loaded(result)

            except Exception as error:
                self.info_var.set("Файл не загружен")
                messagebox.showerror(
                    "Ошибка",
                    str(error)
                )

        else:
            self.root.after(
                100,
                lambda: self.check_load_future(
                    future
                )
            )

    def on_csv_loaded(
            self,
            result
    ):

        self.df_raw = result["df_raw"]
        self.df_work = result["df_work"]

        self.x_combo["values"] = result["all_columns"]
        self.y_combo["values"] = result["numeric_columns"]

        if result["all_columns"]:
            self.x_var.set(result["all_columns"][0])

        if result["numeric_columns"]:
            self.y_var.set(result["numeric_columns"][0])

        self.category_combo["values"] = (
            result["category_values"]
        )
        self.category_var.set("Все")

        self.update_table()

        info = result["info"]
        self.info_var.set(
            f"Строк: {info['rows']} | "
            f"Колонок: {info['columns']} | "
            f"Пропусков: {info['missing']} | "
            f"Память: {info['memory_mb']} MB"
        )

        self.refresh_async()

    def update_column_selectors(self):

        numeric_columns = (
            get_numeric_columns(
                self.df_work
            )
        )

        all_columns = (
            self.df_work.columns
            .tolist()
        )

        self.x_combo["values"] = (
            all_columns
        )

        self.y_combo["values"] = (
            numeric_columns
        )

        if all_columns:
            self.x_var.set(
                all_columns[0]
            )

        if numeric_columns:
            self.y_var.set(
                numeric_columns[0]
            )

        categorical_columns = (
            get_categorical_columns(
                self.df_work
            )
        )

        values = ["Все"]

        if categorical_columns:

            column = categorical_columns[0]
            series = (
                self.df_work[column]
                .astype(str)
            )

            if series.nunique() > 100:
                unique_values = (
                    series
                    .value_counts()
                    .head(100)
                    .index
                    .tolist()
                )
            else:
                unique_values = (
                    series
                    .unique()
                    .tolist()
                )

            values.extend(unique_values)

        self.category_combo["values"] = (
            values
        )

        self.category_var.set(
            "Все"
        )

    def update_table(self):

        self.tree.delete(
            *self.tree.get_children()
        )

        self.tree["columns"] = list(
            self.df_work.columns
        )

        self.tree["show"] = "headings"

        for column in self.df_work.columns:

            self.tree.heading(
                column,
                text=column
            )

            self.tree.column(
                column,
                width=120
            )

        preview = self.df_work.head(
            100
        )

        for row in preview.values:

            self.tree.insert(
                "",
                tk.END,
                values=list(row)
            )

    def refresh_async(self):

        if self.df_work is None:
            return

        future = (
            self.thread_manager.run_task(
                self.prepare_plot
            )
        )

        self.root.after(
            100,
            lambda:
            self.check_future(
                future
            )
        )

    def check_future(
            self,
            future
    ):

        if future.done():

            try:

                result = (
                    future.result()
                )

                self.draw(
                    result
                )

            except Exception as error:

                messagebox.showerror(
                    "Ошибка",
                    str(error)
                )

        else:

            self.root.after(
                100,
                lambda:
                self.check_future(
                    future
                )
            )

    def prepare_plot(self):

        df = self.df_work.copy()

        chart_type = (
            self.chart_var.get()
        )

        heatmap_data = None

        if chart_type == "HeatMap":

            heatmap_data = (
                create_heatmap_data(
                    df
                )
            )

        return {
            "df": df,
            "heatmap": heatmap_data
        }

    def draw(
            self,
            result
    ):

        draw_chart(
            chart_type=self.chart_var.get(),
            fig=self.fig,
            df=result["df"],
            x_col=self.x_var.get(),
            y_col=self.y_var.get(),
            heatmap_data=result["heatmap"],
            use_smoothing=self.smoothing_var.get()
        )

        self.canvas.draw_idle()

    def export_plot(self):

        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("PDF", "*.pdf")
            ]
        )

        if not filepath:
            return

        self.fig.savefig(
            filepath,
            dpi=300,
            bbox_inches="tight"
        )

        messagebox.showinfo(
            "Готово",
            "График сохранён"
        )

    def on_close(self):

        self.thread_manager.shutdown()

        self.root.destroy()

    def run(self):

        self.root.mainloop()