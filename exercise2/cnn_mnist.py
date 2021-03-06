from __future__ import print_function

import argparse
import gzip
import json
import os
import pickle

import numpy as np
import tensorflow as tf

from cnntf import CnnTensorflow 

tf.logging.set_verbosity(tf.logging.INFO)

def one_hot(labels):
    """this creates a one hot encoding from a flat vector:
    i.e. given y = [0,2,1]
     it creates y_one_hot = [[1,0,0], [0,0,1], [0,1,0]]
    """
    classes = np.unique(labels)
    n_classes = classes.size
    one_hot_labels = np.zeros(labels.shape + (n_classes,))
    for c in classes:
        one_hot_labels[labels == c, c] = 1
    return one_hot_labels


def mnist(datasets_dir='./data'):
    if not os.path.exists(datasets_dir):
        os.mkdir(datasets_dir)
    data_file = os.path.join(datasets_dir, 'mnist.pkl.gz')
    if not os.path.exists(data_file):
        print('... downloading MNIST from the web')
        try:
            import urllib
            urllib.urlretrieve('http://google.com')
        except AttributeError:
            import urllib.request as urllib
        url = 'http://www.iro.umontreal.ca/~lisa/deep/data/mnist/mnist.pkl.gz'
        urllib.urlretrieve(url, data_file)

    print('... loading data')
    # Load the dataset
    f = gzip.open(data_file, 'rb')
    try:
        train_set, valid_set, test_set = pickle.load(f, encoding="latin1")
    except TypeError:
        train_set, valid_set, test_set = pickle.load(f)
    f.close()

    test_x, test_y = test_set
    test_x = test_x.astype('float32')
    test_x = test_x.astype('float32').reshape(test_x.shape[0], 28, 28, 1)
    test_y = test_y.astype('int32')
    valid_x, valid_y = valid_set
    valid_x = valid_x.astype('float32')
    valid_x = valid_x.astype('float32').reshape(valid_x.shape[0], 28, 28, 1)
    valid_y = valid_y.astype('int32')
    train_x, train_y = train_set
    train_x = train_x.astype('float32').reshape(train_x.shape[0], 28, 28, 1)
    train_y = train_y.astype('int32')
    print('... done loading data')

    return train_x, one_hot(train_y), valid_x, one_hot(valid_y), test_x, one_hot(test_y)


def main(unused_argv):
  # Load training and eval data
  mnist = tf.contrib.learn.datasets.load_dataset("mnist")
  train_data = mnist.train.images  # Returns np.array
  train_labels = np.asarray(mnist.train.labels, dtype=np.int32)
  eval_data = mnist.test.images  # Returns np.array
  eval_labels = np.asarray(mnist.test.labels, dtype=np.int32)

  ##parser = argparse.ArgumentParser()
  ##parser.add_argument("--output_path", default="./", type=str, nargs="?",
  ##                  help="Path where the results will be stored")
  ##parser.add_argument("--input_path", default="./", type=str, nargs="?",
  ##                  help="Path where the data is located. If the data is not available it will be downloaded first")
  ##parser.add_argument("--learning_rate", default=1e-3, type=float, nargs="?", help="Learning rate for SGD")
  ##parser.add_argument("--num_filters", default=32, type=int, nargs="?",
  ##                  help="The number of filters for each convolution layer")
  ##parser.add_argument("--batch_size", default=128, type=int, nargs="?", help="Batch size for SGD")
  ##parser.add_argument("--epochs", default=12, type=int, nargs="?",
  ##                  help="Determines how many epochs the network will be trained")
  ##parser.add_argument("--run_id", default=0, type=int, nargs="?",
  ##                  help="Helps to identify different runs of an experiments")
  ##parser.add_argument("--filter_size", default=3, type=int, nargs="?",
  ##                  help="Filter width and height")
  ##args = parser.parse_args()

  # hyperparameters
  ##lr = args.learning_rate
  ##num_filters = args.num_filters
  ##batch_size = args.batch_size
  ##epochs = args.epochs
  ##filter_size = args.filter_size

   # train and test convolutional neural network
  ##train_data, train_labels, valid_data, valid_labels, test_data, test_labels = mnist(args.input_path)

  ##train_labels = np.asarray(train_labels, dtype=np.int32)
  ##valid_labels = np.asarray(valid_labels, dtype=np.int32)
  ##test_labels = np.asarray(test_labels, dtype=np.int32)
  
  # Create the Estimator
  ##mnist_classifier = tf.estimator.Estimator(
  ##    model_fn=cnn_model_fn, model_dir="./models")
  mnist_classifier = tf.estimator.Estimator(model_fn=CnnTensorflow.model, model_dir="./models")

  # Set up logging for predictions
  # Log the values in the "Softmax" tensor with label "probabilities"
  tensors_to_log = {"probabilities": "softmax_tensor"}
  logging_hook = tf.train.LoggingTensorHook(
      tensors=tensors_to_log, every_n_iter=50)

  # Train the model
  train_input_fn = tf.estimator.inputs.numpy_input_fn(
      x={"x": train_data},
      y=train_labels,
      batch_size=128,
      num_epochs=12,
      shuffle=False)
  mnist_classifier.train(input_fn=train_input_fn, steps=2000, hooks=[logging_hook])

  # Evaluate/Test the model and print results
  eval_input_fn = tf.estimator.inputs.numpy_input_fn(
      x={"x": eval_data},
      y=eval_labels,
      num_epochs=12,
      shuffle=True)
  eval_results = mnist_classifier.evaluate(input_fn=eval_input_fn)
  print(eval_results)

if __name__ == "__main__":
  tf.app.run()

