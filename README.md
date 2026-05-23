# Smart Energy Grid Monitoring System

## Project Overview
A system to monitor and analyze energy consumption data from smart meters,
demonstrating the advantages of TimescaleDB's time-partitioning features.

## Team Members
- MUSABYIMANA Diane 101218
- UGIZWENAYO Divine 101191
- NDAHIMANA Raphael 101228

## Technology Stack
- **EMQX** - MQTT Broker
- **TimescaleDB** - Time-series database
- **Python** - Data simulation and pipeline
- **Grafana** - Dashboard and visualization
- **Docker** - Container management

## Project Structure
smart-energy-grid/
├── subscriber.py      # MQTT subscriber and data storage
├── generator.py       # Smart meter data simulator
├── fast_loader.py     # Bulk historical data loader
├── sql_scripts.sql    # All SQL scripts
└── README.md          # Project documentation

## Setup Instructions

### Prerequisites
- Docker Desktop
- Python 3.x
- pip packages: paho-mqtt, psycopg2-binary

### Step 1: Start Services
```cmd
docker start timescaledb
docker start emqx
docker start grafana
```

### Step 2: Install Python Dependencies
```cmd
pip install paho-mqtt psycopg2-binary
```

### Step 3: Run Subscriber
```cmd
python subscriber.py
```

### Step 4: Run Generator
```cmd
python generator.py
```

## Performance Results

### Baseline Query Times (1-day chunks)
| Query | Execution Time |
|-------|---------------|
| Query 1 | 107 ms |
| Query 2 | 357 ms |
| Query 3 | 4086 ms |
| Query 4 | 530 ms |

### Chunk Strategy Comparison
| Query | 3h chunks | 1-day chunks | 1-week chunks |
|-------|-----------|--------------|---------------|
| Query 1 | 267 ms | 107 ms | 60 ms |
| Query 2 | 730 ms | 357 ms | 843 ms |
| Query 3 | 6214 ms | 4086 ms | 3216 ms |
| Query 4 | 617 ms | 530 ms | 753 ms |

### Compression Results
| Table | Before | After | Ratio |
|-------|--------|-------|-------|
| 1-day chunks | 783 MB | 397 MB | 1.97x |
| 3h chunks | 794 MB | 413 MB | 1.92x |
| 1-week chunks | 782 MB | 395 MB | 1.98x |

### Continuous Aggregation Performance
| Approach | Time |
|----------|------|
| Raw data | 60.411 ms |
| Continuous aggregate | 6.374 ms |

## Dashboard
Built with Grafana featuring:
- Real-time meter readings
- Daily consumption patterns
- Weekly trends
- Monthly usage by region
- Performance metrics
- Compression analysis
- Chunk strategy comparison
