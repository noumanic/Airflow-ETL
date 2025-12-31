from airflow.decorators import dag, task
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from datetime import datetime
import pandas as pd

# ---------------- DAG DEFINITION ----------------
@dag(
    dag_id="etl_taskflow_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["etl", "taskflow"]
)
def etl_pipeline():

    # ---------------- EXTRACT ----------------
    @task
    def extract_data():
        data = {
            "name": ["A", "B", "C"],
            "score": [80, 90, 70]
        }
        return pd.DataFrame(data).to_dict()

    # ---------------- TRANSFORM ----------------
    @task
    def transform_data(raw_data: dict):
        df = pd.DataFrame(raw_data)
        df["grade"] = df["score"].apply(lambda x: "Pass" if x >= 75 else "Fail")
        return df.to_dict()

    # ---------------- LOAD ----------------
    @task
    def load_data(clean_data: dict):
        df = pd.DataFrame(clean_data)
        print("Final Data:")
        print(df)
        return f"Loaded {len(df)} records successfully"

    # ---------------- REPORT (PythonOperator) ----------------
    def generate_report(**context):
        message = context["ti"].xcom_pull(task_ids="load_data")
        print("REPORT:", message)

    report_task = PythonOperator(
        task_id="generate_report",
        python_callable=generate_report
    )

    # ---------------- EMAIL ----------------
    email_task = EmailOperator(
        task_id="send_email",
        to="team@example.com",
        subject="ETL Pipeline Report",
        html_content="<h3>ETL Pipeline Completed Successfully</h3>"
    )

    # ---------------- DEPENDENCIES ----------------
    raw = extract_data()
    transformed = transform_data(raw)
    loaded = load_data(transformed)

    loaded >> report_task >> email_task


etl_pipeline()