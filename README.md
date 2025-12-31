# Airflow-ETL

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Directory Structure](#directory-structure)
- [DAG Workflow](#dag-workflow)
- [Setup Instructions](#setup-instructions)
- [Python Dependencies](#python-dependencies)
- [Understanding Dependencies](#understanding-dependencies)
- [Automatic Data Passing](#automatic-data-passing)
- [Executor and Scheduler](#executor-and-scheduler)
- [How to Run This Project](#how-to-run-this-project)
- [Frequently Asked Questions](#frequently-asked-questions)
- [Task Failure Behavior](#task-failure-behavior)
- [Author](#author)

---

## Project Overview

Airflow-ETL is a **production-ready hybrid Airflow ETL pipeline** that combines:

- **TaskFlow API tasks** for ETL (Extract → Transform → Load) with automatic data passing via XCom
- **Classic Operators** (`PythonOperator` and `EmailOperator`) for report generation and email notifications
- **Dockerized environment** for reproducibility
- **Orchestration with Docker-Compose**: Airflow Scheduler, Webserver, and PostgreSQL metadata DB

This setup is suitable for **MLOps pipelines, automated data workflows, and production-grade Airflow deployments**.

---

## Features

- ✅ ETL pipeline using TaskFlow API: `extract_data` → `transform_data` → `load_data`
- ✅ Report generation using PythonOperator
- ✅ Email notification using EmailOperator
- ✅ Hybrid task dependencies: implicit for TaskFlow tasks, explicit for operators
- ✅ Fully containerized with Docker and orchestrated using Docker-Compose
- ✅ Automatic XCom-based data passing
- ✅ Scalable and production-ready

---

## Directory Structure

```
Airflow-ETL/
│
├── dags/
│   └── etl_taskflow_dag.py    # Main DAG with ETL + Operators
├── logs/                       # Airflow logs
├── plugins/                    # Optional custom hooks/operators
├── Dockerfile                  # Custom Airflow container
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Orchestrates Airflow services
├── .env                        # Environment variables
└── README.md                   # Project documentation
```

---

## DAG Workflow

### Visual Representation

```
extract_data (@task)
      ↓
transform_data (@task)
      ↓
load_data (@task)
      ↓
generate_report (PythonOperator)
      ↓
send_email (EmailOperator)
```

### Task Descriptions

| Task | Type | Description |
|------|------|-------------|
| `extract_data` | TaskFlow API | Extracts raw data |
| `transform_data` | TaskFlow API | Cleans and transforms data |
| `load_data` | TaskFlow API | Loads transformed data |
| `generate_report` | PythonOperator | Generates report |
| `send_email` | EmailOperator | Sends completion email |

### Dependencies Explanation

- **TaskFlow API tasks** use **implicit dependencies** via function return values
- **Operators** use **explicit dependencies** using the `>>` operator
- **Hybrid DAG approach** ensures real-world functionality while maintaining clean, modern ETL structure

---

## Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/noumanic/Airflow-ETL.git
cd Airflow-ETL
```

### 2. Build Docker Image
```bash
docker-compose build
```

### 3. Start Airflow Services
```bash
docker-compose up -d
```

### 4. Access Airflow UI
Navigate to: `http://localhost:8080`

**Default Credentials:**
- **Username:** `airflow`
- **Password:** `airflow`

### 5. Trigger DAG
- Enable `etl_taskflow_pipeline` in Airflow UI
- Trigger manually or wait for scheduled execution

---

## Python Dependencies

- `pandas`
- `scikit-learn`
- `airflow` (already included in container)

Add any additional packages in `requirements.txt` as needed.

---

## Understanding Dependencies

### Dependency Chain (Task by Task)

#### 🔹 1. extract_data
- **Upstream:** None
- **Downstream:** `transform_data`
- **Reason:** Raw data must be extracted first

#### 🔹 2. transform_data
- **Upstream:** `extract_data`
- **Downstream:** `load_data`
- **Reason:** Data transformation requires extracted data

#### 🔹 3. load_data
- **Upstream:** `transform_data`
- **Downstream:** `generate_report`
- **Reason:** Data must be loaded before reporting

#### 🔹 4. generate_report
- **Upstream:** `load_data`
- **Downstream:** `send_email`
- **Reason:** Report is generated only after load completion

#### 🔹 5. send_email
- **Upstream:** `generate_report`
- **Downstream:** None
- **Reason:** Email is sent after report generation

### How Dependencies Are Defined in Code

#### Implicit Dependencies (TaskFlow API)
```python
raw = extract_data()
transformed = transform_data(raw)
loaded = load_data(transformed)
```

**What happens internally:**
- Airflow creates dependencies automatically
- Return values are passed using XCom
- Execution order is enforced

> 📌 **Exam Line:** In TaskFlow API, dependencies are inferred from function calls.

#### Explicit Dependencies (Bitshift Operator)
```python
loaded >> report_task >> email_task
```

Equivalent to:
```python
loaded.set_downstream(report_task)
report_task.set_downstream(email_task)
```

> 📌 Used for classic operators.

### Dependency Types Used in This DAG

| Type | Used? | Explanation |
|------|-------|-------------|
| Implicit | ✅ Yes | TaskFlow return-based |
| Explicit | ✅ Yes | `>>` operator |
| Conditional | ❌ No | No branching |
| Parallel | ❌ No | Linear pipeline |

---

## Automatic Data Passing

### How Data Flows Without XCom Code

```python
raw = extract_data()
transformed = transform_data(raw)
```

**Why this works:**
- TaskFlow API automatically pushes return values to XCom
- Next task receives data as function arguments

> 📌 **Exam Line:** TaskFlow API simplifies XCom by passing data through function returns.

---

## Executor and Scheduler

### Overview

Both the **Scheduler** and **Executor** are used — even though we did not write code for them explicitly. They are configured and run at the infrastructure level, not inside the DAG code.

### Why You Didn't "See" Them in the Code

In Airflow:
- **DAG code** → defines what should run
- **Scheduler** → decides when tasks run
- **Executor** → decides how & where tasks run

> 👉 Scheduler and Executor are Airflow services, not Python functions.

### Where the Scheduler Is Used

In `docker-compose.yml`:
```yaml
airflow-scheduler:
  command: scheduler
```

📌 **This container IS the scheduler.**

**What it does internally:**
- Parses DAG files from `dags/`
- Checks schedules (`@daily`)
- Resolves dependencies
- Sends tasks to the executor

> 📌 **Exam Line:** The Airflow scheduler continuously monitors DAGs and triggers task instances when their conditions are met.

### Where the Executor Is Used

In `docker-compose.yml`:
```yaml
AIRFLOW__CORE__EXECUTOR: LocalExecutor
```

📌 **This tells Airflow:** "Execute tasks using the LocalExecutor"

**What LocalExecutor does:**
- Runs tasks in parallel
- Uses local processes
- Suitable for development & small production

> 📌 **Exam Line:** The executor determines how tasks are executed and scaled.

### Complete Flow (GOLD FOR VIVA)

```
DAG Code
   ↓
Scheduler detects runnable tasks
   ↓
Executor executes the tasks
   ↓
Worker process runs Python code
```

> 📌 **Key insight:** DAGs do NOT execute themselves — the scheduler + executor do.

### Why You Should NOT Use Scheduler/Executor in DAG Code

❌ **WRONG:**
```python
scheduler = Scheduler()
executor = LocalExecutor()
```

**Reason:**
- Airflow is declarative
- Execution is managed by Airflow services
- Mixing execution logic in DAGs breaks scalability

> 📌 **Exam phrase:** Airflow separates workflow definition from execution.

### Did We Use Them?

| Component | Used? | Where |
|-----------|-------|-------|
| Scheduler | ✅ Yes | `airflow-scheduler` service |
| Executor | ✅ Yes | `AIRFLOW__CORE__EXECUTOR` |
| Webserver | ✅ Yes | UI & monitoring |
| Metadata DB | ✅ Yes | PostgreSQL |

### How to Explicitly Change Executor (Exam Tip)

**Example: CeleryExecutor**
```yaml
AIRFLOW__CORE__EXECUTOR: CeleryExecutor
```

📌 **Requires:**
- Redis / RabbitMQ
- Worker containers

---

## How to Run This Project

### Step 1: Initialize Airflow
```bash
docker-compose up airflow-webserver airflow-scheduler
```

### Step 2: Open UI
Navigate to: `http://localhost:8080`

**Credentials:**
- **Username:** `airflow`
- **Password:** `airflow`

### Step 3: Trigger DAG
- Enable `etl_taskflow_pipeline`
- Click ▶ Run

---

## Frequently Asked Questions

### Q: Why TaskFlow API?
It simplifies DAG creation and enables automatic data passing.

### Q: Why docker-compose?
To orchestrate multiple Airflow services reliably.

### Q: How tasks communicate?
Using XCom via function return values.

### Q: Difference between PythonOperator and @task?
`@task` is a higher-level and cleaner abstraction.

---

## Task Failure Behavior

### What Happens If a Task Fails?

| Failed Task | Result |
|-------------|--------|
| `extract_data` | All downstream blocked |
| `transform_data` | Load, report, email skipped |
| `load_data` | Report & email skipped |
| `generate_report` | Email skipped |

> 📌 **Exam phrase:** Airflow enforces fail-fast execution using dependency constraints.

---

## Notes

- TaskFlow API simplifies XCom usage via return values
- Hybrid DAG allows combining ETL tasks with real-world operators
- Docker + Docker-Compose ensures reproducible environment and orchestration
- Linear DAG ensures upstream tasks must succeed before downstream executes

---

## Author

**Nouman Hafeez**  
Final Year Computer Scientist @ FAST-NU  
Focused on AI, Data Science, Full-Stack Engineering

---

**Repository:** [https://github.com/noumanic/Airflow-ETL](https://github.com/noumanic/Airflow-ETL)