# dataPostproc_DNS
The post-process code to handle the DNS data.
# Installation
The first thing you should install is the Anaconda and configure the Python virtual environment.Then， you can install the `setup.py`  directly
```
sudo python setup.py install 
```

# Usage
The easiest way to get the usage is try to use -h option of the script.

```
dataPostproc  
The options of dataPostproc   
-h|--help: Help.  
-o|--output: The output of dataPostproc script.  
-f|--filename: You can use a list to select a file list include your data.  
-n|--normalize: Open normalization.  
-t|--tke : Calculate the TKE.  
-d|--direction: The direction of the postprocess.  
-v|--variables: The variables list to output.  
-x|--blockx :Select hyberslab of in x-direction.  
-y|--blocky :Select hyberslab of in y-direction.  
-z|--blockz :Select hyberslab of in z-direction.  
The combination of the options.  
If you want to generate a new file: you can use -o -f -v  
```
