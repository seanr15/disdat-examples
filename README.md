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
dsdt apply pipelines.4_return-targets.ReturnTargets
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
dsdt run --no-push --no-pull -f . pipelines.4_return-targets.ReturnTargets
dsdt ls -v return_targets
NAME                	PROC_NAME           	OWNER   	DATE              	COMMITTED	UUID                                    	TAGS
return_targets      	ReturnTargets____ca7a191361	root    	06-04-19 20:17:26 	False   	96abb085-bbdd-48b6-917d-d51d2c8ac744
return_targets      	ReturnTargets____ca7a191361	kyocum  	06-04-19 20:13:34 	False   	bef67232-86b6-4847-a2db-bf55eadc674b
```

Notice that the run command did a few extra things.  Specifically, `no-push` prevents the pipeline from pushing bundles to the s3 remote of your local context, `no-pull` prevents the pipeline from initially synchronizing with the remote, and `-f` forces the entire pipeline to re-run.    



