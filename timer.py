import matplotlib.pyplot as plt

from dataclasses import dataclass
from time import perf_counter
from typing import Dict, Callable, List


@dataclass
class TimedOperation:
    times: List[float]
    min: float
    max: float


class Timer:
    def __init__(self):
        self.times: Dict[str, TimedOperation] = {}

    def timed(self, func: Callable):
        times = self.times

        def wrapper(*args, **kwargs):
            nonlocal times

            start = perf_counter()
            retval = func(*args, **kwargs)
            dt = perf_counter() - start
            try:
                operation = times[func.__qualname__]
                operation.times.append(dt)

                if dt < operation.min:
                    operation.min = dt
                elif dt > operation.max:
                    operation.max = dt
            except KeyError:
                times[func.__qualname__] = TimedOperation([dt], dt, dt)
            return retval

        return wrapper

    def calculate(self):
        return {
            key: (sum(operation.times) / len(operation.times), operation.min, operation.max)
            for key, operation in self.times.items()
        }

    def show_graph(self):
        for name, operation in self.times.items():
            sub = operation.times[20:80]
            print(f"{name}: {sum(sub) / len(sub)}")
            plt.plot(sub)
        plt.show()

    def show(self):
        for function_name, time_data in self.calculate().items():
            mean_s, min_s, max_s = time_data
            print(f"    {function_name}: {mean_s:.7f} ({min_s:.7f} min) ({max_s:.7f} max)")
