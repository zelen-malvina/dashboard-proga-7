import pandas as pd


def df_cleaner(df: pd.DataFrame) -> pd.DataFrame:  # нормализация данных
    new_df = df.copy()

    new_df = new_df.dropna()

    new_df = new_df.loc[new_df["discount"] < 1]
    new_df = new_df.loc[new_df["qty"] != 0]
    new_df = new_df.loc[new_df["price"] > 0]

    new_df.loc[new_df["discount"] < 0, "discount"] = 0

    return new_df


def df_new_col(df: pd.DataFrame) -> pd.DataFrame:
    new_df = df.copy()
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    new_df["total_cost"] = new_df["price"] * new_df["qty"] * (1 - new_df["discount"])
    new_df["datetime"] = pd.to_datetime(new_df["ts"], unit="s")
    new_df["week_day"] = new_df["datetime"].dt.dayofweek.map(lambda x: days[x])
    new_df["is_discounted"] = new_df["discount"] > 0

    return new_df


df = pd.read_csv("data.csv")
print(f"Исходное количество строк: {len(df)}")

df = df_cleaner(df)
print(f"После очистки: {len(df)} строк")

df = df_new_col(df)

df.to_csv("processed_data.csv", index=False)  # добавил index=False

print(df["datetime"].tail())
print(df.info())

# Дополнительная проверка
print(f"\nПроверка на отрицательные цены: {(df['price'] < 0).sum()}")
print(f"Проверка на отрицательную итоговую стоимость: {(df['total_cost'] < 0).sum()}")
print(f"Диапазон цен: {df['price'].min():.2f} - {df['price'].max():.2f}")