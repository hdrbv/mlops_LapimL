from flask import Flask, request, jsonify, abort, Response
from flask_restx import Api
from models.model_api import ML_models

app = Flask(__name__)
api = Api(app)
models = ML_models()


@app.route("/api/get_possible_model", methods=['GET', 'PUT'])
def get_possible_model():
    """
    Show type of task (identify with target) & possible models for learning 
    """
    return models.get_available_model(request.json)


@app.route("/api/create_model", methods=['POST'])
def create_model():
    """
    Create model (should add as parameter - model_name)
    """
    try:
        request.json['model_name']
    except KeyError:
        abort(Response("Please, check correct param 'model_name' "))
    models.create_model(**request.json)
    return 'Model creation - completed.'


@app.route("/api/get_model", methods=['GET'])
def get_all_models():
    """
    Return all models
    """
    return jsonify(models.models)


@app.route("/api/get_model/<int:model_id>", methods=['GET'])
def get_model(model_id):
    """
    Return model with a specific ID
    """
    return models.get_model(model_id)


@app.route("/api/update_model", methods=['PUT'])
def update_model():
    """
    Update specific model (should add as parameter - model_name)
    """
    models.update_model(request.json)
    return 'Model updating - completed'


@app.route("/api/delete_model/<int:model_id>", methods=['DELETE'])
def delete_model(model_id):
    """
    Delete model with specific ID
    """
    models.delete_model(model_id)
    return 'Model {} deleting - completed'.format(model_id)


@app.route("/api/fit/<int:model_id>", methods=['PUT'])
def fit(model_id):
    """
    Fit model with specific ID
    """
    models.fit(model_id, **request.json)
    return 'Model {} fitting - completed'.format(model_id)


@app.route("/api/predict/<int:model_id>", methods=['GET', 'PUT'])
def predict(model_id):
    """
    Make a prediction using a model with specific ID
    """
    preds = models.predict(model_id, **request.json)
    return preds


@app.route("/api/predict_proba/<int:model_id>", methods=['GET', 'PUT'])
def predict_proba(model_id):
    """
    Get a prediction from a model with specific ID
    """
    model_scores = models.predict_proba(model_id, **request.json)
    return model_scores


@app.route("/api/get_scores/<int:model_id>", methods=['GET', 'PUT'])
def get_scores(model_id):
    """
    Get the classification metrics from a model with specific ID 
    """
    scores = models.get_scores(model_id, **request.json)
    return scores


if __name__ == '__main__':
    app.run("0.0.0.0", 8080)
