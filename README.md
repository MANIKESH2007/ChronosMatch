# ChronosMatch — Zero-Copy High-Frequency Trading Engine

ChronosMatch is an educational trading-system project built with Python. It demonstrates order-book management, simulated order matching, performance benchmarking, live cryptocurrency market-data monitoring, and historical market analytics through an interactive Streamlit dashboard.

The project combines three independent data systems:

1. **Simulated trading:** A local matching engine processes synthetic buy and sell orders.
2. **Live market data:** A Binance WebSocket connection receives public BTC/USDT trade information.
3. **Historical analytics:** Binance BTCUSDT aggregate-trade data from September 2026 is processed and visualized.

> **Important:** ChronosMatch receives public live market data but does not place orders on Binance or execute real-money trades. All matching-engine executions are simulated locally.

## Features

### 1. Order Management and Matching Engine

- Create and validate BUY and SELL orders.
- Support LIMIT and MARKET order-type labels.
- Maintain separate buy and sell order books.
- Prioritize buy orders by highest price and sell orders by lowest price.
- Match compatible orders.
- Support partial order fills.
- Remove completely filled orders.
- Cancel orders using their IDs.
- Prevent duplicate order IDs.

### 2. Synthetic Order Simulation

- Generate repeatable synthetic orders.
- Configure the number of orders.
- Set a random seed.
- Process generated orders through the matching engine.
- Reset the simulation.
- Visualize order-book and trade information.

### 3. Performance Benchmarking

- Measure matching-engine processing time.
- Calculate median processing time.
- Calculate minimum and maximum processing time.
- Measure order throughput.
- Calculate elapsed time per order.
- Execute multiple benchmark trials.

### 4. Live Binance Market Data

- Connect to Binance's public BTC/USDT trade WebSocket.
- Receive live trade messages.
- Extract price, quantity, timestamp and trading symbol.
- Identify aggressive buy and sell activity.
- Validate incoming messages.
- Automatically reconnect after network interruptions.
- Run the market-data worker in a background thread.
- Retain up to 500 recent trades by default.

### 5. Historical Market Analytics

- Process Binance BTCUSDT aggregate-trade data.
- Read large CSV files in chunks.
- Convert microsecond timestamps into UTC datetime.
- Calculate historical trading statistics.
- Calculate Volume Weighted Average Price (VWAP).
- Aggregate historical trades into OHLCV candles.
- Support 1-hour, 4-hour and 1-day timeframes.
- Filter historical charts by date range.

### 6. Interactive Dashboard

Built using Streamlit and Plotly.

Dashboard features include:

- Dark and light themes.
- Simulation controls.
- Order-book visualization.
- Trade history.
- Execution-price charts.
- Market-depth charts.
- Order-scatter charts.
- Historical BTC price charts.
- Historical trading-volume charts.
- Historical market KPI cards.
- Live Binance feed status.
- Live trade statistics.
- Live price and market-activity charts.
- Automatic live-panel refresh every five seconds.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application and matching engine |
| Streamlit | Interactive dashboard |
| Pandas | Historical data processing |
| Plotly | Interactive charts |
| WebSockets | Live Binance market-data connection |
| pytest | Automated testing |
| Git | Version control |
| GitHub | Source-code hosting |

## Project Architecture

```text
ChronosMatch/
|
|-- app.py
|
|-- chronos/
|   |-- __init__.py
|   |-- order.py
|   |-- order_book.py
|   |-- matching_engine.py
|   |-- ring_buffer.py
|   |-- metrics.py
|   |-- dashboard_data.py
|   |-- market_data.py
|   |-- live_market_worker.py
|   |-- live_charts_component.py
|   |-- historical_data.py
|
|-- components/
|   |-- live_charts/
|       |-- index.html
|
|-- scripts/
|   |-- __init__.py
|   |-- generate_orders.py
|   |-- benchmark.py
|   |-- test_live_market_data.py
|
|-- tests/
|   |-- test_order.py
|   |-- test_order_book.py
|   |-- test_matching_engine.py
|   |-- test_ring_buffer.py
|   |-- test_metrics.py
|   |-- test_dashboard_data.py
|   |-- test_market_data.py
|   |-- test_live_market_worker.py
|   |-- test_historical_data.py
|   |-- test_integration.py
|
|-- data/
|   |-- BTCUSDT-aggTrades-2026-09.csv
|
|-- requirements.txt
|-- .gitignore
|-- README.md
```

The historical dataset is stored locally and is not included in the Git repository.

## Main Components

| Module | Responsibility |
|---|---|
| `chronos/order.py` | Defines and validates orders |
| `chronos/order_book.py` | Stores, prioritizes and cancels orders |
| `chronos/matching_engine.py` | Matches compatible orders and records simulated trades |
| `chronos/ring_buffer.py` | Implements a fixed-capacity circular buffer |
| `chronos/metrics.py` | Provides performance metrics |
| `chronos/dashboard_data.py` | Prepares simulation data for dashboard visualization |
| `chronos/market_data.py` | Parses Binance trade messages and manages the WebSocket stream |
| `chronos/live_market_worker.py` | Receives live market data in a background thread |
| `chronos/live_charts_component.py` | Connects the dashboard to the live chart component |
| `chronos/historical_data.py` | Loads, validates and aggregates historical trade data |
| `components/live_charts/index.html` | Implements the custom live-chart interface |
| `scripts/generate_orders.py` | Generates synthetic orders |
| `scripts/benchmark.py` | Measures matching-engine performance |
| `scripts/test_live_market_data.py` | Provides a live market-data testing utility |
| `app.py` | Runs the Streamlit dashboard |

## How the Matching Engine Works

1. An order is created and validated.
2. The order is inserted into the appropriate side of the order book.
3. Buy orders are sorted from highest to lowest price.
4. Sell orders are sorted from lowest to highest price.
5. The matching engine retrieves the best available buy and sell orders.
6. A match occurs when the best buy price is greater than or equal to the best sell price.
7. The execution price is the sell order's price.
8. The executed quantity is the smaller remaining quantity of the two orders.
9. Remaining quantities are updated.
10. Completely filled orders are removed from the order book.
11. Executed trades are recorded.

**Implementation note:** The order model accepts both LIMIT and MARKET labels, but separate market-order execution rules have not been implemented. Both currently follow the same price-based matching logic.

## Understanding the Three Data Systems

| Data system | Source | Purpose |
|---|---|---|
| Synthetic orders | Local order generator | Simulated order matching |
| Live market data | Binance BTC/USDT WebSocket | Live market monitoring |
| Historical market data | Binance aggregate-trade archive | Historical market analysis |

These systems operate independently.

Live Binance trades are not automatically submitted to the simulated matching engine. Historical data is also independent of both live market activity and synthetic executions.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/MANIKESH2007/ChronosMatch.git
cd ChronosMatch
```

### 2. Create a Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Verify Dependencies

```powershell
python -m pip check
```

## Historical Dataset Setup

ChronosMatch uses the Binance public BTCUSDT aggregate-trade dataset for September 2026.

### Dataset Details

| Property | Value |
|---|---|
| Exchange | Binance |
| Trading pair | BTCUSDT |
| Data type | Aggregate trades (`aggTrades`) |
| Period | September 1–30, 2026 (UTC) |
| Total records | 26,690,426 |
| CSV filename | `BTCUSDT-aggTrades-2026-09.csv` |
| Timestamp unit | Microseconds |
| Source | Binance Public Data Archive |

Download the September 2026 BTCUSDT aggregate-trade archive from:

`https://data.binance.vision/`

Extract the CSV and place it inside the project's `data/` directory:

```text
ChronosMatch/
|
|-- data/
    |-- BTCUSDT-aggTrades-2026-09.csv
```

The application expects this exact CSV filename.

### CSV Column Definitions

The dataset contains eight columns and does not include a header row.

| Column | Field | Description |
|---|---|---|
| 1 | `agg_trade_id` | Aggregate trade ID |
| 2 | `price` | Executed trade price |
| 3 | `quantity` | Executed quantity |
| 4 | `first_trade_id` | First trade ID in the aggregate |
| 5 | `last_trade_id` | Last trade ID in the aggregate |
| 6 | `timestamp` | Execution timestamp in microseconds |
| 7 | `is_buyer_maker` | Indicates whether the buyer was the market maker |
| 8 | `is_best_match` | Indicates whether the trade was the best price match |

### Dataset Processing

The historical loader:

- Reads CSV records in chunks of 100,000 by default.
- Validates prices, quantities and timestamps.
- Converts timestamps from microseconds to UTC datetime.
- Determines the aggressor side from the buyer-maker flag.
- Calculates historical summary statistics.
- Aggregates records into OHLCV candles.

The chunk-based processing approach avoids loading the entire raw CSV into memory at once.

### Historical Statistics

The application calculates:

- Total trades.
- Minimum and maximum price.
- Total BTC quantity.
- Total USDT quote volume.
- VWAP.
- Buy quantity.
- Sell quantity.
- First and last timestamps.

### Historical Chart Timeframes

The dashboard supports:

| Timeframe | Frequency |
|---|---|
| 1 Hour | `1h` |
| 4 Hours | `4h` |
| 1 Day | `1D` |

The historical date-range selector filters the displayed candles.

The historical summary KPI cards represent the complete dataset, while the charts display the selected date range.

### Dataset Validation

The downloaded dataset was checked before integration:

- ZIP archive integrity verified.
- All 26,690,426 records scanned.
- Eight-column structure checked.
- Price, quantity, trade ID and timestamp checks performed.
- Aggregate trade IDs verified as strictly increasing.
- Timestamps verified as non-decreasing.

**Recorded validation result:** All performed checks passed.

The CSV and ZIP files are excluded from Git because of their large size.

## Run the Dashboard

After installing the dependencies and placing the historical CSV in the correct directory, execute:

```powershell
streamlit run app.py
```

Streamlit will display the local dashboard address in the terminal.

Open that address in your browser.

### Live Market Data

The live Binance feed can be started and stopped from the dashboard.

An internet connection is required to receive live market data. If Binance is unreachable, the worker attempts to reconnect automatically.

The live feed is optional. The local matching-engine simulation does not depend on the live feed.

## Run Automated Tests

Execute the complete test suite:

```powershell
python -m pytest -v
```

**Latest verified result during final project audit: 126 tests passed.**

The tests cover order validation, order-book operations, matching logic, ring-buffer behavior, metrics, dashboard data, historical data processing, live market-data parsing, worker behavior and integration.

## Run the Benchmark

The benchmark processes synthetic orders through the matching engine.

Run 1,000 orders across three trials:

```powershell
python -m scripts.benchmark --orders 1000 --trials 3
```

Run the default benchmark of 10,000 orders across five trials:

```powershell
python -m scripts.benchmark
```

### Benchmark Measurements

The benchmark reports:

- Orders processed per trial.
- Number of trials.
- Trades executed.
- Median processing time.
- Minimum processing time.
- Maximum processing time.
- Median throughput in orders per second.
- Median elapsed time per order in microseconds.

**Benchmark disclaimer:** Results depend on the local computer, workload and system conditions. These measurements are for educational performance evaluation and are not production HFT performance guarantees.

## Current Limitations

- The matching engine uses Python lists and sorting for order-book management.
- The implementation is a simplified educational simulator, not a production exchange engine.
- Separate market-order execution semantics are not implemented.
- The live feed currently supports BTCUSDT.
- Live market data is not connected to the simulated execution engine.
- Historical analytics depend on the local CSV dataset being available.
- Benchmark results are local measurements and do not establish production-grade performance.
- The project does not provide real-money trading or exchange order placement.

## Future Improvements

Possible extensions include:

- Improve order-book data structures and matching performance.
- Implement separate market-order execution rules.
- Add additional trading pairs.
- Expand historical analytics.
- Improve benchmark reporting and reproducibility.
- Add further integration and stress tests.
- Explore lower-latency and memory-efficient implementations.

## Disclaimer

ChronosMatch is an educational software project developed for learning and demonstrating trading-system concepts.

It receives public Binance market data but does not place real exchange orders, execute real-money trades or provide financial advice.

It should not be considered a production-ready high-frequency trading system.