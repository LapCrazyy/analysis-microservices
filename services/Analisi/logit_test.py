

import os
import pickle
import statsmodels.api as sm
import pandas as pd
import sys
import logging
import downloadData
import uploadData
from sklearn.metrics import mean_squared_error
from minio_connect import connect
import read_join_csv as rjc

#ENVS
soglia = float(os.environ.get('class_margin', 28))
analisi = os.environ.get('type', "all")
pattern=[]
if analisi=="logit": #logic for keeping result just of this pipeline in data
    pattern=["classificator_result_mse_i"]

#MINIO BUCKETS AND FILES
buckets=["data", "model"]
working_dir="/app"
#scaler is optional if not present will be recalculated
download_files=["logit_model.pkl","real.csv","generated.csv"]
#da fare uploadfiles have to
upload_file="logit_result_mse_i"


minio_client = connect()
if downloadData.download_file_by_patterns_from_buckets(minio_client, working_dir, buckets, download_files)== False:
    sys.exit(-1)

csvFake = rjc.readCsv("/app/generated.csv")
csvReal = rjc.readCsv("/app/real.csv")
X_train = rjc.joinDf(csvFake,csvReal)

if X_train.empty:
    print("error csvReal, csvFake, are both empty, check its existance on minio")
    sys.exit(-1)
    
print("per il calcolo del mean squared error, è necessitata la conoscenza di Y, questa viene cercata all'indice di colonna 0\nse nei dati non è presente, sostituire la collana 0 con valori numerici binari\n rappresentanti la variabile dipendete")

#read model
try:
    with open('/app/logit_model.pkl', 'rb') as f:
        logit = pickle.load(f)
except:
    print("il modello logit_model.pkl non è stato trovato nel fs locale, l'analisi non pùò essere effettuata")
    sys.exit(-1)

mse="" #mean squared error
try:    #expect prediction so only X inputs
    X_train_with_intercept = sm.add_constant(X_train)
    logit_predictions = logit.predict(X_train_with_intercept)
    binary_predictions_l = (logit_predictions > 0.5).astype(int)
except: #finds Y in col[0], X col[1:], find mse
    correct_predictions = (X_train.iloc[:, 0] > soglia).astype(int)
    X_train = X_train.iloc[:, 1:]
    X_train_with_intercept = sm.add_constant(X_train)
    logit_predictions = logit.predict(X_train_with_intercept)
    binary_predictions_l = (logit_predictions > 0.5).astype(int)
    mse = mean_squared_error(correct_predictions, binary_predictions_l)
logitdf = X_train.copy()
logitdf["predictions"] = binary_predictions_l
upload_file = f"logit_result_mse_i{mse}.csv"
logitdf.to_csv(f"/app/{upload_file}")

#remove uploaded data
if uploadData.upload_file_to_minio(minio_client,working_dir+"/"+upload_file, buckets[1], upload_file)==False:
    sys.exit(-1)
#remove other past analysis results if needed
if uploadData.remove_objects_from_minio(minio_client,buckets[0], pattern) == False:
    sys.exit(-1)
# delete datas of the analysis
if os.path.exists("/app/reali.csv"):
    os.remove("/app/reali.csv")
if os.path.exists("/app/generated.csv"):
    os.remove("/app/generated.csv")

sys.exit(0)