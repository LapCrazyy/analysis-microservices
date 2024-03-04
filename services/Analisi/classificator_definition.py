import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LayerNormalization, Dropout

def plot_metric(metric, ylabel, title, filename):
    plt.figure(figsize=(10, 5))
    plt.plot(metric, label=ylabel, color='blue' if ylabel == 'Loss' else 'green')
    plt.title(title)
    plt.xlabel('Epoch')
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.savefig(filename, format="png")


def model(input_shape):
# Model definition
    model = Sequential([
        Dense(64, activation='relu', input_shape=(input_shape,)),
        LayerNormalization(),  
        Dropout(0.6),  
        Dense(32, activation='relu'),
        Dropout(0.3),  
        Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
    return model