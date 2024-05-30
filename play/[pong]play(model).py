from environments import pong_jesse

import torch
import torch.nn as nn

net = nn.Sequential(
    nn.Linear(4, 512),
    nn.ReLU(),
    nn.Linear(512, 256),
    nn.ReLU(),
    nn.Linear(256, 3)
)
net.load_state_dict(torch.load("../Trained_Models/Pong(16.10) (4, 512, 256, 3)"))

game = pong_jesse.Game(game_mode="ai", render=1, offset=2)
state, info = game.reset()

frame = 0
done = False
print(info)
while not done:
    frame += 1
    action = net(torch.FloatTensor(state)).max(0)[1].item()
    state, reward, done, info = game.step(action)
    if reward != 0:
        print(info)

