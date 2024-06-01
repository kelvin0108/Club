import torch
import torch.nn as nn
import sys
import os

# 获取当前脚本所在目录的绝对路径
current_dir = os.path.dirname(__file__)

# 获取包的根目录的绝对路径
package_root = os.path.abspath(os.path.join(current_dir, ".."))

# 将包的根目录添加到系统路径中
sys.path.append(package_root)
from environments import frozen_lake
env = frozen_lake.Game(is_slippery=1, game_mode="ai", max_step=150, render=1, skin="Billy")

net = nn.Sequential(
    nn.Linear(16, 200),
    nn.ReLU(),
    nn.Linear(200, 100),
    nn.ReLU(),
    nn.Linear(100, 4)
)
net.load_state_dict(torch.load("Trained_Models/FrozenLake(96%) (16, 200, 100, 4)"))

state = env.reset()
if env.render == 0:
    print(env.show_map(), end="\r")
    print("Initial:")

total_reward = 0
while True:
    
    action = net(torch.FloatTensor(state)).max(0)[1].item()
    state, done, reward = env.step(action)

    if action == 0:
        display_action = "right"
    elif action == 1:
        display_action = "down"
    elif action == 2:
        display_action = "left"
    elif action == 3:
        display_action = "up"
    print("Action:", display_action, end="\n\n")
    total_reward += reward
    if env.render == 0:
        print(env.show_map(), end="\r")
    if done:
        break

print(total_reward)

