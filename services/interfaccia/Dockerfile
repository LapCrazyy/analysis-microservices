FROM python:3.10.13
WORKDIR /app

COPY . /app
#COPY ../downloadData.py /app
#COPY ../uploadData.py /app
#COPY ../minio_connect.py /app


RUN pip install docker
RUN pip install boto3
RUN pip install python-dotenv

# Set environment variable

ENV MINIO_ROOT_USER ste
ENV MINIO_ROOT_PASSWORD steflois
ENV MINIO_SERVER_ADDRESS http://minio:9000

ENV upData=n
ENV resetData=n
ENV convert=n
ENV t_before_bed=12
ENV exclude_y=n
ENV ganT=n
ENV numEpochs_G=200
ENV augmentation=n
ENV numSamples=2000
ENV as_real_percentage=0.1
ENV classificatorTrain=n
ENV numEpochs_C=100
ENV logitTrain=n
ENV class_margin=28
ENV analyze=n


CMD ["python", "main.py"]



