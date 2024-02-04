import json
import os

from ast import literal_eval
from unittest import mock

import boto3
import pytest
from botocore.stub import Stubber
from moto import mock_s3

from mlops_lapiml.src.flaskapi import app


@pytest.fixture()
def flask_app():
    app.config.update({
        "TESTING": True,
    })

    yield app


@pytest.fixture()
def client(flask_app):
    with flask_app.test_client() as c:
        yield c


@pytest.fixture()
def runner(flask_app):
    return flask_app.test_cli_runner()


def test_request_get_model(client):
    response = client.get("/api/get_model")
    test_data = literal_eval(response.data.decode('utf-8').strip())

    assert response.status_code == 200
    assert type(test_data) == list and len(test_data) == 0


def test_request_get_possible_model(client):
    response = client.put(
        "/api/get_possible_model", data=json.dumps({"target": ["2"]}), content_type="application/json"
    )

    assert response.status_code == 200
    assert "Current task 'binary'" in response.text \
           and "Available models: ['LogisticRegression', 'CatBoostClassifier', 'DecisionTreeClassifier']" in response.text


def test_request_create_model_wrong(client):
    response = client.post(
        "/api/create_model", data=json.dumps({"model_name": "SuperMulticlass"}), content_type="application/json"
    )

    assert response.status_code == 200
    assert "Wrong model name" in response.text


# @pytest.fixture
# def aws_credentials():
#     """Mocked AWS Credentials for moto."""
#     os.environ["AWS_ACCESS_KEY_ID"] = "testing"
#     os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
#     os.environ["AWS_SECURITY_TOKEN"] = "testing"
#     os.environ["AWS_SESSION_TOKEN"] = "testing"
#
#
# @pytest.fixture
# def s3_client(aws_credentials):
#     with mock_s3():
#         conn = boto3.client("s3", region_name="us-east-1")
#         yield conn
#
#
# @pytest.fixture
# def bucket_name():
#     return "my-test-bucket"
#
#
# @pytest.fixture
# def s3_test(s3_client, bucket_name):
#     s3_client.create_bucket(Bucket=bucket_name)
#     yield
#
#
# def test_request_create_model_success(client, s3_client, s3_test):
#     response = client.post(
#             "/api/create_model", data=json.dumps({"model_name": "multiclass"}), content_type="application/json"
#         )
#
#     assert response.status_code == 200
#     print(response.text)


# def predict():
#     return True
# # app.dependency_overrides[get_db] = override_get_db
# client = TestClient(app)
#
#
# def test_create_model(monkeypatch, empty_call) -> None:
#     monkeypatch.setattr(LogisticRegression, "create_model", value=empty_call)
#     response = client.post(
#         "/models/",
#         json={
#             "model": schemas.ModelCreate(
#                 dataframe_id=1,
#                 type="LogisticRegression",
#             ).model_dump(),
#             "hyperparams": {},
#         },
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["dataframe_id"] == 1
#     assert data["id"] == 1
#
#
def test_delete_model(client) -> None:
    model_id = 1
    response = client.delete(f"/api/delete_model/{model_id}")
    assert response.status_code == 200, response.text
    assert response.text == "ML-model with ID = 1 does not exist"
