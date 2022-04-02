# Arxiv ontology API 

It's a simple REST API which process a batch of 5 papers from arxiv in order to return their entities. 
This web service is available direclty with the code or by the docker file 
***

### Features included 

 *  Feature 1 : get batch and return their entities in json format
      * Endpoint : /get/entities
      * Type : POST
***
## Installation 

Code has been made with Python 3.8.10
Code has been made with Ubuntu:20.04

Create a virtualenv and activate it:

```shell
python3 -m venv venv
. venv/bin/activate
```
Install Packages 

```shell
pip install -r requirements.txt
```

***
## Run 

In production 

```shell
python3 app.py
```
In developement 

```shell
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```
if flask run doesn't work make : 

```shell
python -m flask run
```

## Run with docker file 

```shell
docker build -t servicener .
```

```shell
docker run -d -p 6000:6000 servicener
```



