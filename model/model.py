import torch.nn as nn

class FlexibleNN(nn.Module):
    def __init__(self, topology):
        super(FlexibleNN, self).__init__()
        self.layers = nn.ModuleList()
        for i in range(len(topology) - 1):
            self.layers.append(nn.Linear(topology[i], topology[i + 1]))
        self.relu = nn.ReLU()

    def forward(self, x):
        out = x
        for i, layer in enumerate(self.layers):
            out = layer(out)
            if i < len(self.layers) - 1:
                out = self.relu(out)
        return out