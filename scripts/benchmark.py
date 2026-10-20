import argparse
import statistics
import time

from chronos.matching_engine import MatchingEngine
from scripts.generate_orders import generate_orders

def run_benchmark(order_count, trials):
    if not isinstance(order_count, int) or isinstance(order_count, bool):
        raise ValueError("order_count must be an integer")


    if order_count < 0:
        raise ValueError("order_count must be non-negative")

    if not isinstance(trials, int) or isinstance(trials, bool):
        raise ValueError("trials must be an integer")

    if trials < 1:
        raise ValueError("trials must be at least 1")

    processing_times = []
    throughputs = []
    trade_counts = []

    for trial in range(trials):
        # Generate fresh order objects for every trial.
        # Keep generation outside the timed section.
        orders = generate_orders(order_count, seed=42)

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

        trade_counts.append(len(engine.trades))

    if len(set(trade_counts)) != 1:
        raise RuntimeError("Trade counts differed between benchmark trials")

    median_time = statistics.median(processing_times)
    median_throughput = statistics.median(throughputs)

    print("\n===== ChronosMatch Benchmark =====")
    print(f"Orders processed per trial: {order_count}")
    print(f"Number of trials: {trials}")
    print(f"Trades executed per trial: {trade_counts[0]}")
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

