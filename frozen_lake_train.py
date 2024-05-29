import copy

from environments import frozen_lake
import numpy as np

import collections
import torch
import torch.nn as nn
import torch.optim as optim

import wandb


class ReplayBuffer:
    def __init__(self, capacity=100):
        self.buffer = collections.deque(maxlen=capacity)

    def append(self, exp):
        self.buffer.append(exp)

    def __len__(self):
        return len(self.buffer)

    def sample(self, batch_size):
        indices = np.random.choice(len(self.buffer), batch_size, replace=False)
        states, actions, rewards, dones, next_states = zip(*[self.buffer[idx] for idx in indices])
        return np.array(states), np.array(actions), np.array(rewards), np.array(dones), np.array(next_states)


def calc_loss(batch, net, tgt_net, gamma):
    states, actions, rewards, dones, new_states = batch
    states_t = torch.FloatTensor(states)
    action_t = torch.IntTensor(actions)
    rewards_t = torch.FloatTensor(rewards)
    new_states_t = torch.FloatTensor(new_states)

    state_action_values = net(states_t).gather(1, action_t.type(torch.int64).unsqueeze(-1)).squeeze(-1)

    next_state_values = tgt_net(new_states_t).max(1)[0]
    next_state_values[dones] = 0.0
    next_state_values = next_state_values.detach()

    expected_state_action_values = rewards_t + next_state_values * gamma

    return nn.MSELoss()(state_action_values, expected_state_action_values)


GAMMA = 0.99
BATCH_SIZE = 8

REPLAY_SIZE = 2000
REPLAY_START_SIZE = 2000

EPSILON_START = 0.98
EPSILON_FINAL = 0.02
EPSILON_DECAY_FRAME = 50000

TGT_SYNC_FRAME = 1000
LEARNING_RATE = 0.0001

DISPLAY_INTERVAL = 100

Experience = collections.namedtuple("Experience", field_names=["state", "action", "reward", "done", "new_state"])

# net = models.dqn.DQN((1, 4, 4), 4)
net = nn.Sequential(
    nn.Linear(16, 200),
    nn.ReLU(),
    nn.Linear(200, 100),
    nn.ReLU(),
    nn.Linear(100, 4)
)
tgt_net = copy.deepcopy(net)

optimizer = optim.Adam(params=net.parameters(), lr=LEARNING_RATE)

replay_buffer = ReplayBuffer(REPLAY_SIZE)

game = frozen_lake.Game(1, 200)
state = game.reset()
print(net)


key = input("Please enter wandb authorize key (https://wandb.ai/authorize): ")
wandb.login(key=key)
wandb.init(
    entity="School Project",
    project="FrozenLake",
    name="Attempt03(3 layers without Conv2d)",
)


epsilon = EPSILON_START
frame_count = 0
game_count = 0
score = 0
while score < 95:
    frame_count += 1

    action = game.sample_action() if np.random.rand() < epsilon else net(torch.FloatTensor(state)).max(0)[1].item()
    # action = game.sample_action() if np.random.rand() < epsilon else net(torch.FloatTensor(state)).max(dim=1)[1].item()
    new_state, done, reward = game.step(action)

    replay_buffer.append(Experience(state, action, reward, done, new_state))

    if done:
        game_count += 1

        if game_count % DISPLAY_INTERVAL == 0:
            last_50_game_won = []
            for i in range(50):
                done = False
                state = game.reset()
                while not done:
                    state, done, reward = game.step(net(torch.FloatTensor(state)).max(0)[1].item())
                    # state, done, reward = game.step(net(torch.FloatTensor(state)).max(dim=1)[1].item())
                last_50_game_won.append(reward)
            score = sum(last_50_game_won)*2
            wandb.log({"frame": frame_count, "win rate": score, "epsilon": epsilon})
            print(f"frame: {frame_count}. win rate: {score}%. epsilon: {epsilon}.")

        game.reset()


    state = new_state
    if epsilon > EPSILON_FINAL:
        epsilon -= (EPSILON_START - EPSILON_FINAL) / EPSILON_DECAY_FRAME

    if frame_count < REPLAY_START_SIZE:
        continue

    optimizer.zero_grad()
    loss = calc_loss(replay_buffer.sample(BATCH_SIZE), net, tgt_net, GAMMA)
    loss.backward()
    optimizer.step()

    if frame_count % TGT_SYNC_FRAME == 0:
        tgt_net.load_state_dict(net.state_dict())

torch.save(net.state_dict(), f"FrozenLake({score}%)")
