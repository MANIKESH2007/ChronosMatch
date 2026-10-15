import argparse
import statistics
import time

from chronos.matching_engine import MatchingEngine
from scripts.generate_orders import generate_orders


def run_benchmark(order_count, trials):
    # Generate orders before benchmarking.
    # This keeps order generation outside the timed section.
    orders = generate_orders(order_count)

    processing_times = []
    throughputs = []
    total_trades = 0

    for trial in range(trials):
        engine = MatchingEngine()

        start_time = time.perf_counter()

        for order in orders:
            engine.add_order(order)

        end_time = time.perf_counter()

        elapsed_time = end_time - start_time
        processing_times.append(elapsed_time)

        if elapsed_time > 0:
            throughputs.append(order_count / elapsed_time)
        else:
            throughputs.append(0.0)

        total_trades = len(engine.trades)

    median_time = statistics.median(processing_times)
    median_throughput = statistics.median(throughputs)

    print("\n===== ChronosMatch Benchmark =====")
    print(f"Orders processed per trial: {order_count}")
    print(f"Number of trials: {trials}")
    print(f"Trades executed per trial: {total_trades}")
    print(f"Median processing time: {median_time:.6f} seconds")
    print(f"Minimum processing time: {min(processing_times):.6f} seconds")
    print(f"Maximum processing time: {max(processing_times):.6f} seconds")
    print(f"Median throughput: {median_throughput:.2f} orders/second")

    if order_count > 0:
        print(
            f"Median elapsed time per order: "
            f"{median_time / order_count * 1_000_000:.2f} microseconds"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Benchmark the ChronosMatch matching engine"
    )

    parser.add_argument(
        "--orders",
        type=int,
        default=10000,
        help="Number of orders to generate and process per trial"
    )

    parser.add_argument(
        "--trials",
        type=int,
        default=5,
        help="Number of benchmark trials"
    )

    args = parser.parse_args()

    if args.orders < 0:
        parser.error("--orders must be non-negative")

    if args.trials < 1:
        parser.error("--trials must be at least 1")

    run_benchmark(args.orders, args.trials)