FROM spark:3.5.8-python3

USER root
WORKDIR /opt/hospital-pipeline

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY jobs ./jobs

ENV PYTHONPATH=/opt/hospital-pipeline

CMD ["/opt/spark/bin/spark-submit", "--master", "spark://spark:7077", "/opt/hospital-pipeline/jobs/radiology_pipeline.py"]
