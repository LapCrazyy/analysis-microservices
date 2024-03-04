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
RUN pip install numpy 
RUN pip install openpyxl 
RUN pip install matplotlib boto3

# Set environment variable
ENV MINIO_ROOT_USER ste
ENV MINIO_ROOT_PASSWORD steflois
ENV MINIO_SERVER_ADDRESS minio:9000
ENV numSamples=2000
ENV numEpochs=1000

