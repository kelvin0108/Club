import random
import tkinter as tk
import numpy as np

H = np.array([[1, 1], [3, 1], [3, 2], [0, 3]])
G = np.array([3, 3])
MAP = [
    "SFFF",
    "FHFH",
    "FFFH",
    "HFFG"
    ]


class Game:

  def __init__(self, is_slippery):
    assert is_slippery == 0 or is_slippery == 1, "Error: is_slippery values should fall within the interval [0, 1]."
    self.is_slippery = is_slippery

  def reset(self):
    self.state = np.array([0, 0])
    self.reward = 0
    self.done = False
    return self.state

  def step(self, action):
    assert 0 <= action <= 3, "Error: Action values should fall within the interval [0, 3]."
    assert self.done == False, "The game has ended."
    self.action = random.randrange(action - self.is_slippery,
                                   action + self.is_slippery + 1, 1)
    old_state = self.state.copy()
    if self.action == 0 or self.action == 4:
      self.state[0] += 1
    elif self.action == 1:
      self.state[1] += 1
    elif self.action == 2:
      self.state[0] -= 1
    elif self.action == 3 or self.action == -1:
      self.state[1] -= 1
    if (self.state > np.array([3, 3])).any() or (self.state < np.array(
        [0, 0])).any():
      self.state = old_state
    if (self.state == G).all():
      self.reward += 1
      self.done = True
    for i in range(4):
      if (self.state == H[i]).all():
        self.done = True
    return self.state, self.done, self.reward
