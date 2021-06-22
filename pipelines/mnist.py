from __future__ import print_function
#
# Copyright 2017 Human Longevity, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from builtins import range

import keras.models
import luigi
from disdat.pipe import PipeTask
import disdat.api as api
import tensorflow as tf
import tensorflow_datasets as tfds
import os
from os import walk


"""
MNIST

This is an adaptation of https://www.tensorflow.org/datasets/keras_example

This example shows how you can save TensorFlow datasets and Keras models in bundles and then
 use them as inputs into successive tasks. 

Execution:
$python ./mnist.py
or:
$dsdt apply pipelines.mnist.Evaluate

"""

# Note: Disdat interprets local and s3 file paths inside of bundles.  Sometimes we don't want that, e.g., when
# we are saving directories.  We add a prefix when saving such paths in bundles.
NOLINK_PREFIX = "nolink://"

"""-----------------------------"""
""" TensorFlow Helper Functions """
"""-----------------------------"""

def list_files(dir:str) -> list:
    f = []
    for (dirpath, dirnames, filenames) in walk(dir):
        f.extend([os.path.join(dirpath,f) for f in filenames])
    return f


def normalize_img(image, label):
    """Normalizes images: `uint8` -> `float32`."""
    return tf.cast(image, tf.float32) / 255., label


def get_mnist_tfds(tfds_name, data_dir):
    """
    Use TFDS to extract a dataset from that stared at the data_dir.
    Args:
        tfds_name (str): Name of the tfds
        data_dir (str): The local file path where we stored the tfds

    Returns:
        (ds_info, dataset)
    """
    builder = tfds.builder(tfds_name, data_dir=data_dir)
    ds_info = builder.info
    dataset = builder.as_dataset(split=['train','test'], shuffle_files=True, as_supervised=True)
    return (ds_info, dataset)

"""-----------------------------"""
"""      Disdat Pipe Tasks      """
"""-----------------------------"""

class GetTFDS(PipeTask):
    """ Pipe Task 1
    Get the data for MNIST using TF dataset API
    This is different than the standard TFDS, which uses one place
    to store you TF datasets (typically under your home dir).   Here we
    use Disdat to place each tfds inside a bundle, and give the bundle the
    name of the dataset.  We also store the version in a tag.
    """
    name = luigi.Parameter(default="mnist")

    def pipe_requires(self):
        """ Simply name the output of this PipeTask """
        self.set_bundle_name(self.name)

    def pipe_run(self):
        """
        Simply download_and_prepare to the bundle directory directly.
        Return the list of files in the bundle so Disdat manages them.
        Returns:
            (dict): Return the directory
        """
        data_dir = self.get_output_dir()
        builder = tfds.builder(self.name, data_dir=data_dir)
        builder.download_and_prepare()
        files = list_files(data_dir)
        return {'data_dir':[NOLINK_PREFIX+data_dir], 'files': files}


class Train(PipeTask):
    """ Pipe Task 2
    Train the softmax layer.
    Returns:
        (dict): all the model files in 'save_files' and the name of the dir in 'save_dir'
    """
    name = luigi.Parameter(default='mnist')

    def pipe_requires(self):
        """ Depend on the gzip files being downloaded  """
        self.add_dependency("mnist_tfds", GetTFDS, {'name': self.name})
        self.set_bundle_name("mnist-trained")

    def pipe_run(self, mnist_tfds=None):
        """        """
        print("Beginning training . . . ")

        data_dir = mnist_tfds['data_dir'][0][len(NOLINK_PREFIX):]
        ds_info, mnist = get_mnist_tfds(self.name, data_dir)

        ds_train = mnist[0]
        ds_train = ds_train.map(normalize_img, num_parallel_calls=tf.data.experimental.AUTOTUNE)
        ds_train = ds_train.cache()
        ds_train = ds_train.shuffle(ds_info.splits['train'].num_examples)
        ds_train = ds_train.batch(128)
        ds_train = ds_train.prefetch(tf.data.experimental.AUTOTUNE)

        model = tf.keras.models.Sequential([
            tf.keras.layers.Flatten(input_shape=(28, 28)),
            tf.keras.layers.Dense(128,activation='relu'),
            tf.keras.layers.Dense(10)
        ])
        model.compile(
            optimizer=tf.keras.optimizers.Adam(0.001),
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics=[tf.keras.metrics.SparseCategoricalAccuracy()],
        )
        model.fit(
            ds_train,
            epochs=6
        )
        model_output_dir = self.create_output_dir("keras_model")
        model.save(model_output_dir)
        print("End training.")

        # Note 1: When returning a dictionary, disdat requires a sequence for each value
        # Note 2: You can return file paths or luigi.LocalTarget.
        # Returning directories results in an error.
        files = list_files(model_output_dir)
        return {'output_dir': [os.path.join(NOLINK_PREFIX+model_output_dir)],
                'files': files}


class Evaluate(PipeTask):
    """ Pipe Task 2
    Evaluate model from Train
    """
    name = luigi.Parameter(default='mnist')

    def pipe_requires(self):
        """ """
        self.add_dependency("model", Train, {'name': self.name})
        self.add_dependency("mnist_tfds", GetTFDS, {'name': self.name})
        self.set_bundle_name("mnist-evaluation")

    def pipe_run(self, model=None, mnist_tfds=None):
        """
        Args:
            model (bundle.data): Dictionary with a key for output_dir, and a set of files
            mnist_tfds (bundle.data): Dictionary with a key for output_dir, and a set of files
        """

        print ("Begin evaluation . . . ")
        data_dir = mnist_tfds['data_dir'][0][len(NOLINK_PREFIX):]
        ds_info, mnist = get_mnist_tfds(self.name, data_dir)

        ds_test = mnist[1]
        ds_test = ds_test.map(normalize_img, num_parallel_calls=tf.data.experimental.AUTOTUNE)
        ds_test = ds_test.batch(128)
        ds_test = ds_test.cache()
        ds_test = ds_test.prefetch(tf.data.experimental.AUTOTUNE)

        # Restore the model
        model_output_dir = model['output_dir'][0][len(NOLINK_PREFIX):]
        model = keras.models.load_model(model_output_dir)

        results = model.evaluate(ds_test)
        print("----->>>>> test loss, test acc:", results)
        print ("End evaluation.")

        return results


if __name__ == "__main__":
    api.apply('example-context', Evaluate)
