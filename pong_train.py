import time

from models import dqn
from environments import pong_v2
import numpy as np

import collections
import torch
import torch.nn as nn
import torch.optim as optim

import wandb


class FrameBuffer:
    def __init__(self, stack=4):
        self.stack = stack
        self.deque = collections.deque(maxlen=stack)

    def reset(self):
        self.deque.clear()

    def append(self, state):
        self.deque.append(state)

    def get_state(self):
        buffer = np.zeros((self.stack, 160, 210))
        for i in range(len(self.deque)):
            buffer[i] = np.array(self.deque[i])
        return buffer


class SkipAndBuffer:
    def __init__(self, env, skip=4):
        self.env = env
        self.skip = skip

    def reset(self):
        state, info = self.env.reset()
        return state, info

    def step(self, action):
        total_reward = 0
        buffer = np.zeros((self.skip, 160, 210))
        for i in range(self.skip):
            state, reward, done, info = self.env.step(action)
            total_reward += reward
            buffer[i] = np.array(state)
            if done:
                break
        max_frame = np.max(np.stack(buffer), axis=0)
        return max_frame, total_reward, done, info


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
BATCH_SIZE = 32

REPLAY_SIZE = 10000
REPLAY_START_SIZE = 10000

EPSILON_START = 0.98
EPSILON_FINAL = 0.02
EPSILON_DECAY_FRAME = 100000

TGT_SYNC_FRAME = 1000
LEARNING_RATE = 0.0001

DISPLAY_INTERVAL = 100

Experience = collections.namedtuple("Experience", field_names=["state", "action", "reward", "done", "new_state"])

skip_and_stack = 4
game = pong_v2.Game(game_mode="ai", render=0)
env_wrapper = SkipAndBuffer(game, skip=skip_and_stack)
state, info = env_wrapper.reset()
buffer = FrameBuffer(stack=skip_and_stack)
buffer.append(state)
state = buffer.get_state()

net = dqn.DQN((1, 4, 160, 210), game.action_space())
tgt_net = dqn.DQN((1, 4, 160, 210), game.action_space())

optimizer = optim.Adam(params=net.parameters(), lr=LEARNING_RATE)

replay_buffer = ReplayBuffer(REPLAY_SIZE)

print(net)

key = input("Please enter wandb authorize key (https://wandb.ai/authorize): ")
wandb.login(key=key)
wandb.init(
    # entity="School Project",
    project="Pong",
    name="Attempt01",
)


epsilon = EPSILON_START
frame_count = 0
ts = time.time()
ts_frame = 0
game_count = 0
last_100_games = collections.deque(maxlen=100)
avg_score = 0
while avg_score < 18:
    frame_count += skip_and_stack

    # action = game.sample_action() if np.random.rand() < epsilon else net(torch.FloatTensor(state.reshape(1, skip, 160, 210))).max(0)[1].item()
    action = game.sample_action() if np.random.rand() < epsilon else net(torch.FloatTensor(state.reshape(1, skip_and_stack, 160, 210))).max(dim=1)[1].item()
    new_state, done, reward, info = env_wrapper.step(action)
    buffer.append(new_state)
    new_state = buffer.get_state()

    replay_buffer.append(Experience(state, action, reward, done, new_state))

    if done:
        game_count += 1
        speed = (frame_count - ts_frame) / (time.time() - ts)
        ts_frame = frame_count
        ts = time.time()
        last_100_games.append(info["player"])
        avg_score = sum(last_100_games)/len(last_100_games)
        wandb.log({"frame": frame_count, "average score": avg_score, "epsilon": epsilon, "speed": speed})
        print(f"frame: {frame_count}. average score: {avg_score:.3f}. epsilon: {epsilon:.2f}. speed {speed:.2f}f/s.")  # TODO --> can delete.
        # if game_count % DISPLAY_INTERVAL == 0:
        #     print(f"frame: {frame_count}. average score: {avg_score:.3f}. epsilon: {epsilon:.2f}. speed {speed:.2f}f/s.")

        state, info = env_wrapper.reset()
        buffer.reset()
        buffer.append(state)
        state = buffer.get_state()

        if frame_count < REPLAY_START_SIZE:
            continue

        optimizer.zero_grad()
        loss = calc_loss(replay_buffer.sample(BATCH_SIZE), net, tgt_net, GAMMA)
        loss.backward()
        optimizer.step()

    state = new_state
    if epsilon > EPSILON_FINAL:
        epsilon -= (EPSILON_START - EPSILON_FINAL) / EPSILON_DECAY_FRAME

    if frame_count % TGT_SYNC_FRAME == 0:
        tgt_net.load_state_dict(net.state_dict())

torch.save(net.state_dict(), f"Pong({avg_score}%)")
