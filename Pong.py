import random
import math
import keyboard
import numpy as np
import pygame
import sys
from pygame.locals import *
import threading

class Game:

  def __init__(self, game_mode):
    self.game_mode = game_mode
    self.action_space_size = 3
    self.bar_length = 30


  def reset(self, render):
    self.render_ = render
    self.reset_ball_and_bar()
    self.player_score = 0
    self.opponent_score = 0
    self.done = False
    self.frame = 0
    if self.render_ == 1:
      self.render()
    self.step(None)
    return self.state, self.reward, self.done, self.frame

  def reset_ball_and_bar(self):
    self.ball_speed = 2
    self.bar_top = 79 - self.bar_length // 2 + 1
    self.opponent_bar_top = 79 - self.bar_length // 2 + 1
    self.state = np.zeros([160, 210])
    self.state[self.bar_top:self.bar_top + self.bar_length, 1:2] = 3  #player
    self.state[self.bar_top:self.bar_top + self.bar_length, 207:208] = 2  #opponent
    temp = random.randint(1, 4)
    self.ball_angle = random.uniform((math.pi * (3 * temp - 2)) / 6, (math.pi * (3 * temp - 1)) / 6 )
    self.ball_position = [random.randrange(104, 106), random.randrange(79, 81)]
    self.state[self.ball_position[1], self.ball_position[0]] = 1
    self.reward = 0
    return self.ball_angle, self.ball_speed, self.ball_position

  def step(self, action):
    if action != None:
      frame_limit = 3150
      detect_range = 45
      self.action = action
      if self.game_mode == "human":
        key = keyboard.read_key()
        while key != "down" and key != "space" and key != "up":
          key = keyboard.read_key()
        if key == "down":
          self.action = 0
        elif key == "space":
          self.action = 1
        elif key == "up":
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
      while new_y <= 0 or new_y >= 159 or (new_x <= 6 and self.bar_top <= new_y <= self.bar_top + self.bar_length - 1) or (new_x >= 203 and self.opponent_bar_top <= new_y <= self.opponent_bar_top + self.bar_length - 1):
        if new_y <= 0 or new_y >= 159:
          self.ball_angle = math.pi * 2 - self.ball_angle
        elif (new_x <= 6 and self.bar_top <= new_y <= self.bar_top + self.bar_length - 1) or (new_x >= 203 and self.opponent_bar_top <= new_y <= self.opponent_bar_top + self.bar_length - 1): #板子打到球
          self.ball_angle = (math.pi * 3 - self.ball_angle) % (2 * math.pi)
          self.ball_speed = 3
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
    pygame.init()
    
    self.DISPLAY = pygame.display.set_mode((210, 160))
    pygame.display.set_caption("PONG")
    
    self.DISPLAY.fill((0,0,0))
    pygame.draw.circle(self.DISPLAY, (255, 255, 255), (self.ball_position[0], self.ball_position[1]), 4, 0)
    pygame.draw.rect(self.DISPLAY, (255, 255, 255), (1, self.bar_top, 5, self.bar_length))
    pygame.draw.rect(self.DISPLAY, (255, 255, 255), (203, self.opponent_bar_top, 5, self.bar_length))
    font = pygame.font.Font(None, 36)
    frame_text = font.render("Frame: {}".format(self.frame), True, (255, 255, 255))
    self.DISPLAY.blit(frame_text, (10, 10))  
    frame_text = font.render("Angle: {}".format(self.ball_angle), True, (255, 255, 255))
    self.DISPLAY.blit(frame_text, (10, 30))  
  def run_game(self):
    while True:
      for event in pygame.event.get():
          if event.type == pygame.QUIT:
            pygame.display.quit()
            sys.exit()
           
      self.step(4)
      pygame.display.update()
      clock.tick(120)
    
clock = pygame.time.Clock()
game = Game("human")
game.reset(1) 
game.ball_angle = math.pi / 4
game.run_game()