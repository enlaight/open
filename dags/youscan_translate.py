from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from airflow.operators.docker_operator import DockerOperator

# A DAG represents a workflow, a collection of tasks
with DAG(dag_id="youscan_translate", start_date=datetime(2022, 1, 1), schedule="0 3 * * *", catchup=False) as dag:

    # Tasks are represented as operators
    main = DockerOperator(
        task_id='youscan_translate',
        image='enlaight/airflow:1.0',
        api_version='auto',
        auto_remove=True,
        command="/bin/sh -c 'python3 /root/tasks/youscan_translate.py'",
        docker_url='tcp://docker-proxy:2375',
        network_mode="bridge",
        environment={
            'ENV': 'live',
        },
    )

    # Set dependencies between tasks
    main
