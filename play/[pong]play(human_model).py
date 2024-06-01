import sys
import os

# 获取当前脚本所在目录的绝对路径
current_dir = os.path.dirname(__file__)

# 获取包的根目录的绝对路径
package_root = os.path.abspath(os.path.join(current_dir, ".."))

# 将包的根目录添加到系统路径中
sys.path.append(package_root)
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
net.load_state_dict(torch.load("Trained_Models/Pong/(4, 256, 3)/Pong(15.02) (4, 256, 3)"))

game = pong_jesse.Game(game_mode="human_ai", render=1, net=net, pad_skin="Kelvin", ball_skin="Billy")
state, info = game.reset()
