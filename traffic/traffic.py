import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    model.evaluate(x_test,  y_test, verbose=2)

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    data = []
    # Walk through every directory
    for root, _, files in os.walk(data_dir):
        # Go through every file in directory
        for file in files:
            # Load image
            image = cv2.imread(os.path.join(root, file))
            # Resize image
            resized = cv2.resize(image, (IMG_WIDTH, IMG_HEIGHT))
            # Store image and label with directory name
            label = int(os.path.basename(root))
            data.append({"image": resized, "label": label})

    # Return images and corresponding labels
    images = [row["image"] for row in data]
    labels = [row["label"] for row in data]
    return images, labels


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    # Create a convolutional neural network
    model = tf.keras.models.Sequential([

        # Convolutional layer. Learn 64 filters using a 3x3 kernel
        tf.keras.layers.Conv2D(
            64, (3, 3), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
        ),

        # Max-pooling layer, using 2x2 pool size
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

        # Convolutional layer. Learn 64 filters using a 3x3 kernel
        tf.keras.layers.Conv2D(
            64, (3, 3), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
        ),

        # Max-pooling layer, using 2x2 pool size
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),

        # Flatten units
        tf.keras.layers.Flatten(),

        # Add a hidden layer with dropout
        tf.keras.layers.Dense(512, activation="relu"),
        tf.keras.layers.Dropout(0.5),

        # Add an output layer with NUM_CATEGORIES outputs
        tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax")
    ])

    model.summary()

    # Train neural network
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    # Return model
    return model


if __name__ == "__main__":
    main()


"""
Models:
1.Model from lecture: con-32-3x3, pool-2x2, flatten, dense-128, dropout-0.5
acc: 0.0588-0.0526
2.No dropout: con-32-3x3, pool-2x2, flatten, dense-128
acc: 0.8811-0.8784
3.Lower dropout: con-32-3x3, pool-2x2, flatten, dense-128, dropout-0.2
acc: 0.5164-0.6418
3.Higher dropout: con-32-3x3, pool-2x2, flatten, dense-128, dropout-0.8
acc: 0.0560-0.0499
4.Higher dense: con-32-3x3, pool-2x2, flatten, dense-512, dropout-0.5
acc: 0.8686-0.9446
5.Higher con: con-64-3x3, pool-2x2, flatten, dense-512, dropout-0.5
acc: 0.9264-0.9272
6.Higher pool: con-64-3x3, pool-4x4, flatten, dense-512, dropout-0.5
acc: 0.8727-0.9140

7.Two layers: con-64-3x3, pool-2x2, con-64-3x3, pool-2x2, flatten, dense-512, dropout-0.5
acc: 0.9614-0.9457 (training-testing)
8.Lower dropout: con-64-3x3, pool-2x2, con-64-3x3, pool-2x2, flatten, dense-512, dropout-0.25
acc:0.9517-0.9260 (training-testing)

9.Higher dense: con-64-3x3, pool-2x2, con-64-3x3, pool-2x2, flatten, dense-1024, dropout-0.5
acc:0.9086-0.9067

"""