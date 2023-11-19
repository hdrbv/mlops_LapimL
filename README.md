# LAPIML: Launch API for ML models

This document describes working of API (application programming interface) for fitting machine learning models. 

![*LAPIML*](api.png)

List of models which now are available: 

1. Regression task (quality of models measured by MSE)
	- Ridge
  
2. Binary classification (ROC AUC)
	- LogisticRegression
	- CatBoostClassifier
	- DecisionTreeClassifier
  
3. Multiclass classification (F1 score)
	- RandomForestClassifier
	- CatBoostClassifier
	- DecisionTreeClassifier

Also it's possible to expand this list - send your pull request.

## Launching
For launch API just make a few steps.
In terminal:

    cd /path/to/your/dir/with/files/flaskapi.py/and/modelapi.py/from/github
    flask --app flaskapi --debug run
