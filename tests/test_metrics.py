from chronos.metrics import PerformanceMetrics

def test_initial_values():
    metrics = PerformanceMetrics()

    assert metrics.total_orders == 0
    assert metrics.total_trades == 0

def test_record_order():
    metrics = PerformanceMetrics()

    metrics.record_order()
    metrics.record_order()

    assert metrics.total_orders == 2

def test_record_trade():
    metrics = PerformanceMetrics()

    metrics.record_trade()
    metrics.record_trade()
    metrics.record_trade()

    assert metrics.total_trades == 3

def test_total_time_before_measurement():
    metrics = PerformanceMetrics()

    assert metrics.get_total_time() == 0.0

def test_throughput_without_measurement():
    metrics = PerformanceMetrics()

    assert metrics.get_throughput() == 0.0

def test_average_latency_without_orders():
    metrics = PerformanceMetrics()

    assert metrics.get_average_latency() == 0.0

def test_time_measurement():
    metrics = PerformanceMetrics()

    metrics.start()
    metrics.stop()

    assert metrics.get_total_time() >= 0.0

def test_throughput_calculation():
    metrics = PerformanceMetrics()

    metrics.total_orders = 100
    metrics.start_time = 10.0
    metrics.end_time = 12.0

    assert metrics.get_throughput() == 50.0

def test_average_latency_calculation():
    metrics = PerformanceMetrics()

    metrics.total_orders = 100
    metrics.start_time = 10.0
    metrics.end_time = 12.0

    assert metrics.get_average_latency() == 0.02