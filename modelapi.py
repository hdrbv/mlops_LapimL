import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
import os
from flask import abort, Response
from collections import defaultdict
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from statsmodels.discrete.discrete_model import Probit
from catboost import CatBoostClassifier, CatBoostRegressor
from sklearn.metrics import roc_auc_score, r2_score, f1_score, mean_squared_error
from typing import Tuple, Dict, Union, Any

metrics_dict = {'regression': mean_squared_error,
                'binary': roc_auc_score,
                'multiclass': f1_score}

models_dict = {'regression': [Ridge],
               'binary': [LogisticRegression, CatBoostClassifier, DecisionTreeClassifier],
               'multiclass': [RandomForestClassifier, CatBoostClassifier, DecisionTreeClassifier]}

def round_dict_values(d, k) :
    return {key: float(f"{value:.{k}f}") for key, value in d.items()}

class ML_models :
    def __init__(self) :
        self.models = []
        self.fitted_models = []
        self.counter = 0
        self.task_type = None
        self.available_models = defaultdict()
    def _get_task_type(self, data: dict, cutoff: int = 10) -> None :
        """
        Get the type of task
        data: training sample with target = target
        cutoff: threshold for regression task
        """
        target = pd.DataFrame(data)[['target']]
        if target.nunique()[0] == 2 :
            self.task_type = 'binary'
        elif target.nunique()[0] > cutoff :
            self.task_type = 'regression'
        else:
            self.task_type = 'multiclass'
    def get_available_model(self, target: dict) -> str :
        """
        Define type of task and return list of models
        """
        self._get_task_type(target)
        self.available_models[self.task_type] = {md.__name__: md for md in models_dict[self.task_type]}
        to_print = [md.__name__ for md in models_dict[self.task_type]]
        return f"Current task '{self.task_type}':\n    Available models: {to_print}"
    def create_model(self, model_name: str = '', **kwargs) -> Dict :
        """
        model_name: name of model by user
        dataset_name: name of dataset by user
        return: {'model_id', 'model_name', 'task_type' (defines automatic), 'model', 'scores'}
        """
        self.counter += 1
        ml_dic = {
            'model_id': self.counter,
            'model_name': None,
            'task_type': self.task_type,
            'model': 'Not fitted',
            'scores': {},
        }
        fitted = {
            'model_id': self.counter,
            'model': 'Not fitted',
        }
        if model_name in self.available_models[self.task_type] :
            ml_dic['model_name'] = model_name
        else :
            self.counter -= 1
            abort(Response('''Wrong model name {}{}'''.format(model_name, self.available_models[self.task_type])))
        self.models.append(ml_dic)
        self.fitted_models.append(fitted)
        return ml_dic
    def get_model(self, model_id: int) -> Dict:
        for model in self.models:
            if model['model_id'] == model_id:
                return model
        abort(Response('ML-model with ID = {} does not exist'.format(model_id)))
    def get_fitted_model(self, model_id: int) -> Dict :
        for fit_model in self.fitted_models:
            if fit_model['model_id'] == model_id:
                return fit_model
    def update_model(self, model_dict: dict) -> None :
        """
        This method update the dictionary of the model
        """
        try:
            ml_model = self.get_model(model_dict['model_id'])
            ml_model.update(model_dict)
        except KeyError:
            abort(Response('Incorrect dictionary passed.'))
        except TypeError:
            abort(Response('Dictionary should be passed.'))
    def delete_model(self, model_id: int) -> None :
        model = self.get_model(model_id)
        fitted_model = self.get_fitted_model(model_id)
        self.fitted_models.remove(fitted_model)
        self.models.remove(model)
    @staticmethod
    def _get_dataframe(data: dict) -> Tuple[DataFrame, Union[DataFrame, Any]] :
        """
        data - learning sample with a target
        """
        X = pd.DataFrame(data).drop(columns = 'target')
        target = pd.DataFrame(data)[['target']]
        return X, target
    def fit(self, model_id, data, **kwargs) -> Dict :
        X, y = self._get_dataframe(data)
        model_dict = self.get_model(model_id)
        fitted_model = self.get_fitted_model(model_id)
        if self.task_type == 'multiclass' :
            params = {'random_state': 1488, 'loss_function': 'MultiClass'}
            algo = self.available_models[self.task_type][model_dict['model_name']](**params)
        else :
            params = {'random_state': 1488}
            algo = self.available_models[self.task_type][model_dict['model_name']](**params)
        algo.fit(X, y)
        model_dict['model'] = 'Fitted'
        fitted_model['model'] = algo
        return model_dict
    def predict(self, model_id, X, to_dict: bool = True, **kwargs) -> Union[DataFrame, Any] :
        """
        model_id, X - learning sample without a target, to_json: convert predictions to json format
        """
        X = pd.DataFrame(X)
        _ = self.get_model(model_id)
        fitted_model = self.get_fitted_model(model_id)
        model = fitted_model['model']
        predict = model.predict(X)
        if to_dict:
            return pd.DataFrame(predict).to_dict()
        return predict
    def predict_proba(self, model_id, X, to_dict: bool = True, **kwargs) -> Union[DataFrame, Any] :
        X = pd.DataFrame(X)
        fitted_model = self.get_fitted_model(model_id)
        model = fitted_model['model']
        try :
            if self.task_type == 'multiclass' :
                model_scores = model.predict_proba(X)
            elif self.task_type == 'binary' :
                model_scores = model.predict_proba(X)[:, 1]
        except AttributeError:
            abort(Response(f'Models with task_type {self.task_type} has no method predict_proba'))
        if to_dict:
            return pd.DataFrame(model_scores).to_dict()
        return model_scores
    def get_scores(self, model_id, data, **kwargs) -> Dict :
        """
        model_id, data - learning sample with a target
        """
        if data is None:
            abort(Response('For compute metric you shoukd add data'))
        model_dict = self.get_model(model_id)
        X, y = self._get_dataframe(data)
        if self.task_type != 'regression':
            y_predicted = self.predict_proba(model_id, X, to_dict = False)
        else:
            y_predicted = self.predict(model_id, X, to_dict = False)
        metrics = metrics_dict[self.task_type](y, y_predicted)
        model_dict['scores'] = {metrics_dict[self.task_type].__name__: metrics}
        model_dict['scores'] = round_dict_values(model_dict['scores'], 4)
        return model_dict

