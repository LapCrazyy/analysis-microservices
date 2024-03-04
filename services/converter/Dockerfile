# Use a base Python image
FROM python:3.10.13
WORKDIR /app

COPY . /app
#COPY ../downloadData.py /app
#COPY ../uploadData.py /app
#COPY ../minio_connect.py /app


RUN pip install pandas
RUN pip install openpyxl
RUN pip install boto3

ENV MINIO_ROOT_USER ste
ENV MINIO_ROOT_PASSWORD steflois
ENV MINIO_SERVER_ADDRESS http://minio:9000
ENV nHoursBeforeSleep 12