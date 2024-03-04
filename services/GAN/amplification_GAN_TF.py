

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
import pandas as pd
import pickle
from sklearn.preprocessing import MinMaxScaler
import logging
import sys
import downloadData
import uploadData
from minio_connect import connect
import read_join_csv as rjc
tf.get_logger().setLevel(logging.ERROR)

#load envs
asReal_perc = float(os.environ.get('as_real_percentage:', 0.1))
num_samples = int(os.environ.get('numSamples', 2000))

working_dir= "/app"
bucket_name=["model","data"]
patterns = ['GAN_Generator_Model.h5','scaler.pkl']
uploadFiles = ['generated.csv']
minio_client = connect()

if asReal_perc > 0:
    patterns.append("real.csv")
if downloadData.download_file_by_patterns(minio_client, working_dir, bucket_name[0], patterns) == False:
    sys.exit(-1)


try:
    generator = tf.keras.models.load_model("/app/GAN_Generator_Model.h5")
except:
    print("error, file: GAN_Generator_Model.h5 non found. check its existance on minio or recreate by training the gan")
    sys.exit(-1)
#load normalizer
try:
    with open("/app/scaler.pkl", 'rb') as f:
        scaler = pickle.load(f)
except:
    print("error, file: scaler.pkl not found. check its existance on minio or recreate by training gan")
    sys.exit(-1)

noise_dim = 100
# Generate random noise
noise = tf.random.normal([num_samples, noise_dim])

# Generate synthetic data using the generator
generated_data = generator.predict(noise)

# Reverse the normalization using the fitted scaler to get the original scale
generated_data = scaler.inverse_transform(generated_data)

# Create a DataFrame from the generated data
df_generated = pd.DataFrame(generated_data)

os.remove("/app/GAN_Generator_Model.h5")
os.remove("/app/scaler.pkl")

if asReal_perc > 0:    # join asReal_perc*nSamples_generated --> in real data
    realdata = rjc.readCsv("/app/real.csv")
    num_rows_to_remove = round(len(df_generated) * asReal_perc)
    #random get n rows 
    rows_as_real = df_generated.sample(n=num_rows_to_remove)
    df_generated = df_generated.drop(rows_as_real.index)
    #put as reali inside real data
    new_real = rjc.joinDf(df_generated, realdata)
    if new_real.empty:
        print(f"error merging {asReal_perc}% di generated in real, real and generated are empty collections, check file existance on minio")
        sys.exit(-1)
    new_real.to_csv("/app/real.csv",index=False)    
    df_generated.to_csv("/app/generated.csv", index=False)
    uploadFiles.append("real.csv")
else:
    df_generated.to_csv("/app/generated.csv", index=False)
    
if uploadData.upload_files_to_minio(minio_client, working_dir, bucket_name[1], uploadFiles)==False:
    sys.exit(-1)
sys.exit(0)