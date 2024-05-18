import random
import math
import keyboard
import numpy as np
import pygame
import sys
from pygame.locals import *
import time

class Game:
    def __init__(self, game_mode):
        self.game_mode = game_mode
        self.action_space_size = 3
        self.bar_length = 30
        self.frame_limit = 8000
        self.hide_info = False
        self.skip_step = False

    def reset(self, render):
        self.pause = True
        self.render_ = render
        self.reset_ball_and_bar()
        self.player_score = 0
        self.opponent_score = 0
        self.done = False
        self.frame = 0
        if self.render_ == 1:
            self.render()
            pygame.display.update()
            info = {"player": self.player_score, "opponent": self.opponent_score}
        return self.state.reshape((1, 210, 160)), info

    def reset_ball_and_bar(self):
        self.ball_speed = 2
        self.bar_top = 79 - self.bar_length // 2 + 1
        self.opponent_bar_top = 79 - self.bar_length // 2 + 1
        self.state = np.zeros([160, 210])
        self.state[self.bar_top:self.bar_top + self.bar_length, 1:2] = 3  # player
        self.state[self.bar_top:self.bar_top + self.bar_length, 207:208] = 2  # opponent
        temp = random.randint(1, 4)
        self.ball_angle = random.uniform((math.pi * (3 * temp - 2)) / 6, (math.pi * (3 * temp - 1)) / 6)
        self.ball_position = [random.randrange(104, 106), random.randrange(79, 81)]
        self.state[self.ball_position[1], self.ball_position[0]] = 1
        self.reward = 0
        return self.ball_angle, self.ball_speed, self.ball_position

    def step(self, action): 
        detect_range = 45
        self.action = action
        self.stop_one_sec = False
        self.skip_step = False
        if self.game_mode == "human":
            key = keyboard.read_key()
            while key != "down" and key != "space" and key != "up" and key != "enter" and key != "shift" and key != "right shift" and key != "esc":
                key = keyboard.read_key()
            if key == "esc":
                sys.exit()
            elif key == "shift" or key == "right shift":
                if self.hide_info == False:    
                    self.hide_info = True
                else:
                    self.hide_info = False
                self.render()
                self.skip_step = True
                time.sleep(0.5)
            if key == "down":
                self.action = 0
            elif key == "space":
                self.action = 1
            elif key == "up":
                self.action = 2    
            elif key == "enter":
                self.pause = True
                self.render()
                self.stop_one_sec = True

        elif self.game_mode == "ai":
            assert 0 <= action <= self.action_space_size - 1, f"Error: Action values should fall within the interval [0, {self.action_space_size-1}]."
        if self.pause == False and self.skip_step == False:   
            if self.player_score > self.opponent_score:
                assert self.done == False, "The game has ended. You win."
            elif self.opponent_score > self.player_score:
                assert self.done == False, "The game has ended. You lose."
            else:
                assert self.done == False, "The game has ended. Draw."
            if self.pause == False:
                self.state[self.bar_top:self.bar_top + self.bar_length, 1] = 0
                if self.bar_top + 1 - self.action > 0 and self.bar_top + 1 - self.action + self.bar_length - 1 < 159:
                    self.bar_top = self.bar_top + 1 - self.action  # 0:down, 1:no move, 2:up
                self.state[self.bar_top:self.bar_top + self.bar_length, 1] = 3
                self.state[self.opponent_bar_top:self.opponent_bar_top + self.bar_length, 208] = 0
                if self.ball_position[0] >= (208 - detect_range):
                    if self.ball_position[1] >= self.opponent_bar_top + (self.bar_length / 2 + 1) and self.opponent_bar_top + 1 + self.bar_length - 1 <= 158:
                        self.opponent_bar_top += 1  # go down
                    elif self.ball_position[1] <= self.opponent_bar_top + (self.bar_length / 2) and self.opponent_bar_top >= 1:
                        self.opponent_bar_top -= 1  # go up
                elif self.opponent_bar_top < 79 - self.bar_length // 2 + 1:
                    self.opponent_bar_top += 1
                elif self.opponent_bar_top > 79 - self.bar_length // 2 + 1:
                    self.opponent_bar_top -= 1
                self.state[self.opponent_bar_top:self.opponent_bar_top + self.bar_length, 208] = 2
                self.update_ball_position()
                if self.player_score == 21 or self.opponent_score == 21 or self.frame == self.frame_limit:
                    self.done = True
                self.frame += 1
                if self.render_ == 1:
                    self.render()
            info = {"player": self.player_score, "opponent": self.opponent_score}
            return self.state.reshape((1, 210, 160)), self.reward, self.done, info

    def update_ball_position(self):
        new_x = int(self.ball_position[0] + self.ball_speed * math.cos(self.ball_angle))
        new_y = int(self.ball_position[1] + self.ball_speed * math.sin(self.ball_angle))
        if 0 <= new_x <= 209 and 6 <= self.ball_position[0] <= 203:
            while new_y <= 0 or new_y >= 159 or (new_x <= 6 and self.bar_top <= new_y <= self.bar_top + self.bar_length - 1) or (new_x >= 203 and self.opponent_bar_top <= new_y <= self.opponent_bar_top + self.bar_length - 1):
                if new_y <= 0 or new_y >= 159:
                    self.ball_angle = math.pi * 2 - self.ball_angle
                elif (new_x <= 6 and self.bar_top <= new_y <= self.bar_top + self.bar_length - 1) or (new_x >= 203 and self.opponent_bar_top <= new_y <= self.opponent_bar_top + self.bar_length - 1):  # 板子打到球
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

        
        if self.pause == False:
            if self.hide_info == True:
                self.DISPLAY.fill((0, 0, 0))
                pygame.draw.circle(self.DISPLAY, (255, 255, 255), (self.ball_position[0], self.ball_position[1]), 4, 0)
                pygame.draw.rect(self.DISPLAY, (255, 255, 255), (1, self.bar_top, 5, self.bar_length))
                pygame.draw.rect(self.DISPLAY, (255, 255, 255), (204, self.opponent_bar_top, 5, self.bar_length))
            else:
                self.DISPLAY.fill((0, 0, 0))
                pygame.draw.circle(self.DISPLAY, (255, 255, 255), (self.ball_position[0], self.ball_position[1]), 4, 0)
                pygame.draw.rect(self.DISPLAY, (255, 255, 255), (1, self.bar_top, 5, self.bar_length))
                pygame.draw.rect(self.DISPLAY, (255, 255, 255), (204, self.opponent_bar_top, 5, self.bar_length))
                font = pygame.font.Font(None, 25)
                frame_text = font.render("Frame: {}".format(self.frame), True, (255, 255, 255))
                self.DISPLAY.blit(frame_text, (70, 140))
                frame_text = font.render("You: {}".format(self.player_score), True, (255, 255, 255))
                self.DISPLAY.blit(frame_text, (10, 10))
                frame_text = font.render("Opponent: {}".format(self.opponent_score), True, (255, 255, 255))
                self.DISPLAY.blit(frame_text, (10, 30))
                font = pygame.font.Font(None, 21)
                frame_text = font.render("(limit: {})".format(self.frame_limit), True, (255, 255, 255))
                self.DISPLAY.blit(frame_text, (65, 120))
        elif self.pause == True:
            self.DISPLAY.fill((0, 0, 0))
            title = pygame.font.Font(None, 30)
            frame_text = title.render("Rules", True, (255, 255, 255))
            self.DISPLAY.blit(frame_text, (5, 10))
            font = pygame.font.Font(None, 20)
            frame_text = font.render(
                "1.press enter to start or pause",
                True, (255, 255, 255))
            self.DISPLAY.blit(frame_text, (10, 35))
            frame_text = font.render(
                "2.press esc to close the game",
                True, (255, 255, 255))
            self.DISPLAY.blit(frame_text, (10, 55))
            frame_text = font.render(
                "3.press shift to hide the info",
                True, (255, 255, 255))
            self.DISPLAY.blit(frame_text, (10, 75))
            frame_text = font.render(
                "4.using up and down to move",
                True, (255, 255, 255))
            self.DISPLAY.blit(frame_text, (10, 95))
            frame_text = font.render(
                "  using space to stay stopped",
                True, (255, 255, 255))
            self.DISPLAY.blit(frame_text, (10, 115))
            frame_text = font.render(
                "5.you are left, get 21 to win!",
                True, (255, 255, 255))
            self.DISPLAY.blit(frame_text, (10, 135))



    def run_game(self):
        while True:
            if self.pause == False:
                self.step(4)
                print(self.hide_info)
                pygame.display.update()
                clock.tick(120)
                if self.stop_one_sec:
                    time.sleep(0.5)
                    

            else:
                key = keyboard.read_key()
                if key == "enter":
                    self.pause = False
                    self.render()
                    pygame.display.update()
                    clock.tick(120)
                    time.sleep(0.5)
                elif key == "esc":
                    sys.exit()
            


clock = pygame.time.Clock()
game = Game("human")
game.reset(1)
game.run_game()

