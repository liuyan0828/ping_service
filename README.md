# Ping Service

## 📄 Project Overview

**Ping Service** is a lightweight Python-based network monitoring tool designed to perform continuous or scheduled **Ping requests** to specific hosts or IP addresses. It helps monitor the availability, latency, and stability of network endpoints and can be used for server health checks, connectivity monitoring, and real-time alerting.

## 🚀 Features

- Perform ICMP Ping requests to target servers or IPs.
- Record ping latency and packet loss statistics.
- Support configurable target list and retry settings.
- Provide real-time command-line output.
- Support log output for historical review.
- Easy integration with automated monitoring pipelines.

---

## 🛠️ Tech Stack

| Technology | Description |
|:-:|:-|
| **Python** | Programming Language |
| **Asyncio** | Asynchronous Ping Execution |
| **Subprocess / OS utilities** | For performing ICMP ping requests |
| **Logging** | Logging results to file |

---

## 📥 Installation

1. Clone the repository:

```bash
git clone https://github.com/liuyan0828/ping_service.git
cd ping_service
```

2. Create Python environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # For Linux/Mac
venv\Scripts\activate    # For Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🚦 How to Use

### Run Default Ping

```bash
python main.py
```

### Customize Target and Count

```bash
python main.py --targets google.com,8.8.8.8 --count 5
```

### Output to log file

```bash
python main.py --log ping_results.log
```

### Available Options

| Argument      | Description                      |
|-------------|----------------------------------|
| `--targets`  | Comma-separated list of targets (default: 8.8.8.8) |
| `--count`    | Number of ping attempts per target (default: 4) |
| `--log`      | Output log file path (optional)  |

---

## 📄 Project Structure

```
ping_service/
├── main.py                  # Entry script
├── utils/                   # Helper functions
│   └── ping.py              # Ping logic
├── logs/                    # Log output directory
├── requirements.txt         # Dependencies
└── README.md                # Project Description
```

---

## ✅ Usage Scenarios

- Server / Website uptime monitoring
- Network health checks
- Daily scheduled ping tests
- Integration into CI/CD health monitoring pipelines

---

## 🔥 Future Plans

- Add email/Slack alert integration for downtime
- Add dashboard for real-time ping visualization
- Add batch scheduling support

---

Feel free to fork, contribute, or raise issues to improve this project.
