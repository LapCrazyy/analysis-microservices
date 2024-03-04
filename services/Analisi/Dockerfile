FROM python:3.10.13

WORKDIR /app
COPY . /app
#COPY ../downloadData.py /app
#COPY ../uploadData.py /app
#COPY ../minio_connect.py /app
#COPY ../read_join_csv.py /app

RUN pip install tensorflow==2.15.0
RUN pip install scikit-learn
RUN pip install pandas
RUN pip install statsmodels
RUN pip install matplotlib
RUN pip install boto3

ENV type="all"
ENV class_margin=27
ENV numEpochs=100
ENV MINIO_ROOT_USER ste
ENV MINIO_ROOT_PASSWORD steflois 
ENV MINIO_SERVER_ADDRESS http://minio:9000

