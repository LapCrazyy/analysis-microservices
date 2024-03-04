# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 12:55:15 2024

@author: stefa
RICORDA DI CONTARE IN UP SE Cè QUALCOSA D caricaere else raise E
da capire dove salvare il logitModel in seguito a compose
container analisi
"""

#import numpy as np
import pandas as pd
import statsmodels.api as sm
import pickle
import os
import sys
import downloadData
import uploadData
from minio_connect import connect
import read_join_csv as rjc

#ENVS
soglia = float(os.environ.get('class_margin', 28))


buckets=["data", "model"]
working_dir="/app"
download_files=["real.csv"]
upload_file="logit_model.pkl"

minio_client = connect()

if downloadData.download_file_by_patterns(minio_client, working_dir, buckets[0], download_files)==False:
    sys.exit(-1)
#fit a generic model for multivariate logistic regression.
#data must be organised idx 0 = dependent var, other later on indipendente var.

model_filename = '/app/logit_model.pkl'
data = rjc.readCsv("/app/real.csv")
if data.empty:
    sys.exit(-1)
    
X_train = data.iloc[:, 1:]
y_train = (data.iloc[:, 0] > soglia).astype(float)

# Add intercept term to X
X_train = sm.add_constant(X_train)

# Define logistic regression model
logit_model = sm.Logit(y_train, X_train)

# Train the logistic regression model
logit_result = logit_model.fit()

# Print model summary
print(logit_result.summary())
with open(model_filename, 'wb') as file:
    pickle.dump(logit_result, file)

#upload remove logit_model
if uploadData.upload_file_to_minio(minio_client,working_dir+"/"+upload_file, buckets[1], upload_file) ==False:
    sys.exit(-1)
os.remove("/app/real.csv")
sys.exit(0)