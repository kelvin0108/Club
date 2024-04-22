import random
import math
import numpy as np


class Game:

  def __init__(self, game_mode):
    self.game_mode = game_mode
    self.action_space_size = 3

  def reset(self):
    self.state = np.zeros([210, 160])
    self.state[1, 100:111] = 3
    self.state[158, 100:111] = 2
    
    self.state[self.ball] = 1
    self.reward = 0
    self.done = False
    self.frame = 0
    self.bar = 100
    return self.state, self.reward, self.done, self.frame

  def reset_ball(self):
    self.ball_angle = random.uniform(-math.pi/4, math.pi/4)
    self.ball_speed = 1 
    self.ball_position = [random.randrange(104, 106),
                          random.randrange(104, 106)]
    return self.ball_angle, self.ball_speed, self.ball_position

  def step(self, action):
    self.action = action
    assert 0 <= action <= self.action_space_size - 1, f"Error: Action values should fall within the interval [0, {self.action_space_size-1}]."
    assert self.done == False, "The game has ended."
    self.state[158, self.bar:self.bar + 11] = 0
    if self.action == 0:
      self.bar -= 1
    elif self.action == 2:
      self.bar += 1
    self.state[158, self.bar:self.bar + 11] = 2
    self.update_ball_position()
    self.frame += 1

  def update_ball_position(self):
      new_x = int(self.ball_position[0] + self.ball_speed * math.cos(self.ball_angle))
      new_y = int(self.ball_position[1] + self.ball_speed * math.sin(self.ball_angle))
      if new_x <= 0 or new_x >= 209:
        self.ball_angle = (math.pi*3 - self.ball_angle) % (2*math.pi)
      elif self.state[new_y, new_x] == 2 or self.state[new_y, new_x] == 3:
        self.ball_angle = math.pi*2 - self.ball_angle
      elif (new_x <= 0 or new_x >= 209) and (self.state[new_y, new_x] == 2 or self.state[new_y, new_x] == 3):
        self.ball_angle = (self.ball_angle + math.pi) % (2*math.pi)
      self.state[self.ball_position[1], self.ball_position[0]] = 0
      self.ball_position = [new_x, new_y]
      self.state[self.ball_position[1], self.ball_position[0]] = 1
          
        
        
  def action_space(self):
    return np.arange(self.action_space_size)

  def sample_action(self):
    return np.random.choice(self.action_space(), 1).item()


