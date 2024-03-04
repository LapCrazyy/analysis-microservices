import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import pickle
import logging
import sys
import gan_definition
import downloadData
import uploadData
from minio_connect import connect
import read_join_csv as rjc
tf.get_logger().setLevel(logging.ERROR)

#load envs
num_epochs = int(os.environ.get('numEpochs', 200))

working_dir="/app"
bucket_name=["data","model"]
patterns=["real.csv"]
uploadFiles = ['scaler.pkl','GAN_Generator_Model.h5','lossGAN.png']
#connect to minio
minio_client= connect()
if downloadData.download_file_by_patterns(minio_client, working_dir, bucket_name[0], patterns)==False:
    sys.exit(-1)
gene_loss = []
dis_loss = []

# Load the dataset
data = rjc.readCsv("/app/real.csv")
if data.empty:
    print("file: real.csv not found, check its existance on minio")
    sys.exit(-1)
data_array = data.values.astype(np.float32)

# Normalize the data to [-1, 1]
scaler = MinMaxScaler(feature_range=(-1, 1))
#normalize data
data_normalized = scaler.fit_transform(data_array)

input_shape = data.shape[1]
noise_dim = 100
batch_size = 9

generator = gan_definition.build_generator(noise_dim, input_shape)
discriminator = gan_definition.build_discriminator(input_shape)

# Instantiate GAN model
gan = gan_definition.GAN(generator, discriminator, noise_dim)
gan.compile(  #can parametrize with envs these too
    gen_optimizer=tf.keras.optimizers.Adam(learning_rate=0.00013, beta_1=0.5),
    disc_optimizer=tf.keras.optimizers.Adam(learning_rate=0.00013, beta_1=0.7),
    loss_fn=gan_definition.huber_loss
)
#create tf dataset
data_normalized_tf = tf.data.Dataset.from_tensor_slices(data_normalized)
data_normalized_tf = data_normalized_tf.shuffle(buffer_size=45).batch(batch_size)

# Train the GAN
for epoch in range(num_epochs):
    disc_loss_epoch = 0
    gen_loss_epoch = 0
    for real_data_batch in data_normalized_tf:
        disc_loss_batch, gen_loss_batch = gan.train_step(real_data_batch)
        disc_loss_epoch += disc_loss_batch
        gen_loss_epoch += gen_loss_batch

    disc_loss_epoch /= len(data_normalized_tf)
    gen_loss_epoch /= len(data_normalized_tf)
    dis_loss.append(disc_loss_epoch.numpy())
    gene_loss.append(gen_loss_epoch.numpy())
    if epoch % 50 == 0:
        print(f"Epoch {epoch}/{num_epochs}")

generator.save("/app/GAN_Generator_Model.h5")
with open('/app/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

#tensor->np for plotting

gene_loss = np.array(gene_loss)
dis_loss = np.array(dis_loss)
gan_definition.plot_losses(gene_loss, dis_loss)
os.remove("/app/real.csv")
if uploadData.upload_files_to_minio(minio_client, working_dir, bucket_name[1], uploadFiles) == False:
    sys.exit(-1)
sys.exit(0)
