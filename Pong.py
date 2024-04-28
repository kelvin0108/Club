import random
import math
import keyboard
import numpy as np
import matplotlib.pyplot as plt



class Game:

  def __init__(self, game_mode):
    self.game_mode = game_mode
    self.action_space_size = 3
    self.bar_length = 30
    self.fig, self.ax = plt.subplots() 
    self.img = None  
    self.angle_text = None 
    self.frame_text = None
    self.player_score_text = None
    self.opponent_score_text = None


  def reset(self, render):
    self.render_ = render
    self.reset_ball_and_bar()
    self.player_score = 0
    self.opponent_score = 0
    self.done = False
    self.frame = 0
    if self.render_ == 1:
      self.render()
    return self.state, self.reward, self.done, self.frame

  def reset_ball_and_bar(self):
    self.bar_top = 79 - self.bar_length // 2 + 1
    self.opponent_bar_top = 79 - self.bar_length // 2 + 1
    self.state = np.zeros([160, 210])
    self.state[self.bar_top:self.bar_top + self.bar_length, 1] = 3  #player
    self.state[self.bar_top:self.bar_top + self.bar_length, 208] = 2  #opponent
    self.ball_angle = random.uniform(0, math.pi * 2)
    while self.ball_angle < (math.pi / 6) or self.ball_angle > (math.pi * 11 / 6) or (math.pi * 5 / 6 < self.ball_angle < math.pi * 7 / 6) or (math.pi * 2 / 6 < self.ball_angle < math.pi * 4 / 6) or (math.pi * 8 / 6 < self.ball_angle < math.pi * 10 / 6):
      self.ball_angle = random.uniform(0, math.pi * 2)
      self.ball_angle = random.uniform(0, math.pi * 2)
    self.ball_speed = 2
    self.ball_position = [random.randrange(104, 106), random.randrange(79, 81)]
    self.state[self.ball_position[1], self.ball_position[0]] = 1
    self.reward = 0
    return self.ball_angle, self.ball_speed, self.ball_position

  def step(self, action):
    frame_limit = 3150
    detect_range = 45
    self.action = action
    if self.game_mode == "human":
      if keyboard.read_key() == "down":
        self.action = 0
      elif keyboard.read_key() == "space":
        self.action = 1
      elif keyboard.read_key() == "up":
        self.action = 2
    elif self.game_mode == "ai":    
      assert 0 <= action <= self.action_space_size - 1, f"Error: Action values should fall within the interval [0, {self.action_space_size-1}]."
    assert self.done == False, "The game has ended."
    self.state[self.bar_top:self.bar_top + self.bar_length, 1] = 0
    if self.bar_top + 1 - self.action > 0 and self.bar_top + 1 - self.action + self.bar_length - 1 < 159:
      self.bar_top = self.bar_top + 1 - self.action  # 0:down, 1:no move, 2:up
    self.state[self.bar_top:self.bar_top + self.bar_length, 1] = 3
    self.state[self.opponent_bar_top:self.opponent_bar_top + self.bar_length, 208] = 0
    if self.ball_position[0] >= (208 - detect_range):
      if self.ball_position[1] >= self.opponent_bar_top + (self.bar_length / 2 + 1) and self.opponent_bar_top + 1 + self.bar_length - 1 <= 158:
        self.opponent_bar_top += 1 #go down
      elif self.ball_position[1] <= self.opponent_bar_top + (self.bar_length / 2) and self.opponent_bar_top >= 1:
        self.opponent_bar_top -= 1 #go up 
    elif self.opponent_bar_top < 79 - self.bar_length // 2 + 1:
      self.opponent_bar_top += 1
    elif self.opponent_bar_top > 79 - self.bar_length // 2 + 1:
      self.opponent_bar_top -= 1
    self.state[self.opponent_bar_top:self.opponent_bar_top + self.bar_length, 208] = 2
    self.update_ball_position()
    if self.player_score == 21 or self.opponent_score == 21 or self.frame == frame_limit:
      self.done = True
    self.frame += 1
    if self.render_ == 1:
      self.render()

  def update_ball_position(self):
    new_x = int(self.ball_position[0] +
                self.ball_speed * math.cos(self.ball_angle))
    new_y = int(self.ball_position[1] +
                self.ball_speed * math.sin(self.ball_angle))
    if 0<= new_x <= 209:
      while new_y <= 0 or new_y >= 159 or new_x <= 1 or new_x >= 208:
        if new_y <= 0 or new_y >= 159:
          self.ball_angle = math.pi * 2 - self.ball_angle
        elif new_x <= 1 or new_x >= 208:
          self.ball_angle = (math.pi * 3 - self.ball_angle) % (2 * math.pi)
        new_x = int(new_x + self.ball_speed * math.cos(self.ball_angle))
        new_y = int(new_y + self.ball_speed * math.sin(self.ball_angle))
      self.state[self.ball_position[1], self.ball_position[0]] = 0
      self.ball_position = [new_x, new_y]
    if new_x <= 0:
      self.opponent_score += 1
      self.reward = -1
      self.reset_ball_and_bar()                  
    elif new_x >= 209:
      self.player_score += 1
      self.reward = 1
      self.reset_ball_and_bar()
    else:
      self.state[self.ball_position[1], self.ball_position[0]] = 1

  def action_space(self):
    return np.arange(self.action_space_size)

  def sample_action(self):
    return np.random.choice(self.action_space(), 1).item()

  def render(self):
    if self.img:
      self.img.set_data(self.state)  
    else:
      self.img = self.ax.imshow(self.state, cmap='viridis', interpolation='nearest')  

    if self.angle_text:
      self.angle_text.set_text(f"Angle: {self.ball_angle:.2f}")  
    else:
      self.angle_text = self.ax.text(0.5, 1.01, f"Angle: {self.ball_angle:.2f}", transform=self.ax.transAxes,
                                      ha="center")  
    if self.frame_text:
      self.frame_text.set_text(f"Frame: {self.frame}")  
    else:
      self.frame_text = self.ax.text(0.5, 0.01, f"Frame: {self.frame}", transform=self.ax.transAxes,
                                      ha="center")  
    if self.player_score_text:
      self.player_score_text.set_text(f"Player Score: {self.player_score}")  
    else:
      self.player_score_text = self.ax.text(0.01, 0.95, f"Player Score: {self.player_score}", transform=self.ax.transAxes,
                                              ha="left")  
    if self.opponent_score_text:
      self.opponent_score_text.set_text(f"Opponent Score: {self.opponent_score}")  
    else:
      self.opponent_score_text = self.ax.text(0.99, 0.95, f"Opponent Score: {self.opponent_score}", transform=self.ax.transAxes,
                                                ha="right")             
    self.fig.canvas.draw()  
    plt.pause(0.001)  
