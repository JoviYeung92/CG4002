import numpy as np
import statistics
import math
from scipy import stats
# from spectrum import aryule

def get_mean(input):
    return statistics.mean(input)

def get_min(input):
    return np.min(input)

def get_max(input):
    return np.max(input)

def get_var(input):
    return np.var(input)

def get_std(input):
    return np.std(input)

def get_MAD(input):
    return stats.median_absolute_deviation(input)

def get_l2_mag(input):
    """ Returns the magnitude of the input 3-axial values

    Args:
        input (array of coordinates): The input is a multidimensional array of shape (3, -1)

    Returns:
        mag (ndarray): Magnitude array 
    """
    input_x, input_y, input_z = input
    mag = []
    for i in range(len(input_x)):
        mag.append(math.sqrt(input_x[i]**2 + input_y[i]**2 + input_z[i]**2))
    return np.asarray(mag)

def get_sma(input):
    input_x, input_y, input_z = input
    sma = 0
    for i in range(len(input_x)):
        sma += abs(input_x[i]) + abs(input_y[i]) + abs(input_z[i])
    return sma/len(input_x)

"""
def get_AR(input):
    AR = aryule(input, 4)[0]
    return AR
"""

def get_skewness(input):
    return stats.skew(input)

def get_max_index(input):
    return np.argmax(input)

def get_fft(input):
    return np.fft.fft(input)

def get_time_features(input):
    time_features = []
    acc_x, acc_y, acc_z, acc_mag, gyro_x, gyro_y, gyro_z = input
    stats = [get_min, get_max, get_mean, get_std, get_MAD]
    for func in stats:
        time_features.extend([func(acc_x), func(acc_y), func(acc_z), func(acc_mag), func(gyro_x), func(gyro_y), func(gyro_z)])
    time_features.extend([get_sma([acc_x, acc_y, acc_z]), get_sma([gyro_x, gyro_y, gyro_z])])
    return time_features

def get_freq_features(input, count):
    freq_features = [] 
    freq_acc_x, freq_acc_y, freq_acc_z, freq_acc_mag, freq_gyro_x, freq_gyro_y, freq_gyro_z = [np.abs(get_fft(np.asanyarray(val)) / count) for val in input]
    stats = [get_min, get_max, get_mean, get_std, get_MAD, get_max_index, get_skewness]
    for func in stats:
        freq_features.extend([func(freq_acc_x), func(freq_acc_y), func(freq_acc_z), func(freq_acc_mag), func(freq_gyro_x), func(freq_gyro_y), func(freq_gyro_z)])
    return freq_features

def get_time_features_position(input):
    time_features = []
    acc_z = input
    stats = [get_min, get_max, get_mean, get_std, get_MAD]
    for func in stats:
        time_features.extend([func(acc_z)])
    return time_features

def get_freq_features_position(input, count):
    freq_features = [] 
    freq_acc_z = np.abs(get_fft(np.asanyarray(input)) / count)
    stats = [get_min, get_max, get_mean, get_std, get_MAD, get_max_index, get_skewness]
    for func in stats:
        freq_features.extend([func(freq_acc_z)])
    return freq_features
    
def get_features(window):
    features = []
    count = len(window)
    window = np.asarray(window)
    window_transpose = window.T
    final_data = window_transpose[3:6]
    acc_mag = get_l2_mag(final_data)
    final_data = np.append(final_data, acc_mag.reshape(1, -1), axis=0)
    final_data = np.append(final_data, window_transpose[0:3], axis=0)

    features.extend(get_time_features(final_data))
    features.extend(get_freq_features(final_data, count))

    return np.asarray(features, dtype=np.single)

def get_position_features(window):
    pos_features = []
    count = len(window)

    window = np.asarray(window)
    window_transpose = window.T

    pos_features.extend(get_time_features_position(window_transpose))
    pos_features.extend(get_freq_features_position(window_transpose, count))

    return np.asarray(pos_features)

# print(len(get_position_features([3, 3, 3, 5, 5, 5])))
# print((get_features([[3, 3, 3, 5, 5, 5], [5, 5, 5, 3, 3, 3], [5, 5, 5, 3, 3, 3], [5, 5, 5, 3, 3, 3], [5, 5, 5, 3, 3, 3], [5, 5, 5, 3, 3, 3]])))
