import os
from sklearn.linear_model import LogisticRegression, Ridge

from src.db.db_setup import Base
from src.db import schemas
from src.api.main import app, get_db, DataFrame, LinearModel, Model

TestingSessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
Base.metadata.create_all(bind = engine)
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_create_model(monkeypatch, empty_call) -> None:
    monkeypatch.setattr(LogisticRegression, "create_model", value = empty_call)
    response = client.post(
        "/models/",
        json = {
            "model": schemas.ModelCreate(
                dataframe_id = 1,
                type = "LogisticRegression",
            ).model_dump(),
            "hyperparams": {},
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["dataframe_id"] == 1
    assert data["id"] == 1

def test_delete_model(monkeypatch, empty_call) -> None:
    monkeypatch.setattr(os, "delete_model", value = empty_call)
    model_id = 1
    response = client.delete(f"/models/{model_id}/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Model deleted"

def test_models_predict(monkeypatch) -> None:
    y_pred = [1, 0, 0, 1, 0]
    def _predict(*args, **kwargs):
        return y_pred
    monkeypatch.setattr(Model, "predict", value = predict)
    response = client.post(
        "/models/predict/",
        json={
            "mdl_info": schemas.Predict(model_id=1).model_dump(),
            "dataframe": {}
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["result"] == y_pred
