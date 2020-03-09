# disdat-examples
## Installation and Notebook examples
1. Install dependencies
```commandline
pip install -e .
```
2. Initialize disdat
```commandline
dsdt init
```
3. Start Jupyter Notebooks
```commandline
jupyter notebook
```

4. Open example notebooks

## Running from the CLI and dockerization 
1. Run simple example pipeline from the command line and create an output bundle `return_targets`
```commandline
cd disdat-examples
dsdt apply pipelines.return_targets.ReturnTargets
dsdt ls -v return_targets
NAME                	PROC_NAME           	OWNER   	DATE              	COMMITTED	UUID                                    	TAGS
return_targets      	ReturnTargets____ca7a191361	kyocum  	06-04-19 20:13:34 	False   	bef67232-86b6-4847-a2db-bf55eadc674b
```
2. Now dockerize the pipeline (assuming you remain in the repo's top-level directory and Docker is installed on your system).
```commandline
dsdt dockerize .
```
3. Now run the dockerized version of the pipeline.
```
dsdt run -f . pipelines.return_targets.ReturnTargets
dsdt ls -v return_targets
NAME                	PROC_NAME           	OWNER   	DATE              	COMMITTED	UUID                                    	TAGS
return_targets      	ReturnTargets____ca7a191361	root    	06-04-19 20:17:26 	False   	96abb085-bbdd-48b6-917d-d51d2c8ac744
return_targets      	ReturnTargets____ca7a191361	kyocum  	06-04-19 20:13:34 	False   	bef67232-86b6-4847-a2db-bf55eadc674b
```

Notice that the run command required us to specify the directory of the setup.py (like `dsdt dockerize`) and we added `-f` to force the entire pipeline to re-run.    

# Additional MNIST / Spacy Examples

The ``pipelines`` directory also contains the `mnist.py` and `nlp_spacy.py` pipelines.  

Unlike the above examples, we will run the MNIST and Spacy examples using the CLI. 

## Setup

Here we create a ``example-context`` data context (the same used in the above examples) into which we'll place our data.

    $ dsdt context example-context
    $ dsdt switch example-context

### Example: MNIST

We've shamelessly adapted the Tensorflow example [here](https://www.tensorflow.org/get_started/mnist/pros).  Here we've
broken the example down into three steps in `mnist.py <pipelines/mnist.py>`_, which you will see as three classes:

* ``GetDataGz``: This downloads four gzip files and stores them in a bundle called ``MNIST.data.gz``

* ``Train``: This PipeTask depends on the ``GetDataGz`` tasks, gets the gzip files, builds a Tensorflow graph and trains it.  It stores the saved model into an output bundle called ``MNIST.trained``.

* ``Evaluate``: This PipeTask depends on both upstream tasks.  It rebuilds the graph, restores the values, and evaluates the model.  It returns a single accuracy float in it's output bundle ``MNIST.eval``

To run all three steps, tell the Disdat CLI to execute the last step:

    $ dsdt apply pipelines.mnist.Evaluate
    Successfully downloaded train-images-idx3-ubyte.gz 9912422 bytes.
    Successfully downloaded train-labels-idx1-ubyte.gz 28881 bytes.
    Successfully downloaded t10k-images-idx3-ubyte.gz 1648877 bytes.
    Successfully downloaded t10k-labels-idx1-ubyte.gz 4542 bytes.
    Beginning training . . .
    Extracting file:///Users/kyocum/.disdat/context/examples/objects/fcc264dc-d21b-41f3-81e2-8ee60a527f53/train-images-idx3-ubyte.gz
    Extracting file:///Users/kyocum/.disdat/context/examples/objects/fcc264dc-d21b-41f3-81e2-8ee60a527f53/train-labels-idx1-ubyte.gz
    Extracting file:///Users/kyocum/.disdat/context/examples/objects/fcc264dc-d21b-41f3-81e2-8ee60a527f53/t10k-images-idx3-ubyte.gz
    Extracting file:///Users/kyocum/.disdat/context/examples/objects/fcc264dc-d21b-41f3-81e2-8ee60a527f53/t10k-labels-idx1-ubyte.gz
    2018-01-23 01:15:50.939566: I tensorflow/core/platform/cpu_feature_guard.cc:137] Your CPU supports instructions that this TensorFlow binary was not compiled to use: SSE4.2 AVX AVX2 FMA
    End training.
    Begin evaluation . . .
    Extracting file:///Users/kyocum/.disdat/context/examples/objects/fcc264dc-d21b-41f3-81e2-8ee60a527f53/train-images-idx3-ubyte.gz
    Extracting file:///Users/kyocum/.disdat/context/examples/objects/fcc264dc-d21b-41f3-81e2-8ee60a527f53/train-labels-idx1-ubyte.gz
    Extracting file:///Users/kyocum/.disdat/context/examples/objects/fcc264dc-d21b-41f3-81e2-8ee60a527f53/t10k-images-idx3-ubyte.gz
    Extracting file:///Users/kyocum/.disdat/context/examples/objects/fcc264dc-d21b-41f3-81e2-8ee60a527f53/t10k-labels-idx1-ubyte.gz
    0.9187
    End evaluation.

Now you've produced three bundles.   By default ``dsdt ls`` only shows the final bundle, but we can use ``-i`` to list
intermediate bundles as well.   You can ``cat`` each bundle to see what's inside.  There you'll find all of our output files and
values.

    $ dsdt ls -i
    MNIST.eval
    MNIST.data.gz
    MNIST.trained
    $ dsdt cat MNIST.eval
    0.9187

### Example: Spacy

The Spacy example illustrates how you might include additional packages or data inside your Disdat container.  In this case
we have created a `MANIFEST.in` file which tells setuptools to include the data in `pipelines/en_core_web`.  

This trivial example simply shows how to use Python's built-in `pkg_resources` to get the Spacy `en_core_web` data.   You can run 
this example via  

    $dsdt apply pipelines.nlp_spacy.SimpleNLP
