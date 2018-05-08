import tensorflow as tf
import numpy as np
import scipy as sci
import config as cfg
import data_features_utility as data_utility
from tensorflow.python import debug as tf_debug

tf.logging.set_verbosity(tf.logging.INFO)


def cnn_model_fn(features, labels, mode):
    """Model function for CNN."""
    # Input Layer
    # Reshape X to 4-D tensor: [batch_size, width, height, channels]
    # MNIST images are 28x28 pixels, and have one color channel
    # input_layer = tf.reshape(features["mel"], [-1, 128, 313, 4])
    input_layer = tf.reshape(features['mel'], shape=[-1, cfg.mel_shape[0], cfg.mel_shape[1], 4])

    is_training = (mode == tf.estimator.ModeKeys.TRAIN)
    # input_layer=features['mel'].set_shape([ cfg.mel_shape[0], cfg.mel_shape[1], 4])
    # Convolutional Layer #1
    # Computes 32 features using a 5x5 filter with ReLU activation.
    # Padding is added to preserve width and height.
    # Input Tensor Shape: [batch_size, 28, 28, 1]'
    # Output Tensor Shape: [batch_size, 28, 28, 32]
    with tf.name_scope('conv1'):
        net = tf.layers.conv2d(
            inputs=input_layer,
            filters=64,
            kernel_size=[5, 5],
            padding="same",
            activation=None)
        net = tf.layers.batch_normalization(net, axis=1, training=is_training)
        net=tf.nn.relu(features=net)
        net = tf.layers.max_pooling2d(inputs=net, pool_size=2, strides=2)

    with tf.name_scope('conv2'):
        net = tf.layers.conv2d(
            inputs=net,
            filters=64,
            kernel_size=[5, 5],
            padding="same",
            activation=None)
        net = tf.layers.batch_normalization(net, axis=1, training=is_training)
        net = tf.nn.relu(features=net)
        net = tf.layers.max_pooling2d(inputs=net, pool_size=2, strides=2)

    with tf.name_scope('conv3'):
        net = tf.layers.conv2d(
            inputs=net,
            filters=64,
            kernel_size=[5, 5],
            padding="same",
            activation=None)
        net = tf.layers.batch_normalization(net, axis=1, training=is_training)
        net = tf.nn.relu(features=net)
        net = tf.layers.max_pooling2d(inputs=net, pool_size=2, strides=2)


    with tf.name_scope('conv4'):
        net = tf.layers.conv2d(
            inputs=net,
            filters=64,
            kernel_size=[5, 5],
            padding="same",
            activation=None)
        net = tf.layers.batch_normalization(net, axis=1, training=is_training)
        net = tf.nn.relu(features=net)
        net = tf.layers.max_pooling2d(inputs=net, pool_size=2, strides=2)



    with tf.name_scope('conv5'):
        net = tf.layers.conv2d(
            inputs=net,
            filters=64,
            kernel_size=[5, 5],
            padding="same",
            activation=None)
        net = tf.layers.batch_normalization(net, axis=1, training=is_training)
        net = tf.nn.relu(features=net)
        net = tf.layers.max_pooling2d(inputs=net, pool_size=2, strides=2)

    with tf.name_scope('conv6'):
        net = tf.layers.conv2d(
            inputs=net,
            filters=64,
            kernel_size=[5, 5],
            padding="same",
            activation=None)
        net = tf.layers.batch_normalization(net, axis=1, training=is_training)
        net = tf.nn.relu(features=net)
        net = tf.layers.max_pooling2d(inputs=net, pool_size=2, strides=2)






    net_flat = tf.reshape(net, [-1,2*4*64])

    # Dense Layer
    # Densely connected layer with 1024 neurons
    # Input Tensor Shape: [batch_size, 7 * 7 * 64]
    # Output Tensor Shape: [batch_size, 1024]
    dense = tf.layers.dense(inputs=net_flat, units=1024, activation=tf.nn.relu)

    # Add dropout operation; 0.6 probability that element will be kept
    dropout = tf.layers.dropout(
        inputs=dense, rate=0.4, training=mode == tf.estimator.ModeKeys.TRAIN)

    # Logits layer
    # Input Tensor Shape: [batch_size, 1024]
    # Output Tensor Shape: [batch_size, 10]
    logits = tf.layers.dense(inputs=dropout, units=9)


    predictions = {
        # Generate predictions (for PREDICT and EVAL mode)
        "classes": tf.argmax(input=logits, axis=1),

        "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
    }
    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

    # Calculate Loss (for both TRAIN and EVAL modes)
    loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)

    # Configure the Training Op (for TRAIN mode)
    if mode == tf.estimator.ModeKeys.TRAIN:
        update_op = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        with tf.control_dependencies(update_op):
            optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.001)
            train_op = optimizer.minimize(
                loss=loss,
                global_step=tf.train.get_global_step())
            accuracy = tf.metrics.accuracy(labels=labels, predictions=tf.argmax(tf.nn.softmax(logits), axis=1))
            tf.summary.scalar('train_accuracy', accuracy[1])
            return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

    # Add evaluation metrics (for EVAL mode)
    eval_metric_ops = {
        "accuracy": tf.metrics.accuracy(
            labels=labels, predictions=predictions["classes"])}
    return tf.estimator.EstimatorSpec(
        mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)


def main(unused_argv):
    classifier = tf.estimator.Estimator(
        model_fn=cnn_model_fn, model_dir="./cnn_model")

    tensors_to_log = {"probabilities": "softmax_tensor"}
    logging_hook = tf.train.LoggingTensorHook(
        tensors=tensors_to_log, every_n_iter=50)

    hook = tf_debug.TensorBoardDebugHook("sunny-workstation:7000")

    test_solution = data_utility.AudioPrepare()
    train_input_fn = test_solution.tf_input_fn_maker(is_training=True, n_epoch=100)

    classifier.train(
        input_fn=train_input_fn,
        steps=20000,
        hooks=[logging_hook])
    # classifier.train(
    #     input_fn=train_input_fn,
    #     steps=20000,
    #     hooks=[hook])


if __name__ == "__main__":
    tf.app.run()
