import pandas as pd
import numpy as np


def load_csv_file(filepath: str) -> pd.DataFrame:
    """
    Загружает csv файл
    """

    try:

        df = pd.read_csv(
            filepath
        )

        return df

    except Exception as error:

        raise Exception(
            f"Ошибка загрузки файла:\n{error}"
        )


def detect_column_types(
        df: pd.DataFrame
) -> dict:
    """
    Автоматическое определение колонок
    """

    result = {
        "numeric": [],
        "categorical": [],
        "datetime": []
    }

    for column in df.columns:

        dtype = df[column].dtype

        if np.issubdtype(
                dtype,
                np.number
        ):

            result["numeric"].append(
                column
            )

        elif np.issubdtype(
                dtype,
                np.datetime64
        ):

            result["datetime"].append(
                column
            )

        else:

            result["categorical"].append(
                column
            )

    return result


def try_convert_datetime(
        df: pd.DataFrame
) -> pd.DataFrame:
    """
    Пытается найти колонку времени
    """

    new_df = df.copy()

    possible_columns = [
        "date",
        "datetime",
        "time",
        "timestamp",
        "ts"
    ]

    for col in possible_columns:

        if col in new_df.columns:

            try:

                if col == "ts":

                    new_df[col] = pd.to_datetime(
                        new_df[col],
                        unit="s"
                    )

                else:

                    new_df[col] = pd.to_datetime(
                        new_df[col]
                    )

            except Exception:
                pass

    return new_df


def get_file_info(
        df: pd.DataFrame
) -> dict:
    """
    Информация о датасете
    """

    memory = (
        df.memory_usage(
            deep=True
        )
        .sum()
        /
        1024
        /
        1024
    )

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing": int(
            df.isna()
            .sum()
            .sum()
        ),
        "memory_mb": round(
            memory,
            2
        )
    }