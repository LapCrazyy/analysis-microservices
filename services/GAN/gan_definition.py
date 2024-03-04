import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, BatchNormalization, Dropout
# Loss function of G & D
def huber_loss(y_true, y_pred, delta=1.0):
    error = y_true - y_pred
    abs_error = tf.abs(error)
    quadratic_part = tf.minimum(abs_error, delta)
    linear_part = abs_error - quadratic_part
    return 0.5 * quadratic_part**2 + delta * linear_part

# Function for plotting loss values G & D in different epochs
def plot_losses(generator_losses, discriminator_losses):
    plt.figure(figsize=(10, 5))
    plt.plot(generator_losses, label='Generator Loss', color='blue')
    plt.plot(discriminator_losses, label='Discriminator Loss', color='orange')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('GAN Learning Curve')
    plt.legend()
    plt.grid(True)
    plt.savefig("/app/lossGAN.png")

# Generator network
def build_generator(latent_dim, output_dim):
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation='relu', input_dim=latent_dim),
        
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dense(128, activation='relu'),
        #ch this to have triangle shape in graph
        tf.keras.layers.Dense(output_dim, activation='tanh')
    ])
    return model

# Discriminator network
def build_discriminator(input_dim):
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, activation='relu', input_dim=input_dim),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    return model

# GAN model
class GAN(tf.keras.Model):
    def __init__(self, generator, discriminator, noise_dim):
        super(GAN, self).__init__()
        self.generator = generator
        self.discriminator = discriminator
        self.noise_dim = noise_dim

    def compile(self, gen_optimizer, disc_optimizer, loss_fn):
        super(GAN, self).compile()
        self.gen_optimizer = gen_optimizer
        self.disc_optimizer = disc_optimizer
        self.loss_fn = loss_fn

    def train_step(self, real_data_batch):
        batch_size = tf.cast(tf.shape(real_data_batch)[0], tf.int32)
        noise = tf.random.normal([batch_size, self.noise_dim])
        with tf.GradientTape() as tape:
            generated_data = self.generator(noise, training=True)
            real_output = self.discriminator(real_data_batch, training=True)
            fake_output = self.discriminator(generated_data, training=True)
            disc_real_loss = self.loss_fn(tf.ones_like(real_output), real_output)
            disc_fake_loss = self.loss_fn(tf.zeros_like(fake_output), fake_output)
            disc_loss = disc_real_loss + disc_fake_loss

        gradients_of_discriminator = tape.gradient(disc_loss, self.discriminator.trainable_variables)
        self.disc_optimizer.apply_gradients(zip(gradients_of_discriminator, self.discriminator.trainable_variables))
        #tf.cast(batch_size, tf.int32)
        noise = tf.random.normal([batch_size, self.noise_dim])
        with tf.GradientTape() as tape:
            generated_data = self.generator(noise, training=True)
            fake_output = self.discriminator(generated_data, training=True)
            gen_loss = self.loss_fn(tf.ones_like(fake_output), fake_output)

        gradients_of_generator = tape.gradient(gen_loss, self.generator.trainable_variables)
        self.gen_optimizer.apply_gradients(zip(gradients_of_generator, self.generator.trainable_variables))
        
        
        disc_loss_mean = tf.reduce_mean(disc_loss)
        gen_loss_mean = tf.reduce_mean(gen_loss)

        return disc_loss_mean, gen_loss_mean
