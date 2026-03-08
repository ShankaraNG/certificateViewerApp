# Certificate Viewer App

A Flask-based web application that reads a backend system list, makes live calls to each URL, and fetches SSL certificate details helping you monitor certificate health at a glance.

---

# Overview

The Certificate Viewer Tool connects to a list of backend systems and performs live SSL certificate lookups. It then categorizes each certificate into color-coded bins based on expiry date:

- 🔴 **Red** — Certificate expired or expiring very soon
- 🟡 **Yellow** — Certificate expiring in the near future
- 🟢 **Green** — Certificate is valid and has sufficient time remaining

This makes it easy to quickly identify systems that need urgent attention before certificates expire.

---

# Features

- Live SSL certificate fetching directly from URLs
- Reads systems from a configurable backend list file
- Color-coded expiry bins (Red / Yellow / Green)
- Configuration-driven setup via a properties file
- Lightweight Flask web interface

---

# Tech Stack

- **Language:** Python
- **Framework:** Flask
- **Protocol:** HTTPS / SSL Socket connections

---

# Prerequisites

Before running the application, ensure the following:

- Python 3.x is installed
- All dependencies are installed (see below)
- The **backend system list file** is correctly populated
- The **configuration properties file** has the correct values
- Network access is available to all target URLs

---

# Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd certificate-viewer-tool
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the application

- Update the **backend system list file** with the URLs/hostnames you want to monitor
- Verify all values in the **configuration properties file** are correct for your environment

### 4. Run the application

```bash
python -m app.main
```

The application will start a local Flask server. Open your browser and navigate to the address shown in the terminal output (typically `http://localhost:5000`).

---


## Important Notes

- Make sure the **system configuration** is verified before running the application
- Ensure all values in the **configuration properties file** are accurate
- The tool makes **live network calls** to each URL — ensure your environment has outbound HTTPS access to the target systems

---

## Author

**Shankar N G**

For questions, issues, or more information, please contact Shankar directly.

---
