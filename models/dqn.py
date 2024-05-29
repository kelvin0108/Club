import torch
import torch.nn as nn
import numpy as np


class DQN(nn.Module):
    def __init__(self, input_shape, n_action):
        super(DQN, self).__init__()

        self.conv = nn.Sequential(
            # nn.Conv2d(input_shape[0], 1, kernel_size=2, stride=1, padding=1),
            # nn.ReLU(),
            # nn.MaxPool2d(kernel_size=2),
            # nn.ReLU()

            nn.Conv2d(input_shape[1], 32, kernel_size=8, stride=4),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1),
            nn.ReLU()
        )

        conv_out_size = self._get_conv_out(input_shape)
        self.fc = nn.Sequential(
            nn.Linear(conv_out_size, 512),
            nn.ReLU(),
            nn.Linear(512, n_action)
        )

    def _get_conv_out(self, shape):
        o = self.conv(torch.zeros(shape))
        return int(np.prod(o.size()))

    def forward(self, x):
        conv_out = self.conv(x).view(x.size()[0], -1)  # "-1"是作為其餘參數的通配符. "view" is used to flatten(reshape) output.  # FOR BATCHED.
        # conv_out = self.conv(x).view(-1)  # FOR UNBATCHED.
        return self.fc(conv_out)

