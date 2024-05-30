import copy
import time

from environments import pong_jesse
import numpy as np

import collections
import torch
import torch.nn as nn
import torch.optim as optim

import wandb


def weights_init_normal(m):
    '''Takes in a module and initializes all linear layers with weight
       values taken from a normal distribution.'''

    classname = m.__class__.__name__
    # for every Linear layer in a model
    if classname.find('Linear') != -1:
        y = m.in_features
        # m.weight.data shoud be taken from a normal distribution
        m.weight.data.normal_(0.0,1/np.sqrt(y))
        # m.bias.data should be 0
        m.bias.data.fill_(0)

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
BATCH_SIZE = 512

REPLAY_SIZE = 10000
REPLAY_START_SIZE = 10000

EPSILON_START = 0.98
EPSILON_FINAL = 0.02
EPSILON_DECAY_FRAME = 100000

TGT_SYNC_FRAME = 1000
LEARNING_RATE = 0.0001

DISPLAY_INTERVAL = 2

Experience = collections.namedtuple("Experience", field_names=["state", "action", "reward", "done", "new_state"])

layer_and_node = (4, 256, 3)
net = nn.Sequential(
    nn.Linear(4, 256),
    nn.ReLU(),
    nn.Linear(256, 3)
)
# net.apply(weights_init_normal)
tgt_net = copy.deepcopy(net)

optimizer = optim.Adam(params=net.parameters(), lr=LEARNING_RATE)

replay_buffer = ReplayBuffer(REPLAY_SIZE)

game = pong_jesse.Game(game_mode="ai", render=0)
state, info = game.reset()

key = input("Please enter wandb authorize key (https://wandb.ai/authorize): ")
if key != " No":
    wandb.login(key=key)
    wandb.init(
        entity="School Project",
        project="Pong_2",
        name="Attempt03 " + str(layer_and_node) + f" (Batch size = {BATCH_SIZE})",
    )

print(net)
print(f"Gamma: {GAMMA}.\n"
      f"Batch Size: {BATCH_SIZE}. Replay Size: {REPLAY_SIZE}. Replay Start Size: {REPLAY_START_SIZE}.\n"
      f"Epsilon Start: {EPSILON_START}. Epsilon Final: {EPSILON_FINAL}. Epsilon Decay Frame: {EPSILON_DECAY_FRAME}.\n"
      f"Target Network Sync Frame: {TGT_SYNC_FRAME}.\n"
      f"Learning Rate: {LEARNING_RATE}.\n\n")

epsilon = EPSILON_START
frame_count = 0
game_count = 0
avg_score = 0
ts = time.time()
ts_frame = 0
last_50_score = collections.deque(maxlen=50)
_neg20, _neg10, _0, _10, _15, _16, _17, _18, _19, _20 = False, False, False, False, False, False, False, False, False, False
while avg_score < 19.5:
    frame_count += 1

    action = game.sample_action() if np.random.rand() < epsilon else net(torch.FloatTensor(state)).max(0)[1].item()
    # action = game.sample_action() if np.random.rand() < epsilon else net(torch.FloatTensor(state)).max(dim=1)[1].item()
    new_state, reward, done, info = game.step(action)

    replay_buffer.append(Experience(state, action, reward, done, new_state))

    if done:
        game_count += 1

        last_50_score.append(info["player"] - info["opponent"])
        speed = (frame_count - ts_frame) / (time.time() - ts)
        ts = time.time()
        ts_frame = frame_count
        avg_score = sum(last_50_score) / len(last_50_score)
        if key != "No":
            wandb.log({"game:": game_count, "frame": frame_count, "average score (difference)": avg_score, "epsilon": epsilon, "speed": speed})
        if game_count % DISPLAY_INTERVAL == 0:
            print(f"game: {game_count}. frame: {frame_count}. average score: {avg_score:.3f}. epsilon: {epsilon:.2f}. speed: {speed:.2f}f/s.")

        state, info = game.reset()

    state = new_state
    if epsilon > EPSILON_FINAL:
        epsilon -= (EPSILON_START - EPSILON_FINAL) / EPSILON_DECAY_FRAME

    if frame_count % TGT_SYNC_FRAME == 0:
        tgt_net.load_state_dict(net.state_dict())

    # Model saving.
    if avg_score > -20 and not _neg20:
        torch.save(net.state_dict(), f"Pong({avg_score:.2f}) " + str(layer_and_node))
        _neg20 = True
    if avg_score > -10 and not _neg10:
        torch.save(net.state_dict(), f"Pong({avg_score:.2f}) " + str(layer_and_node))
        _neg10 = True
    if avg_score > 0 and not _0:
        torch.save(net.state_dict(), f"Pong({avg_score:.2f}) " + str(layer_and_node))
        _0 = True
    if avg_score > 10 and not _10:
        torch.save(net.state_dict(), f"Pong({avg_score:.2f}) " + str(layer_and_node))
        _10 = True
    if avg_score > 15 and not _15:
        torch.save(net.state_dict(), f"Pong({avg_score:.2f}) " + str(layer_and_node))
        _15 = True
    if avg_score > 16 and not _16:
        torch.save(net.state_dict(), f"Pong({avg_score:.2f}) " + str(layer_and_node))
        _16 = True
    if avg_score > 17 and not _17:
        torch.save(net.state_dict(), f"Pong({avg_score:.2f}) " + str(layer_and_node))
        _17 = True
    if avg_score > 18 and not _18:
        torch.save(net.state_dict(), f"Pong({avg_score:.2f}) " + str(layer_and_node))
        _18 = True
    if avg_score > 19 and not _19:
        torch.save(net.state_dict(), f"Pong({avg_score:.2f}) " + str(layer_and_node))
        _19 = True

    if reward != 0:
        if frame_count < REPLAY_START_SIZE:
            continue

        optimizer.zero_grad()
        loss = calc_loss(replay_buffer.sample(BATCH_SIZE), net, tgt_net, GAMMA)
        loss.backward()
        optimizer.step()


torch.save(net.state_dict(), f"Pong({avg_score:.2f}) " + str(layer_and_node))
