import time
class PerformanceMetrics:
    def __init__(self):
        self.total_orders = 0
        self.total_trades = 0
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.perf_counter()

    def stop(self):
        self.end_time = time.perf_counter()

    def record_order(self):
        self.total_orders += 1

    def record_trade(self):
        self.total_trades += 1

    def get_total_time(self):
        if self.start_time is None or self.end_time is None:
            return 0.0

        return self.end_time - self.start_time

    def get_throughput(self):
        total_time = self.get_total_time()

        if total_time <= 0:
            return 0.0

        return self.total_orders / total_time

    def get_average_latency(self):
        if self.total_orders == 0:
            return 0.0

        return self.get_total_time() / self.total_orders
