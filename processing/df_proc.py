import pandas as pd
import numpy as np


# ==========================================================
# Очистка данных
# ==========================================================

def df_cleaner(df: pd.DataFrame) -> pd.DataFrame:
    new_df = df.copy()

    new_df = new_df.dropna()

    if "discount" in new_df.columns:

        new_df = new_df.loc[
            new_df["discount"] < 1
        ]

        new_df.loc[
            new_df["discount"] < 0,
            "discount"
        ] = 0

    if "qty" in new_df.columns:

        new_df = new_df.loc[
            new_df["qty"] > 0
        ]

    return new_df


# ==========================================================
# Feature Engineering
# ==========================================================

def df_new_col(df: pd.DataFrame) -> pd.DataFrame:
    new_df = df.copy()

    required_cols = {
        "price",
        "qty",
        "discount"
    }

    if required_cols.issubset(new_df.columns):

        new_df["total_cost"] = (
            new_df["price"]
            * new_df["qty"]
            * (1 - new_df["discount"])
        )

    if "ts" in new_df.columns:

        new_df["datetime"] = pd.to_datetime(
            new_df["ts"],
            unit="s"
        )

        days = {
            0: "Понедельник",
            1: "Вторник",
            2: "Среда",
            3: "Четверг",
            4: "Пятница",
            5: "Суббота",
            6: "Воскресенье"
        }

        new_df["week_day"] = (
            new_df["datetime"]
            .dt.dayofweek
            .map(days)
        )

        new_df["month"] = (
            new_df["datetime"]
            .dt.month
        )

        hours = (
            new_df["datetime"]
            .dt.hour
        )

        new_df["purchase_period"] = pd.cut(
            hours,
            bins=[0, 6, 12, 18, 24],
            labels=[
                "Ночь",
                "Утро",
                "День",
                "Вечер"
            ],
            include_lowest=True
        )

    if "discount" in new_df.columns:

        new_df["is_discounted"] = (
            new_df["discount"] > 0
        )

    return new_df


# ==========================================================
# Удаление выбросов через IQR
# ==========================================================

def remove_outliers(
    df: pd.DataFrame,
    column: str
) -> pd.DataFrame:

    new_df = df.copy()

    if column not in new_df.columns:
        return new_df

    q1 = new_df[column].quantile(0.25)

    q3 = new_df[column].quantile(0.75)

    iqr = q3 - q1

    lower = q1 - 1.5 * iqr

    upper = q3 + 1.5 * iqr

    new_df = new_df.loc[
        (new_df[column] >= lower)
        &
        (new_df[column] <= upper)
    ]

    return new_df


# ==========================================================
# Фильтрация
# Использует query()
# ==========================================================

def apply_filters(
    df: pd.DataFrame,
    category_column=None,
    category_value=None,
    date_from=None,
    date_to=None
) -> pd.DataFrame:

    new_df = df.copy()

    if (
        category_column
        and category_value
        and category_value != "Все"
    ):

        new_df = new_df.query(
            f"`{category_column}` == @category_value"
        )

    if (
        date_from is not None
        and "datetime" in new_df.columns
    ):

        new_df = new_df.loc[
            new_df["datetime"] >= date_from
        ]

    if (
        date_to is not None
        and "datetime" in new_df.columns
    ):

        new_df = new_df.loc[
            new_df["datetime"] <= date_to
        ]

    return new_df


# ==========================================================
# Агрегация
# groupby().agg()
# ==========================================================

def apply_grouping(
    df: pd.DataFrame,
    group_column: str,
    value_column: str,
    agg_type: str = "sum"
) -> pd.DataFrame:

    temp_df = df.copy()

    agg_map = {
        "sum": "sum",
        "mean": "mean",
        "median": "median",
        "min": "min",
        "max": "max"
    }

    agg_func = agg_map.get(
        agg_type,
        "sum"
    )

    result = (
        temp_df
        .groupby(group_column)
        .agg(
            value=(value_column, agg_func)
        )
        .reset_index()
    )

    return result


# ==========================================================
# Биннинг
# pd.cut()
# ==========================================================

def create_bins(
    df: pd.DataFrame,
    column: str,
    bins: int = 5
) -> pd.DataFrame:

    temp_df = df.copy()

    if column not in temp_df.columns:
        return temp_df

    temp_df[f"{column}_group"] = pd.cut(
        temp_df[column],
        bins=bins
    )

    return temp_df


# ==========================================================
# Скользящее среднее
# rolling()
# ==========================================================

def create_rolling_average(
    df: pd.DataFrame,
    value_column: str,
    window: int = 7
) -> pd.Series:

    temp_df = df.copy()

    return (
        temp_df[value_column]
        .rolling(window)
        .mean()
    )


# ==========================================================
# Агрегация по времени
# resample()
# ==========================================================

def resample_data(
    df: pd.DataFrame,
    value_column: str,
    period: str = "D"
) -> pd.DataFrame:

    temp_df = df.copy()

    if "datetime" not in temp_df.columns:
        return temp_df

    result = (
        temp_df
        .set_index("datetime")
        [value_column]
        .resample(period)
        .sum()
        .reset_index()
    )

    return result


# ==========================================================
# Данные для HeatMap
# pivot_table()
# ==========================================================

def create_heatmap_data(
    df: pd.DataFrame
) -> pd.DataFrame:

    temp_df = df.copy()

    if (
        "week_day" not in temp_df.columns
        or
        "purchase_period" not in temp_df.columns
        or
        "total_cost" not in temp_df.columns
    ):
        return pd.DataFrame()

    pivot = pd.pivot_table(
        temp_df,
        values="total_cost",
        index="week_day",
        columns="purchase_period",
        aggfunc="mean"
    )

    return pivot


# ==========================================================
# melt()
# ==========================================================

def create_melted_data(
    df: pd.DataFrame,
    id_vars: list
) -> pd.DataFrame:

    temp_df = df.copy()

    return pd.melt(
        temp_df,
        id_vars=id_vars
    )


# ==========================================================
# Автоопределение колонок
# ==========================================================

def get_numeric_columns(
    df: pd.DataFrame
) -> list:

    return (
        df
        .select_dtypes(
            include=np.number
        )
        .columns
        .tolist()
    )


def get_categorical_columns(
    df: pd.DataFrame
) -> list:

    return (
        df
        .select_dtypes(
            include=[
                "object",
                "category",
                "bool"
            ]
        )
        .columns
        .tolist()
    )


# ==========================================================
# Общая предобработка
# ==========================================================

def preprocess_data(
    df: pd.DataFrame
) -> pd.DataFrame:

    temp_df = df.copy()

    temp_df = df_cleaner(
        temp_df
    )

    temp_df = df_new_col(
        temp_df
    )

    if "total_cost" in temp_df.columns:

        temp_df = remove_outliers(
            temp_df,
            "total_cost"
        )

    for col in [
        "week_day",
        "month",
        "purchase_period"
    ]:

        if col in temp_df.columns:

            temp_df[col] = (
                temp_df[col]
                .astype("category")
            )

    return temp_df