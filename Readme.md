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
export FLASK_RUN_PORT=5000
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```
if flask run doesn't work (In developement) make : 

```shell
python -m flask run
```
***
## Run with docker

### Installation

```shell
docker build -t servicener .
```
### Installation

```shell
docker run -d -p 5000:5000 servicener
```

## Utilization 

### Usage

Documentation is available on swagger with the url 

```shell
http://localhost:5000/apidocs/
```

Web Service is accessible by a post request with the url : 
```shell
http://localhost:5000/get/entities
```
and data schema entrypoint : 

```shell
json_data = {
            'papier_1':'https://export.arxiv.org/pdf/2203.06419v1',
            'papier_2':'https://export.arxiv.org/pdf/2203.06416v1',
            'papier_3':'https://export.arxiv.org/pdf/2203.07372v1',  
            'papier_4':'https://export.arxiv.org/pdf/2203.08878v1',
            'papier_5':'https://export.arxiv.org/pdf/2203.08958v1'
            }
```
### Exemple client request

```shell
json_data = {
            'papier_1':'https://export.arxiv.org/pdf/2203.06419v1',
            'papier_2':'https://export.arxiv.org/pdf/2203.06416v1',
            'papier_3':'https://export.arxiv.org/pdf/2203.07372v1',  
            'papier_4':'https://export.arxiv.org/pdf/2203.08878v1',
            'papier_5':'https://export.arxiv.org/pdf/2203.08958v1'
            }
            
headers = {'content-type': 'application/json'}
response = requests.post(url = "http://localhost:5000/get/entities", data =json.dumps(json_data), headers = headers)
```




