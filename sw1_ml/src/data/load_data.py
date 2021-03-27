import os
import sys
import numpy as np

sys.path.insert(3, 'C:\\Users\\shrey\\Desktop\\NUS- Everything\\Semester 7\\CG4002\\CG4002_B18\\sw1_ml\\src\\feature_extraction\\')

from sklearn.preprocessing import OneHotEncoder

from features import get_features, get_position_features

def one_hot_encoder(data):
    OHE = OneHotEncoder(sparse=False)
    return OHE.fit_transform(data)

#
# TODO: Improve code by passing dictionary to only one set of functions for both dance and positions
#

def load_feature_data(full_path, dance_move, points_per_window):
    X, X_1, y = [], [], []
    result = {'hair.txt': 0, 'rocket.txt': 1, 'zigzag.txt': 2, 'window.txt': 3, 'pushback.txt': 4, 'elbow.txt': 5, 'scarecrow.txt': 6, 'shoulder.txt': 7, 'logout.txt': 8}
    with open(full_path, "r") as dance_move_file:
        for row in dance_move_file:
            val = row.split()
            val = list(map(float, val))
            X_1.append(val)
    
    # Feature extraction
    window_count = len(X_1)//points_per_window
    window_count = window_count*2 - 1
    for i in range(window_count):
        window = []
        for j in range(points_per_window):
            window.append(X_1[i*points_per_window//2 + j])
        # try:
        window = np.asarray(window, dtype=object)[:, 0:6].tolist()
        X.append(get_features(window))
        # except:
            # if len(window[0]) is not 6: 
            # continue
    y = np.full(len(X), result[dance_move])
    return X, y

def load_dance_data(path, sampling_rate, window_size):
    X, y = [], []
    count = int(sampling_rate*window_size)
    dance_moves = ['hair.txt', 'rocket.txt', 'zigzag.txt', 'elbow.txt', 'pushback.txt', 'scarecrow.txt', 'shoulder.txt', 'window.txt', 'logout.txt']
    for dance_move in os.listdir(path):
        if dance_move in dance_moves:
            print("Files read from", dance_move)
            full_path = os.path.join(path, dance_move)
            X_1, y_1 = load_feature_data(full_path, dance_move, count)
            X.extend(X_1)
            y.extend(y_1)
    X = np.asarray(X)
    y = np.asarray(y).reshape(-1, 1)
    return X, y

"""
Data load for Ensemble model
"""

def load_ensemble_data(full_path, dance_move, points_per_window):
    X, X_1, y = [], [], []
    result = {'hair.txt': 0, 'rocket.txt': 1, 'zigzag.txt': 2, 'window.txt': 3, 'pushback.txt': 4, 'elbow.txt': 5, 'scarecrow.txt': 6, 'shoulder.txt': 7, 'logout.txt': 8}
    with open(full_path, "r") as dance_move_file:
        for row in dance_move_file:
            val = row.split()
            val = list(map(float, val))
            X_1.append(val)
    
    # Feature extraction
    window_count = len(X_1)//points_per_window
    window_count = window_count*2 - 1
    for i in range(window_count):
        window = []
        for j in range(points_per_window):
            window.append(X_1[i*points_per_window//2 + j])
        # try:
        window = np.asarray(window, dtype=object)[:, 0:6].tolist()
        # X.append(get_features(window))
        print(len(window))
        X.extend(window)
        # except:
            # if len(window[0]) is not 6: 
            # continue
    # X.extend(window[39:90]) # Get 50 middle datapoints
    y = np.full(len(X), result[dance_move])
    return X, y

def load_dance_data_ensemble(path, sampling_rate, window_size):
    X, y = [], []
    count = int(sampling_rate*window_size)
    dance_moves = ['hair.txt', 'rocket.txt', 'zigzag.txt', 'elbow.txt', 'pushback.txt', 'scarecrow.txt', 'shoulder.txt', 'window.txt', 'logout.txt']
    for dance_move in os.listdir(path):
        if dance_move in dance_moves:
            print("Files read from", dance_move)
            full_path = os.path.join(path, dance_move)
            X_1, y_1 = load_ensemble_data(full_path, dance_move, count)
            X.extend(X_1)
            y.extend(y_1)
    X = np.asarray(X)
    y = np.asarray(y).reshape(-1, 1)
    return X, y

def load_feature_data_position(full_path, pos, points_per_window):
    X, X_1, y = [], [], []
    result = {'left.txt': 0, 'right.txt': 1, 'none.txt': 2}
    with open(full_path, "r") as position_file:
        for row in position_file:
            val = row.strip()
            val = float(val)
            X_1.append(val)
    
    # Feature extraction
    window_count = len(X_1)//points_per_window
    window_count = window_count*2 - 1
    for i in range(window_count):
        window = []
        for j in range(points_per_window):
            window.append(X_1[i*points_per_window//2 + j])
        #try:
        window = np.asarray(window, dtype=object).tolist()
        X.append(get_position_features(window))
        #except:
        #    # if len(window[0]) is not 6: 
        #    continue
    y = np.full(len(X), result[pos])
    return X, y

def load_position_data(path, sampling_rate, window_size):
    X, y = [], []
    count = int(sampling_rate*window_size)
    position = ['left.txt', 'right.txt', 'none.txt']
    for pos in os.listdir(path):
        if pos in position:
            print("Files read from", pos)
            full_path = os.path.join(path, pos)
            X_1, y_1 = load_feature_data_position(full_path, pos, count)
            X.extend(X_1)
            y.extend(y_1)
    X = np.asarray(X)
    y = np.asarray(y).reshape(-1, 1)
    return X, y

def load_feature_data_position_w11(full_path, pos, points_per_window):
    X, X_1, y = [], [], []
    result = {'left.txt': 0, 'right.txt': 1, 'none.txt': 2}
    with open(full_path, "r") as position_file:
        for row in position_file:
            val = row.split()
            val = list(map(float, val))
            X_1.append(val)
    
    # Feature extraction
    window_count = len(X_1)//points_per_window
    window_count = window_count*2 - 1
    for i in range(window_count):
        window = []
        for j in range(points_per_window):
            window.append(X_1[i*points_per_window//2 + j])
        #try:
        window = np.asarray(window, dtype=object)[:, 0:6].tolist()
        X.append(get_features(window))
        #except:
        #    # if len(window[0]) is not 6: 
        #    continue
    y = np.full(len(X), result[pos])
    return X, y

def load_position_data_w11(path, sampling_rate, window_size):
    X, y = [], []
    count = int(sampling_rate*window_size)
    position = ['left.txt', 'right.txt', 'none.txt']
    for pos in os.listdir(path):
        if pos in position:
            print("Files read from", pos)
            full_path = os.path.join(path, pos)
            X_1, y_1 = load_feature_data_position_w11(full_path, pos, count)
            X.extend(X_1)
            y.extend(y_1)
    X = np.asarray(X)
    y = np.asarray(y).reshape(-1, 1)
    return X, y
