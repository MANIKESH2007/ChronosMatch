# ChronosMatch

**ChronosMatch — Zero-Copy High-Frequency Trading Engine** is a Python-based trading simulation project that demonstrates order-book management, order matching, synthetic market activity, and performance analytics through an interactive Streamlit dashboard.

> **Project status:** Educational trading simulation. The current implementation uses synthetic orders and does not connect to a live exchange.

## Features

* **Order management:** Create and validate buy and sell orders.
* **Order book:** Maintain buy orders in descending price order and sell orders in ascending price order.
* **Matching engine:** Match compatible buy and sell orders and record executed trades.
* **Partial fills:** Support orders that are only partially executed.
* **Order cancellation:** Remove resting orders from the order book.
* **Synthetic order generation:** Generate repeatable test workloads.
* **Performance benchmarking:** Measure processing time, throughput, and elapsed time per order.
* **Performance metrics:** Track trading activity and execution statistics.
* **Interactive dashboard:** Visualize market analytics, order-book depth, trade history, and summary metrics using Streamlit and Plotly.
* **Automated testing:** Validate core functionality using pytest.

## Technology Stack

* Python
* Streamlit
* Pandas
* Plotly
* pytest
* Git and GitHub

## Project Architecture

```text
ChronosMatch/
├── app.py
├── chronos/
│   ├── order.py
│   ├── order_book.py
│   ├── matching_engine.py
│   ├── ring_buffer.py
│   ├── metrics.py
│   └── dashboard_data.py
├── scripts/
│   ├── generate_orders.py
│   └── benchmark.py
├── tests/
├── data/
├── requirements.txt
└── README.md
```

### Main Components

| Component                    | Responsibility                                           |
| ---------------------------- | -------------------------------------------------------- |
| `chronos/order.py`           | Defines orders and validates their fields.               |
| `chronos/order_book.py`      | Stores, sorts, and cancels orders.                       |
| `chronos/matching_engine.py` | Matches compatible orders and records trades.            |
| `chronos/ring_buffer.py`     | Implements a fixed-capacity circular buffer.             |
| `chronos/metrics.py`         | Tracks processing time, throughput, and latency metrics. |
| `chronos/dashboard_data.py`  | Prepares simulation data for dashboard components.       |
| `scripts/generate_orders.py` | Generates synthetic orders.                              |
| `scripts/benchmark.py`       | Runs repeatable performance benchmark trials.            |
| `app.py`                     | Provides the interactive Streamlit trading dashboard.    |
| `tests/`                     | Contains automated tests for the project.                |

## How Order Matching Works

1. An order is created and validated.
2. The order book stores the order on the appropriate side.
3. Buy orders are prioritized by highest price, while sell orders are prioritized by lowest price.
4. The matching engine compares the best buy and best sell orders.
5. A trade occurs when the best buy price is greater than or equal to the best sell price.
6. The executed quantity is the smaller remaining quantity of the two orders.
7. Fully filled orders are removed; partially filled orders remain in the book.
8. The resulting trades and order-book state are displayed through the dashboard.

**Note:** The current matching engine is a simplified educational implementation. Although the order model accepts `MARKET` as an order type, full market-order execution semantics are not implemented.

## Installation

Clone the repository and enter the project directory:

```bash
git clone https://github.com/MANIKESH2007/ChronosMatch.git
cd ChronosMatch
```

Create and activate a virtual environment on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the Dashboard

Start the Streamlit application:

```powershell
streamlit run app.py
```

Streamlit will display the local dashboard address in the terminal and may open it automatically in your browser.

## Run the Tests

Execute the complete test suite:

```powershell
python -m pytest -v
```

**Latest verified test result:** 58 tests passed.

## Run the Benchmark

Run three benchmark trials, each processing 1,000 synthetic orders:

```powershell
python -m scripts.benchmark --orders 1000 --trials 3
```

### Sample Benchmark Results

The following results were recorded in a local benchmark run:

| Metric                        |                   Result |
| ----------------------------- | -----------------------: |
| Orders processed per trial    |                    1,000 |
| Number of trials              |                        3 |
| Trades executed per trial     |                      743 |
| Median processing time        |         0.009502 seconds |
| Minimum processing time       |         0.007405 seconds |
| Maximum processing time       |         0.009556 seconds |
| Median throughput             | 105,239.89 orders/second |
| Median elapsed time per order |        9.50 microseconds |

**Benchmark disclaimer:** These measurements are from a small synthetic workload on a local development machine. Execution times and throughput vary with system load, environment, and workload. They are not production performance guarantees or evidence of production-grade high-frequency trading performance.

## Current Limitations

* Uses synthetic orders rather than a live exchange feed.
* Does not yet integrate a historical market dataset.
* Implements a simplified matching engine.
* Does not implement full market-order execution semantics.
* Benchmark results are local measurements rather than production-grade performance evaluations.

## Future Improvements

* Integrate a public market-data feed.
* Add historical market-data analysis.
* Improve matching-engine performance for larger order books.
* Expand automated test coverage and edge-case validation.
* Improve benchmark reproducibility and reporting.

## Disclaimer

ChronosMatch is an educational software project. It is not connected to a live exchange and is not intended for real-money trading.
