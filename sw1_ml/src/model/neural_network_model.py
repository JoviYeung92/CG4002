from torch import nn
from torch.quantization import QuantStub, DeQuantStub

class Neural_Network_Model(nn.Module):
    def __init__(self, input_size, hidden_states, output_size):
        super().__init__()

        self.input_size = input_size
        self.hidden_states = hidden_states
        self.output_size = output_size
        
        # Inputs to hidden layer linear transformation
        self.linear = nn.Linear(input_size, hidden_states[0])
        self.hidden = nn.Linear(hidden_states[0], hidden_states[1])

        # Output layer, 10 units - one for each digit
        self.output = nn.Linear(hidden_states[1], output_size)
        self.relu = nn.ReLU()

        # Define sigmoid activation and softmax output 
        self.sigmoid = nn.Sigmoid()
        self.softmax = nn.Softmax(dim=1)
        
    def forward(self, x):
        # Pass the input tensor through each of our operations
        x = self.linear(x)
        x = self.relu(x)
        x = self.hidden(x)
        x = self.relu(x)
        x = self.sigmoid(x)
        x = self.output(x)
        x = self.softmax(x)
        
        return x

# Hyperparameters for our network
input_size = 1024 # X.shape[1]
hidden_states = [256, 128]
output_size = 3 # y.shape[1]

def neural_network_model_1(input_size, hidden_states, output_size):
    model = nn.Sequential(nn.Linear(input_size, hidden_states[0]),
                nn.ReLU(),
                nn.Linear(hidden_states[0], hidden_states[1]),
                nn.ReLU(),
                nn.Linear(hidden_states[1], output_size),
                nn.LogSoftmax(dim=1))        
    return model

def neural_network_model_fpga(input_size, hidden_states, output_size):
    model = nn.Sequential(QuantStub(),
                nn.Linear(input_size, hidden_states[0]),
                nn.ReLU(),
                nn.Linear(hidden_states[0], hidden_states[1]),
                nn.ReLU(),
                nn.Linear(hidden_states[1], output_size),
                nn.LogSoftmax(dim=1),
                DeQuantStub())        
    return model

def neural_network_model_2(input_size, hidden_states, output_size):
    model = nn.Sequential(nn.Linear(input_size, hidden_states[0]),
                nn.ReLU(),
                nn.Linear(hidden_states[0], hidden_states[1]),
                nn.ReLU(),
                nn.Linear(hidden_states[1], hidden_states[2]),
                nn.ReLU(),
                nn.Linear(hidden_states[2], output_size),
                nn.LogSoftmax(dim=1))        
    return model
