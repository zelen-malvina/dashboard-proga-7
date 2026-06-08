from concurrent.futures import (
    ThreadPoolExecutor
)


class ThreadManager:

    def __init__(
            self,
            max_workers=2
    ):

        self.executor = (
            ThreadPoolExecutor(
                max_workers=max_workers
            )
        )

    def run_task(
            self,
            func,
            *args,
            **kwargs
    ):
        """
        Запуск функции в отдельном потоке
        """

        future = (
            self.executor.submit(
                func,
                *args,
                **kwargs
            )
        )

        return future

    def shutdown(self):
        """
        Остановка пула потоков
        """

        self.executor.shutdown(
            wait=False
        )