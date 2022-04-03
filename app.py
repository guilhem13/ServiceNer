import json
import flask
import multiprocessing as mp
from flasgger import Swagger, swag_from
from flask import Response,request
from waitress import serve
from knowledgegraph.models.notificationmodel import Notification
from knowledgegraph.models.datamodel import DataPaper
from knowledgegraph.controller.treatment.mainprocess import Pipeline


app = flask.Flask(__name__)
app.config["UPLOAD_FOLDER"] = "."
swagger = Swagger(app)


def main_function(block_paper):
    p = Pipeline("https://export.arxiv.org/pdf/", 0)
    out_queue = mp.Queue()
    batch_size = 5
    return p.make_traitement_pipeline(block_paper, out_queue, batch_size)


@app.route("/get/entities", methods=["GET", "POST"])
@swag_from("swagger/get_entities.yml")
def upload_file():
    """Endpoint returning list of Entities based on references part analysis
    """
    if request.method == "POST":

        try: 
            data = request.json
            block_arxiv = []
            for key, value in list(data.items()): 
                data_paper = DataPaper(value)
                print(data_paper.__dict__)
                block_arxiv.append(data_paper)
            result = main_function(block_arxiv)
            res = json.dumps([json.dumps(o.__dict__, default=lambda x: x.__dict__) for o in result])
            return res

        except Exception as e:
            return Response(
                Notification(
                    "400",
                    "error : can't process batch",
                ).message(),
                status=400,
                mimetype="application/json",
            )


############################### Error handler ########################################
# route for error 500
@app.errorhandler(500)
def internal_server_errors(error):
    return Response(
        Notification(
            "404",
            "error :/ Internal Server Error",
        ).message(),
        status=404,
        mimetype="application/json",
    )


# route for error 404
@app.errorhandler(404)
def internal_server_error(error):
    return Response(
        Notification(
            "404",
            "Sorry wrong endpoint.This endpoint doens't exist. Check your endpoint or your id arguments",
        ).message(),
        status=404,
        mimetype="application/json",
    )

##########################################################################################

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)
