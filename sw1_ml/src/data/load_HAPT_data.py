import csv
import numpy as np

def load_data(dataset_path):
    features_train = []
    labels_train = []
    
    features_test = []
    labels_test = []
    
    with open(dataset_path + 'Train\\X_train.txt') as fh:
        for line in fh:
            # Each line is a feature vector of size 561
            features_train.append(line.split())
    
    with open(dataset_path + 'Train\\y_train.txt') as fh:
        for line in fh:
            labels_train.append(int(line))
    
    features_train = np.asarray(features_train).astype(np.float32)
    labels_train = np.asarray(labels_train).astype(np.float32)
    
    with open(dataset_path + 'Test\\X_test.txt') as fh:
        for line in fh:
            # Each line is a feature vector of size 561
            features_test.append(line.split())
    
    with open(dataset_path + 'Test\\y_test.txt') as fh:
        for line in fh:
            labels_test.append(int(line))
    
    features_test = np.asarray(features_test).astype(np.float32)
    labels_test = np.asarray(labels_test).astype(np.float32)

    return features_train, labels_train, features_test, labels_test
    