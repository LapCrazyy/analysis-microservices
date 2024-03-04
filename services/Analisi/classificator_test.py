import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import pickle
import tensorflow as tf
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
import sys
import logging
import downloadData
import uploadData
from minio_connect import connect
import read_join_csv as rjc
tf.get_logger().setLevel(logging.ERROR)


#ENVS
soglia = float(os.environ.get('class_margin', 28))
analisi = os.environ.get('type', "all")

#MINIO BUCKETS AND FILES
buckets=["data", "model"]
working_dir="/app"
#scaler is optional if not present will be recalculated
download_files=["scaler.pkl","classificator.h5","real.csv","generated.csv"]
#da fare uploadfiles HAVE TO MAKE IT PATTERN SEARCH FS
upload_file="classificator_result_mse_i"

pattern=[]
if analisi=="classificator":
    pattern=["logit_result_mse_i"]

minio_client = connect()
if downloadData.download_file_by_patterns_from_buckets(minio_client, working_dir, buckets, download_files) == False:
    sys.exit(-1)

csvFake = rjc.readCsv("/app/generated.csv")
csvReal = rjc.readCsv("/app/real.csv")
X_train = rjc.joinDf(csvFake,csvReal)

if X_train.empty:
    print("error csvReal, csvFake, are both empty, check its existance on minio")
    sys.exit(-1)
    
#file model reading
try:
    loaded_model = tf.keras.models.load_model("/app/classificator.h5")
except:
    print("model classificator.h5 not findend in local fs, cannot execute classificator predictions")
    sys.exit(-1)
try:
    with open("/app/scaler.pkl", 'rb') as f:
            scaler = pickle.load(f)
    x_train = scaler.fit_transform(X_train)
except:
    print("model scaler.pkl not findend in local fs, cannot execute classificator predictions, without normalizer")    
    sys.exit(-1)

mse=""
try: #expect data only X to predict Y
    predictionsIA = loaded_model.predict(x_train)
    binary_predictions_ia = (predictionsIA > 0.5).astype(int)
except: #found Y in col 0, X in others  -> PREDICT AND FIND MSE
    correct_predictions = (X_train.iloc[:, 0] > soglia).astype(int)
    x_train = x_train[:, 1:]
    predictionsIA = loaded_model.predict(x_train)
    binary_predictions_ia = (predictionsIA > 0.5).astype(int)
    mse = mean_squared_error(correct_predictions, binary_predictions_ia)

iadf = X_train.copy() 
iadf["predictions"] = binary_predictions_ia
upload_file = f"classificator_result_mse_i{mse}.csv"
iadf.to_csv(f"/app/{upload_file}")


if uploadData.upload_file_to_minio(minio_client,working_dir+"/"+upload_file, buckets[1], upload_file) == False:
    sys.exit(-1)
uploadData.remove_objects_from_minio(minio_client,buckets[0], pattern)

sys.exit(0)