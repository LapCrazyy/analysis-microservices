
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import sys
import pickle
import logging
import downloadData
import uploadData
from minio_connect import connect
import read_join_csv as rjc
import classificator_definition as cd
tf.get_logger().setLevel(logging.ERROR)

#ENVS
soglia = float(os.environ.get('class_margin', 28))
nE = int(os.environ.get('numEpochs', 400))


buckets=["data", "model"]
working_dir="/app"
#scaler is optional if not present will be recalculated
download_files=["scaler.pkl","real.csv"]
upload_files=["classificator.h5","scaler.pkl","accuracy_classificator.png","loss_classificator.png"]

minio_client = connect()
if downloadData.download_file_by_patterns_from_buckets(minio_client, working_dir, buckets, download_files) == False:
    sys.exit(-1)

data = rjc.readCsv("/app/real.csv")
if data.empty:
    print("file: real.csv not found, check its existance on minio")
    sys.exit(-1)
    
#get input shape
input_shape = data.iloc[:,1:].shape[1]

scalerFinded=False
try: #Open if it was loaded
    with open("/app/scaler.pkl", 'rb') as f:
        scaler = pickle.load(f)#recicle gan file
    scalerFinded=True
#managing scaler
except:
    #create mine scaler based on real.csv, if it wasn't on minio
    scaler = MinMaxScaler(feature_range=(-1, 1))
    
#from cols 1 up to last, are X independent vars
X_train = data.iloc[:,1:]
#1st col expect dependent var y
y_train = (data.iloc[:, 0] > soglia).astype(int)

model = cd.model(input_shape)

# x normalization (-1,1)S
X_train = scaler.fit_transform(X_train)

# training
history = model.fit(X_train, y_train, epochs=nE, batch_size=7, verbose=0)

# saving modeks
model.save('/app/classificator.h5')
with open('/app/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

#sclare.pkl not present on minio put it on 
if not scalerFinded:
    with open('/app/scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    upload_files.append("scaler.pkl")


# getting metrics
loss = history.history['loss']
accuracy = history.history['accuracy']
# Plot Loss
cd.plot_metric(loss, 'Loss', 'Training Loss', "/app/loss_classificator.png")
# Plot Accuracy
cd.plot_metric(accuracy, 'Accuracy', 'Training Accuracy', "/app/accuracy_classificator.png")

#remove files in upload
if uploadData.upload_files_to_minio(minio_client, working_dir, buckets[1], upload_files) == False:
    sys.exit(-1)
os.remove("/app/real.csv")
sys.exit(0)