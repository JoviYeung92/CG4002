# Prepare data for training and testing
import torch
import torch.utils.data
from torch import nn
import torch.nn.functional as F

import numpy as np

from sklearn.utils import shuffle

class Prepare_data(torch.utils.data.Dataset):
    def __init__(self, inputs, labels):
        self.inputs = inputs
        self.labels = labels

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, index):
        x = self.inputs[index]
        y = self.labels[index]
        return x, y

def load_neural_network_data(X_train, y_train, X_test, y_test):
    X_train, y_train, X_test, y_test = np.asarray(X_train), np.asarray(y_train), np.asarray(X_test), np.asarray(y_test)
    X_train = torch.from_numpy(X_train).float()
    y_train = torch.from_numpy(y_train).float()
    y_train = y_train.reshape(y_train.shape[0]).long()
    
    X_test = torch.from_numpy(X_test).float()
    y_test = torch.from_numpy(y_test).float()
    y_test = y_test.reshape(y_test.shape[0]).long()

    trainloader = torch.utils.data.DataLoader(Prepare_data(X_train, y_train), batch_size=32, shuffle=True)
    testloader = torch.utils.data.DataLoader(Prepare_data(X_test, y_test), batch_size=32)
    return trainloader, testloader
