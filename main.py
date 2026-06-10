import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class SalesAnalyzer:
    def __init__(self, root, df):
        self.root = root
        self.root.title("Анализ продаж")
        self.root.geometry("1200x800")

        self.df = df

        # Получаем уникальные категории (0-100)
        self.categories = sorted([c for c in df['cat_code'].unique() if 0 <= c <= 100])

        # Создаем вкладки
        self.setup_tabs()

    def setup_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        self.create_lineplot_tab()
        self.create_barchart_tab()
        self.create_histogram_tab()
        self.create_heatmap_tab()
        self.create_scatter_tab()

    # ============ ВКЛАДКА 1: ЛИНЕЙНЫЙ ГРАФИК ============
    def create_lineplot_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Линейный график")

        # Верхняя панель с настройками
        frame = ttk.LabelFrame(tab, text="Настройки", padding=10)
        frame.pack(fill='x', padx=10, pady=5)

        # Категория
        ttk.Label(frame, text="Категория:").grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.line_cat = ttk.Combobox(frame, values=["Все"] + self.categories, state="readonly")
        self.line_cat.set("Все")
        self.line_cat.grid(row=0, column=1, pady=5, padx=5)

        # Масштаб
        ttk.Label(frame, text="Масштаб:").grid(row=0, column=2, sticky='w', pady=5, padx=5)
        self.line_scale = ttk.Combobox(frame, values=["week", "month", "year"], state="readonly")
        self.line_scale.set("week")
        self.line_scale.grid(row=0, column=3, pady=5, padx=5)

        # Агрегация
        ttk.Label(frame, text="Агрегация:").grid(row=0, column=4, sticky='w', pady=5, padx=5)
        self.line_func = ttk.Combobox(frame, values=["sum", "mean"], state="readonly")
        self.line_func.set("sum")
        self.line_func.grid(row=0, column=5, pady=5, padx=5)

        # Кнопка
        ttk.Button(frame, text="Построить", command=self.update_lineplot).grid(row=0, column=6, pady=5, padx=20)

        # Область для графика
        self.line_frame = ttk.Frame(tab)
        self.line_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.line_canvas = None
        self.line_toolbar = None

    def update_lineplot(self):
        cat = None if self.line_cat.get() == "Все" else int(self.line_cat.get())
        scale = self.line_scale.get()
        func = self.line_func.get()

        # Очищаем старый график
        if self.line_canvas:
            self.line_canvas.get_tk_widget().destroy()
            self.line_toolbar.destroy()

        # Показываем загрузку
        loading_label = ttk.Label(self.line_frame, text="Загрузка... Пожалуйста, подождите", font=("Arial", 14))
        loading_label.pack(expand=True)
        self.root.update()

        fig = self.create_lineplot(cat=cat, func=func, scale=scale)

        loading_label.destroy()

        if fig:
            self.line_canvas = FigureCanvasTkAgg(fig, master=self.line_frame)
            self.line_canvas.draw()

            # Добавляем панель инструментов
            self.line_toolbar = NavigationToolbar2Tk(self.line_canvas, self.line_frame)
            self.line_toolbar.update()

            self.line_canvas.get_tk_widget().pack(fill='both', expand=True)

    def create_lineplot(self, cat=None, func="sum", scale="week"):
        data = self.df.copy()

        if cat is not None:
            data = data[data['cat_code'] == cat]

        if len(data) == 0:
            messagebox.showerror("Ошибка", "Нет данных для выбранной категории")
            return None

        if scale == "week":
            data['time_group'] = pd.to_datetime(data['datetime']).dt.to_period('W')
        elif scale == "month":
            data['time_group'] = pd.to_datetime(data['datetime']).dt.to_period('M')
        elif scale == "year":
            data['time_group'] = pd.to_datetime(data['datetime']).dt.to_period('Y')
        else:
            return None

        if func == "sum":
            grouped = data.groupby('time_group')['total_cost'].sum().reset_index()
        else:
            grouped = data.groupby('time_group')['total_cost'].mean().reset_index()

        if scale == 'week':
            dates = pd.to_datetime(grouped['time_group'].astype(str).str.split('/').str[0])
            labels = dates.dt.strftime('Нед %W')
        elif scale == 'month':
            labels = grouped['time_group'].astype(str).str[:7]
        else:
            labels = grouped['time_group'].astype(str)

        n_ticks = min(10, len(grouped))
        step = max(1, len(grouped) // n_ticks)
        tick_positions = range(0, len(grouped), step)
        tick_labels = [labels[i] for i in tick_positions]

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=grouped, x=range(len(grouped)), y='total_cost', ax=ax)

        agg_name = "Сумма" if func == "sum" else "Среднее"
        scale_name = {"week": "неделям", "month": "месяцам", "year": "годам"}
        title = f"{agg_name} выручки по {scale_name[scale]}"
        if cat is not None:
            title += f" | Категория: {cat}"
        ax.set_title(title)
        ax.set_xlabel(scale.capitalize())
        ax.set_ylabel(f"{agg_name} выручки")
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, rotation=45)

        plt.tight_layout()
        return fig

    # ============ ВКЛАДКА 2: СТОЛБЧАТАЯ ============
    def create_barchart_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Столбчатая диаграмма")

        frame = ttk.LabelFrame(tab, text="Настройки", padding=10)
        frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame, text="Категория:").grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.bar_cat = ttk.Combobox(frame, values=["Все"] + self.categories, state="readonly")
        self.bar_cat.set("Все")
        self.bar_cat.grid(row=0, column=1, pady=5, padx=5)

        ttk.Button(frame, text="Построить", command=self.update_barchart).grid(row=0, column=2, pady=5, padx=20)

        self.bar_frame = ttk.Frame(tab)
        self.bar_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.bar_canvas = None
        self.bar_toolbar = None

    def update_barchart(self):
        cat = None if self.bar_cat.get() == "Все" else int(self.bar_cat.get())

        if self.bar_canvas:
            self.bar_canvas.get_tk_widget().destroy()
            if self.bar_toolbar:
                self.bar_toolbar.destroy()

        loading_label = ttk.Label(self.bar_frame, text="Загрузка... Пожалуйста, подождите", font=("Arial", 14))
        loading_label.pack(expand=True)
        self.root.update()

        fig = self.create_barchart(cat=cat)

        loading_label.destroy()

        if fig:
            self.bar_canvas = FigureCanvasTkAgg(fig, master=self.bar_frame)
            self.bar_canvas.draw()
            self.bar_toolbar = NavigationToolbar2Tk(self.bar_canvas, self.bar_frame)
            self.bar_toolbar.update()
            self.bar_canvas.get_tk_widget().pack(fill='both', expand=True)

    def create_barchart(self, cat=None):
        data = self.df.copy()
        if cat is not None:
            data = data[data['cat_code'] == cat]

        days_order = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        grouped = data.groupby('week_day')['total_cost'].sum().reset_index()

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=grouped, x='week_day', y='total_cost', order=days_order, ax=ax)

        title = "Выручка по дням недели"
        if cat is not None:
            title += f" | Категория: {cat}"
        ax.set_title(title)
        ax.set_xlabel("День недели")
        ax.set_ylabel("Выручка")
        ax.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        return fig

    # ============ ВКЛАДКА 3: ГИСТОГРАММА ============
    def create_histogram_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Гистограмма")

        frame = ttk.LabelFrame(tab, text="Настройки", padding=10)
        frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame, text="Категория:").grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.hist_cat = ttk.Combobox(frame, values=["Все"] + self.categories, state="readonly")
        self.hist_cat.set("Все")
        self.hist_cat.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(frame, text="Интервалы:").grid(row=0, column=2, sticky='w', pady=5, padx=5)
        self.hist_bins = ttk.Combobox(frame, values=[10, 20, 30, 50], state="readonly")
        self.hist_bins.set(30)
        self.hist_bins.grid(row=0, column=3, pady=5, padx=5)

        ttk.Button(frame, text="Построить", command=self.update_histogram).grid(row=0, column=4, pady=5, padx=20)

        self.hist_frame = ttk.Frame(tab)
        self.hist_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.hist_canvas = None
        self.hist_toolbar = None

    def update_histogram(self):
        cat = None if self.hist_cat.get() == "Все" else int(self.hist_cat.get())
        bins = int(self.hist_bins.get())

        if self.hist_canvas:
            self.hist_canvas.get_tk_widget().destroy()
            if self.hist_toolbar:
                self.hist_toolbar.destroy()

        loading_label = ttk.Label(self.hist_frame, text="Загрузка... Пожалуйста, подождите", font=("Arial", 14))
        loading_label.pack(expand=True)
        self.root.update()

        fig = self.create_histogram(cat=cat, bins=bins)

        loading_label.destroy()

        if fig:
            self.hist_canvas = FigureCanvasTkAgg(fig, master=self.hist_frame)
            self.hist_canvas.draw()
            self.hist_toolbar = NavigationToolbar2Tk(self.hist_canvas, self.hist_frame)
            self.hist_toolbar.update()
            self.hist_canvas.get_tk_widget().pack(fill='both', expand=True)

    def create_histogram(self, cat=None, bins=30):
        data = self.df.copy()
        if cat is not None:
            data = data[data['cat_code'] == cat]

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.histplot(data=data, x='total_cost', bins=bins, ax=ax)

        title = "Распределение стоимости покупок"
        if cat is not None:
            title += f" | Категория: {cat}"
        ax.set_title(title)
        ax.set_xlabel("Стоимость покупки")
        ax.set_ylabel("Количество")

        plt.tight_layout()
        return fig

    # ============ ВКЛАДКА 4: ТЕПЛОВАЯ КАРТА ============
    def create_heatmap_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Тепловая карта")

        frame = ttk.LabelFrame(tab, text="Настройки", padding=10)
        frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame, text="Категория:").grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.heat_cat = ttk.Combobox(frame, values=["Все"] + self.categories, state="readonly")
        self.heat_cat.set("Все")
        self.heat_cat.grid(row=0, column=1, pady=5, padx=5)

        ttk.Button(frame, text="Построить", command=self.update_heatmap).grid(row=0, column=2, pady=5, padx=20)

        self.heat_frame = ttk.Frame(tab)
        self.heat_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.heat_canvas = None
        self.heat_toolbar = None

    def update_heatmap(self):
        cat = None if self.heat_cat.get() == "Все" else int(self.heat_cat.get())

        if self.heat_canvas:
            self.heat_canvas.get_tk_widget().destroy()
            if self.heat_toolbar:
                self.heat_toolbar.destroy()

        loading_label = ttk.Label(self.heat_frame, text="Загрузка... Пожалуйста, подождите", font=("Arial", 14))
        loading_label.pack(expand=True)
        self.root.update()

        fig = self.create_heatmap(cat=cat)

        loading_label.destroy()

        if fig:
            self.heat_canvas = FigureCanvasTkAgg(fig, master=self.heat_frame)
            self.heat_canvas.draw()
            self.heat_toolbar = NavigationToolbar2Tk(self.heat_canvas, self.heat_frame)
            self.heat_toolbar.update()
            self.heat_canvas.get_tk_widget().pack(fill='both', expand=True)

    def create_heatmap(self, cat=None):
        data = self.df.copy()
        if cat is not None:
            data = data[data['cat_code'] == cat]

        data['hour'] = pd.to_datetime(data['datetime']).dt.hour

        days_order = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        pivot = data.pivot_table(index='week_day', columns='hour',
                                 values='total_cost', aggfunc='sum', fill_value=0)
        pivot = pivot.reindex(days_order)

        fig, ax = plt.subplots(figsize=(14, 6))
        # Убираем подписи внутри клеток (annot=False)
        sns.heatmap(pivot, annot=False, cmap='YlOrRd', ax=ax)

        title = "Выручка по дням и часам"
        if cat is not None:
            title += f" | Категория: {cat}"
        ax.set_title(title)
        ax.set_xlabel("Час")
        ax.set_ylabel("День недели")

        plt.tight_layout()
        return fig

    # ============ ВКЛАДКА 5: ТОЧЕЧНЫЙ ============
    def create_scatter_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Точечный график")

        frame = ttk.LabelFrame(tab, text="Настройки", padding=10)
        frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(frame, text="Категория:").grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.scatter_cat = ttk.Combobox(frame, values=["Все"] + self.categories, state="readonly")
        self.scatter_cat.set("Все")
        self.scatter_cat.grid(row=0, column=1, pady=5, padx=5)

        # Чекбокс для сэмплирования
        self.sample_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Сэмплировать (10000 точек)", variable=self.sample_var).grid(row=0, column=2,
                                                                                                 pady=5, padx=5)

        ttk.Button(frame, text="Построить", command=self.update_scatter).grid(row=0, column=3, pady=5, padx=20)

        self.scatter_frame = ttk.Frame(tab)
        self.scatter_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.scatter_canvas = None
        self.scatter_toolbar = None

    def update_scatter(self):
        cat = None if self.scatter_cat.get() == "Все" else int(self.scatter_cat.get())
        use_sample = self.sample_var.get()

        if self.scatter_canvas:
            self.scatter_canvas.get_tk_widget().destroy()
            if self.scatter_toolbar:
                self.scatter_toolbar.destroy()

        loading_label = ttk.Label(self.scatter_frame, text="Загрузка... Пожалуйста, подождите", font=("Arial", 14))
        loading_label.pack(expand=True)
        self.root.update()

        fig = self.create_scatter(cat=cat, use_sample=use_sample)

        loading_label.destroy()

        if fig:
            self.scatter_canvas = FigureCanvasTkAgg(fig, master=self.scatter_frame)
            self.scatter_canvas.draw()
            self.scatter_toolbar = NavigationToolbar2Tk(self.scatter_canvas, self.scatter_frame)
            self.scatter_toolbar.update()
            self.scatter_canvas.get_tk_widget().pack(fill='both', expand=True)

    def create_scatter(self, cat=None, use_sample=True):
        data = self.df.copy()
        if cat is not None:
            data = data[data['cat_code'] == cat]

        # Для большого объема данных берем сэмпл
        if use_sample and len(data) > 10000:
            data = data.sample(n=10000, random_state=42)

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.scatterplot(data=data, x='price', y='total_cost',
                        hue='is_discounted', alpha=0.5, ax=ax)

        title = "Зависимость стоимости от цены товара"
        if cat is not None:
            title += f" | Категория: {cat}"
        if use_sample and len(self.df) > 10000:
            title += f" (сэмпл: {len(data)} точек из {len(self.df)})"
        ax.set_title(title)
        ax.set_xlabel("Цена товара")
        ax.set_ylabel("Итоговая стоимость")

        plt.tight_layout()
        return fig


# ============ ЗАПУСК ============
if __name__ == "__main__":
    # Загружаем данные
    try:
        df = pd.read_csv("processed_data.csv")
        print(f"Данные загружены: {len(df)} строк")
        print(f"Колонки: {df.columns.tolist()}")
    except FileNotFoundError:
        print("Файл processed_data.csv не найден!")
        exit(1)

    root = tk.Tk()
    app = SalesAnalyzer(root, df)
    root.mainloop()