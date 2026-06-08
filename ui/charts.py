import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt


# =====================================================
# Очистка фигуры
# =====================================================

def clear_figure(fig):
    fig.clear()


# =====================================================
# Линейный график
# =====================================================

def plot_line(
        fig,
        df,
        x_col,
        y_col,
        use_smoothing=False
):

    clear_figure(fig)

    ax = fig.add_subplot(111)

    temp_df = df.copy()
    temp_df = temp_df.head(5000)

    if use_smoothing:

        temp_df = temp_df.sort_values(
            by=x_col
        )

        temp_df[y_col] = (
            temp_df[y_col]
            .rolling(7)
            .mean()
        )

    sns.lineplot(
        data=temp_df,
        x=x_col,
        y=y_col,
        ax=ax
    )

    ax.set_title(
        f"{y_col} по {x_col}"
    )

    ax.grid(True)

    fig.tight_layout()


# =====================================================
# Столбчатый график
# =====================================================

def plot_bar(
        fig,
        df,
        x_col,
        y_col
):

    clear_figure(fig)

    ax = fig.add_subplot(111)

    sns.barplot(
        data=df,
        x=x_col,
        y=y_col,
        ax=ax
    )

    ax.set_title(
        f"{y_col} по {x_col}"
    )

    fig.tight_layout()


# =====================================================
# Scatter
# =====================================================

def plot_scatter(
        fig,
        df,
        x_col,
        y_col
):

    clear_figure(fig)

    temp_df = df.head(10000)

    ax = fig.add_subplot(111)

    sns.scatterplot(
        data=temp_df,
        x=x_col,
        y=y_col,
        ax=ax
    )

    ax.set_title(
        f"{y_col} vs {x_col}"
    )

    fig.tight_layout()


# =====================================================
# HeatMap
# =====================================================

def plot_heatmap(
        fig,
        pivot_df
):

    clear_figure(fig)

    ax = fig.add_subplot(111)

    if pivot_df is None or pivot_df.empty:

        ax.text(
            0.5,
            0.5,
            "Нет данных для HeatMap",
            ha="center",
            va="center"
        )

        fig.tight_layout()
        return

    sns.heatmap(
        pivot_df,
        annot=True,
        cmap="YlGnBu",
        ax=ax
    )

    ax.set_title(
        "Тепловая карта"
    )

    fig.tight_layout()


# =====================================================
# Гистограмма
# =====================================================

def plot_histogram(
        fig,
        df,
        column
):

    clear_figure(fig)

    ax = fig.add_subplot(111)

    sns.histplot(
        data=df,
        x=column,
        kde=True,
        ax=ax
    )

    ax.set_title(
        f"Распределение {column}"
    )

    fig.tight_layout()


# =====================================================
# BoxPlot
# =====================================================

def plot_boxplot(
        fig,
        df,
        column
):

    clear_figure(fig)

    ax = fig.add_subplot(111)

    sns.boxplot(
        y=df[column],
        ax=ax
    )

    ax.set_title(
        f"BoxPlot {column}"
    )

    fig.tight_layout()


# =====================================================
# Универсальная функция отрисовки
# =====================================================

def draw_chart(
        chart_type,
        fig,
        df,
        x_col=None,
        y_col=None,
        heatmap_data=None,
        use_smoothing=False
):

    if chart_type == "Линейный":

        plot_line(
            fig,
            df,
            x_col,
            y_col,
            use_smoothing
        )

    elif chart_type == "Столбчатый":

        plot_bar(
            fig,
            df,
            x_col,
            y_col
        )

    elif chart_type == "Точечный":

        plot_scatter(
            fig,
            df,
            x_col,
            y_col
        )

    elif chart_type == "HeatMap":

        plot_heatmap(
            fig,
            heatmap_data
        )

    elif chart_type == "Гистограмма":

        plot_histogram(
            fig,
            df,
            x_col
        )

    elif chart_type == "BoxPlot":

        plot_boxplot(
            fig,
            df,
            y_col
        )