import random
import math
import numpy as np


class Game:

  def __init__(self, game_mode):
    self.game_mode = game_mode
    self.action_space_size = 3

  def reset(self):
    self.state = np.zeros([160, 210])
    self.reset_ball_and_bar()
    self.player_score = 0
    self.opponent_score = 0
    self.reward = 0
    self.done = False
    self.frame = 0
    return self.state, self.reward, self.done, self.frame

  def reset_ball_and_bar(self):
    self.bar = 75
    self.state[self.bar:self.bar + 10, 1] = 3 #player
    self.state[self.bar:self.bar + 10, 208] = 2 #opponent
    self.ball_angle = random.uniform(-math.pi/4, math.pi/4)
    self.ball_speed = 1 
    self.ball_position = [random.randrange(104, 106),
                          random.randrange(79, 81)]
    self.state[self.ball_position[1], self.ball_position[0]] = 1
    return self.ball_angle, self.ball_speed, self.ball_position

  def step(self, action):
    self.action = action
    assert 0 <= action <= self.action_space_size - 1, f"Error: Action values should fall within the interval [0, {self.action_space_size-1}]."
    assert self.done == False, "The game has ended."
    self.state[self.bar:self.bar + 10, 1] = 0
    if self.bar + 1 - self.action > 0 and self.bar + 1 - self.action + 10 < 159:
      self.bar = self.bar + 1 - self.action # 0:up, 1:no move, 2:down
    self.state[self.bar:self.bar + 10, 1] = 3
    self.update_ball_position()
    if self.player_score == 21 or self.opponent_score == 21:
      self.done = True
      if self.player_score == 21:
        self.reward += 1
      else:
        self.reward += -1
    elif self.frame == 120:
      if self.player_score > self.opponent_score:
        self.reward += 1
      elif self.player_score < self.opponent_score:
        self.reward += -1
      self.done = True
    else:
      self.frame += 1

  def update_ball_position(self):
      new_x = int(self.ball_position[0] + self.ball_speed * math.cos(self.ball_angle))
      new_y = int(self.ball_position[1] + self.ball_speed * math.sin(self.ball_angle))
      if new_y <= 0 or new_y >= 159:
        self.ball_angle = math.pi*2 - self.ball_angle
      elif self.state[new_y, new_x] == 2 or self.state[new_y, new_x] == 3:
        self.ball_angle = (math.pi*3 - self.ball_angle) % (2*math.pi)
      new_x = int(new_x + self.ball_speed * math.cos(self.ball_angle))
      new_y = int(new_y + self.ball_speed * math.sin(self.ball_angle))
      self.state[self.ball_position[1], self.ball_position[0]] = 0
      self.ball_position = [new_x, new_y]
      if new_x <= 0:
        self.opponent_score += 1
        self.reset_ball_and_bar()
      elif new_x >= 209:
        self.player_score += 1
        self.reset_ball_and_bar()
      else:
        self.state[self.ball_position[1], self.ball_position[0]] = 1
          
  
  def action_space(self):
    return np.arange(self.action_space_size)

  def sample_action(self):
    return np.random.choice(self.action_space(), 1).item()

