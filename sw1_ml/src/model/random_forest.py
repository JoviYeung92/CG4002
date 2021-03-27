import numpy as np
import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt

from sklearn.model_selection import RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, accuracy_score

# Using 3 fold cross validation
def rfc_validation(X_train, y_train):
    # Number of trees in random forest
    n_estimators = [int(x) for x in np.linspace(start = 10, stop = 100, num = 5)]
    # Number of features to consider at every split
    max_features = ['auto', 'sqrt']
    # Maximum number of levels in tree
    # max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
    # max_depth.append(None)
    # Minimum number of samples required to split a node
    min_samples_split = [2, 5, 10]
    # Minimum number of samples required at each leaf node
    min_samples_leaf = [1, 2, 4]
    # Method of selecting samples for training each tree
    bootstrap = [True, False]
    # Create the random grid
    random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               #'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap}

    classifier = RandomForestClassifier()
    # Random search of parameters, using 3 fold cross validation, 
    # search across 100 different combinations, and use all available cores
    rf_random = RandomizedSearchCV(estimator = classifier, param_distributions = random_grid, n_iter = 100, cv = 3, verbose=2, random_state=42, n_jobs = -1)
    # Fit the random search model
    rf_random.fit(X_train, y_train)
    return rf_random

def rfc(X_train, y_train, X_test, y_test, labels, n_est, mss, msl, mf, bt):
    # Fitting Random Forest Classification to the Training set
    classifier = RandomForestClassifier(n_estimators = n_est, min_samples_split=mss, min_samples_leaf=msl, max_features=mf, bootstrap= bt, criterion = 'entropy', random_state = 42)
    classifier.fit(X_train, y_train)

    y_pred = classifier.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)

    # matrix = confusion_matrix(y_test, y_pred)

    y_test = np.vectorize(labels.get)(y_test)
    y_pred = np.vectorize(labels.get)(y_pred)

    # Confusion matrix
    print('Results of Random Forest Classifier-')
    df_cm = pd.crosstab(y_test, y_pred, rownames=['Actual move'], colnames=['Predicted move'])
    print(df_cm)
    print("Accuracy:", accuracy)

    plt.figure(figsize = (12, 10))
    sn.heatmap(df_cm, annot=True)
