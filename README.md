# APIML: API for ML models Launching

This document describes working of API (application programming interface) for deploying & fitting machine learning models. 

<image src="api.png" alt="Описание картинки">

List of models which now are available: 

	1. Regression task (quality of models measured by MSE)
		* Ridge
	2. Binary classification (ROC AUC)
		* LogisticRegression
		* CatBoostClassifier
		* DecisionTreeClassifier
	3. Multiclass classification (F1 score)
		* RandomForestClassifier
		* CatBoostClassifier
		* DecisionTreeClassifier

Also it's possible to expand this list - send your pull request.

