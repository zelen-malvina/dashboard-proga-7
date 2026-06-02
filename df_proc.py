import pandas as pd


def df_cleaner(df: pd.DataFrame) -> pd.DataFrame:
    new_df = df.copy()
    new_df.dropna()
    new_df = new_df.loc[new_df["discount"] < 1]
    new_df.loc[new_df["discount"] < 0, "discount"] = 0
    new_df = new_df.loc[new_df["qty"] != 0]

    return new_df


def df_new_col(df: pd.DataFrame) -> pd.DataFrame:
    new_df = df.copy()
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресение"]

    new_df["total_cost"] = new_df["price"] * new_df["qty"] * (1 - new_df["discount"])
    new_df["datetime"] = pd.to_datetime(new_df["ts"], unit="s")
    new_df["week_day"] = days[new_df["date"].dt.dayofweek]
    new_df["is_discounted"] = new_df["discount"] > 0

    return new_df

