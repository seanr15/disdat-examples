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

We've adapted the Tensorflow Keras example [here](https://www.tensorflow.org/datasets/keras_example).  Here we've
broken the example down into three steps in `mnist.py <pipelines/mnist.py>`_, which you will see as three classes:

* ``GetTFDS``: This downloads the mnist tfds and stores the files in a bundle named for the tfds ``mnist``

* ``Train``: This PipeTask depends on the ``GetTFDS`` tasks and trains a simple Keras NN using it.  It stores the saved model into an output bundle called ``mnist-trained``.

* ``Evaluate``: This PipeTask depends on both upstream tasks.  It restores the model, and evaluates it.  It returns a loss and accuracy in its output bundle ``mnist-evaluation``

To run all three steps, tell the Disdat CLI to execute the last step:

    $ dsdt apply pipelines.mnist.Evaluate

    [ . . . lots of output . . . ]

    ===== Luigi Execution Summary =====
    Scheduled 4 tasks of which:
    * 4 ran successfully:
        - 1 DriverTask(...)
        - 1 Evaluate(...)
        - 1 GetTFDS(...)
        - 1 Train(...)

    This progress looks :) because there were no failed tasks or missing dependencies

Now you've produced three bundles.   Use ``dsdt ls`` to see our three bundles.  You can ``cat`` each bundle to see what's inside.  There you'll find all of our output files and
values.

    $ dsdt ls m.*
    mnist-evaluation
    mnist-trained
    mnist
    $ dsdt cat mnist-evaluation
    [0.08208457 0.97430003]

### Example: Spacy

The Spacy example illustrates how you might include additional packages or data inside your Disdat container.  In this case
we have created a `MANIFEST.in` file which tells setuptools to include the data in `pipelines/en_core_web`.  

This trivial example simply shows how to use Python's built-in `pkg_resources` to get the Spacy `en_core_web` data.   You can run 
this example via  

    $dsdt apply pipelines.nlp_spacy.SimpleNLP
