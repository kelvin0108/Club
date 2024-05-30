from environments import pong_jesse

import torch
import torch.nn as nn

net = nn.Sequential(
    nn.Linear(4, 256),
    nn.ReLU(),
    nn.Linear(256, 3),

    # nn.Linear(4, 512),
    # nn.ReLU(),
    # nn.Linear(512, 256),
    # nn.ReLU(),
    # nn.Linear(256, 3)
)
net.load_state_dict(torch.load("../Trained_Models/Pong/(4, 256, 3)/Pong(5.00) (4, 256, 3)"))

game = pong_jesse.Game(game_mode="human_ai", render=1, net=net)
state, info = game.reset()
