# Dependency Chain (Linear Pipeline)
extract_data
     ↓
transform_data
     ↓
load_data
     ↓
generate_report
     ↓
send_email


# Dependency Explanation (Task by Task)
🔹 1. extract_data

Upstream: None

Downstream: transform_data

Reason: Raw data must be extracted first.

🔹 2. transform_data

Upstream: extract_data

Downstream: load_data

Reason: Data transformation requires extracted data.

🔹 3. load_data

Upstream: transform_data

Downstream: generate_report

Reason: Data must be loaded before reporting.

🔹 4. generate_report

Upstream: load_data

Downstream: send_email

Reason: Report is generated only after load completion.

🔹 5. send_email

Upstream: generate_report

Downstream: None

Reason: Email is sent after report generation.

# How Dependencies Are Defined in Code (VERY IMPORTANT)
🔹 Implicit Dependencies (TaskFlow API)
raw = extract_data()
transformed = transform_data(raw)
loaded = load_data(transformed)


📌 What happens internally

Airflow creates dependencies automatically

Return values are passed using XCom

Execution order is enforced

📌 Exam Line

In TaskFlow API, dependencies are inferred from function calls.

🔹 Explicit Dependencies (Bitshift Operator)
loaded >> report_task >> email_task


Equivalent to:

loaded.set_downstream(report_task)
report_task.set_downstream(email_task)


📌 Used for classic operators.

6️⃣ Dependency Type Used in This DAG
Type	Used?	Explanation
Implicit	✅ Yes	TaskFlow return-based
Explicit	✅ Yes	>> operator
Conditional	❌ No	No branching
Parallel	❌ No	Linear pipeline
7️⃣ What Happens If a Task Fails?
Failed Task	Result
extract_data	All downstream blocked
transform_data	Load, report, email skipped
load_data	Report & email skipped
generate_report	Email skipped

📌 Exam phrase

Airflow enforces fail-fast execution using dependency constraints.



# Automatic Data Passing (VERY IMPORTANT)
How data flows without XCom code:
python
Copy code
raw = extract_data()
transformed = transform_data(raw)
📌 Why this works

TaskFlow API automatically pushes return values to XCom

Next task receives data as function arguments

📌 Exam Line

TaskFlow API simplifies XCom by passing data through function returns.


# How to Run This Project
Step 1: Initialize Airflow
docker-compose up airflow-webserver airflow-scheduler

Step 2: Open UI
http://localhost:8080


Username: airflow

Password: airflow

Step 3: Trigger DAG

Enable etl_taskflow_pipeline

Click ▶ Run


Q: Why TaskFlow API?

It simplifies DAG creation and enables automatic data passing.

Q: Why docker-compose?

To orchestrate multiple Airflow services reliably.

Q: How tasks communicate?

Using XCom via function return values.

Q: Difference between PythonOperator and @task?

@task is higher-level and cleaner abstraction.




# Executor and the Schedular
Yes, both the Scheduler and Executor are used — even though we did not write code for them explicitly.
They are configured and run at the infrastructure level, not inside the DAG code.

🔹 Why You Didn’t “See” Them in the Code

In Airflow:

DAG code → defines what should run

Scheduler → decides when tasks run

Executor → decides how & where tasks run

👉 Scheduler and Executor are Airflow services, not Python functions.

🔹 Where the Scheduler Is Used (Very Important)

In your setup:

airflow-scheduler:
  command: scheduler


📌 This container IS the scheduler.

What it does internally:

Parses DAG files from dags/

Checks schedules (@daily)

Resolves dependencies

Sends tasks to the executor

📌 Exam line

The Airflow scheduler continuously monitors DAGs and triggers task instances when their conditions are met.

🔹 Where the Executor Is Used

In docker-compose.yml:

AIRFLOW__CORE__EXECUTOR: LocalExecutor


📌 This tells Airflow:

“Execute tasks using the LocalExecutor”

What LocalExecutor does:

Runs tasks in parallel

Uses local processes

Suitable for development & small production

📌 Exam line

The executor determines how tasks are executed and scaled.

🔹 Complete Flow (THIS IS GOLD FOR VIVA)
DAG Code
   ↓
Scheduler detects runnable tasks
   ↓
Executor executes the tasks
   ↓
Worker process runs Python code


📌 Key insight

DAGs do NOT execute themselves — the scheduler + executor do.

🔹 Why You Should NOT Use Scheduler/Executor in DAG Code

❌ WRONG:

scheduler = Scheduler()
executor = LocalExecutor()


📌 Reason:

Airflow is declarative

Execution is managed by Airflow services

Mixing execution logic in DAGs breaks scalability

📌 Exam phrase

Airflow separates workflow definition from execution.

🔹 Did We Use Them? (Direct Answer)
Component	Used?	Where
Scheduler	✅ Yes	airflow-scheduler service
Executor	✅ Yes	AIRFLOW__CORE__EXECUTOR
Webserver	✅ Yes	UI & monitoring
Metadata DB	✅ Yes	PostgreSQL
🔹 How to Explicitly Change Executor (Exam Tip)
Example: CeleryExecutor
AIRFLOW__CORE__EXECUTOR: CeleryExecutor


📌 Requires:

Redis / RabbitMQ

Worker containers