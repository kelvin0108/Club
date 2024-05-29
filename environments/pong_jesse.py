import math
import random

import numpy as np
import pygame
import torch
import sys


class Game:
    def __init__(self, game_mode="human", render=1, offset=1, net=None):
        self.offset = offset
        self.game_mode = game_mode
        self.render = render
        self.net = net

        pygame.init()
        self.clock = pygame.time.Clock()

        self.player_score = 0
        self.opponent_score = 0

        self.reset()
        if self.game_mode == "human" or self.game_mode == "human_ai":
            self.main_loop()

    def reset(self):
        self.reset_score()
        self.reset_game()

        state = (self.ball_x, self.ball_y, self.ball_dir, self.player_y)

        return state, {"player": self.player_score, "opponent": self.opponent_score}

    def reset_score(self):
        self.player_score = 0
        self.opponent_score = 0

    def reset_game(self):
        # Setup screen.
        self.screen_width = 210
        self.screen_height = 160
        if self.render == 1:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption("Pong")
        elif self.render == 0:
            self.screen = pygame.Surface((self.screen_width, self.screen_height))

        # Setup object.
        self.ball_x = self.screen_width / 2 - 4
        self.ball_y = self.screen_height / 2 - 4
        self.ball = pygame.Rect(self.ball_x, self.ball_y, 8, 8)

        self.pad_size = 40
        self.player_x = 20 - 4
        self.player_y = self.screen_height / 2 - self.pad_size / 2
        self.player = pygame.Rect(self.player_x, self.player_y, 8, self.pad_size)
        self.opponent_x = self.screen_width - 20 - 4
        self.opponent_y = self.screen_height / 2 - self.pad_size / 2
        self.opponent = pygame.Rect(self.opponent_x, self.opponent_y, 8, self.pad_size)

        # Setup movement.
        temp = random.randint(1, 4)
        self.ball_dir = random.uniform((math.pi * (3 * temp - 2)) / 6, (math.pi * (3 * temp - 1)) / 6)
        self.ball_speed = 1.5 / self.offset

        self.ball_xv = math.cos(self.ball_dir) * self.ball_speed
        self.ball_yv = math.sin(self.ball_dir) * self.ball_speed

        self.player_speed = 2 / self.offset
        if self.game_mode == "human_ai":
            self.opponent_speed = 2 / self.offset
        else:
            self.opponent_speed = 1.2 / self.offset

        self.up, self.down = False, False
        self.player_en, self.opponent_en = False, False

    def main_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.down = True
                    if event.key == pygame.K_UP:
                        self.up = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        self.down = False
                    if event.key == pygame.K_UP:
                        self.up = False

            # None: 0. Up: 1. Down: 2.
            if self.up and self.down:
                action = 0
            elif self.up:
                action = 1
            elif self.down:
                action = 2
            else:
                action = 0
            state, reward, done, info = self.step(action)
            if reward != 0:
                print(info)
            if done:
                self.reset()


    def step(self, action):
        reward = 0

        # Ball Logics.
        self.ball_x += self.ball_xv
        self.ball_y += self.ball_yv
        if self.ball_y + 8 > self.screen_height:
            self.ball_y = self.screen_height - 8
            self.ball_dir *= -1
        if self.ball_y < 0:
            self.ball_y = 0
            self.ball_dir *= -1

        player_coll = self.ball.colliderect(self.player)
        opponent_coll = self.ball.colliderect(self.opponent)

        if not player_coll:
            self.player_en = True
        if not opponent_coll:
            self.opponent_en = True

        if self.player_en and player_coll:
            self.ball_dir = math.radians(70 - random.random() * 140)
            self.ball_speed = 3 / self.offset
            self.player_en = False
        if self.opponent_en and opponent_coll:
            self.ball_dir = math.radians(110 + random.random() * 140)
            self.ball_speed = 3 / self.offset
            self.opponent_en = False

        self.ball.x = self.ball_x
        self.ball.y = self.ball_y
        self.ball_xv = math.cos(self.ball_dir) * self.ball_speed
        self.ball_yv = math.sin(self.ball_dir) * self.ball_speed

        # Player Logics.
        if self.game_mode == "human_ai":
            if action == 2:
                self.opponent_y += self.opponent_speed
            if action == 1:
                self.opponent_y -= self.opponent_speed
            if self.opponent_y < 0:
                self.opponent_y = 0
            if self.opponent_y + self.pad_size > self.screen_height:
                self.opponent_y = self.screen_height - self.pad_size

            self.opponent.y = self.opponent_y
        else:
            if action == 2:
                self.player_y += self.player_speed
            if action == 1:
                self.player_y -= self.player_speed
            if self.player_y < 0:
                self.player_y = 0
            if self.player_y + self.pad_size > self.screen_height:
                self.player_y = self.screen_height - self.pad_size

            self.player.y = self.player_y

        # AI Logics.
        if self.game_mode == "human_ai":
            act = self.net(torch.FloatTensor((self.ball_x, self.ball_y, self.ball_dir, self.player_y))).max(0)[1].item()
            if act == 2:
                self.player_y += self.player_speed
            if act == 1:
                self.player_y -= self.player_speed
            if self.player_y < 0:
                self.player_y = 0
            if self.player_y + self.pad_size > self.screen_height:
                self.player_y = self.screen_height - self.pad_size

            self.player.y = self.player_y
        else:
            if math.pow(self.opponent_x - self.ball.x, 2) + math.pow(self.opponent_y - self.ball.y, 2) < 10000:
                if abs((self.opponent_y + self.pad_size / 2) - (self.ball.y + 4)) > self.pad_size / 4:
                    if self.opponent_y + self.pad_size / 2 < self.ball.y + 4:
                        self.opponent_y += self.opponent_speed
                    else:
                        self.opponent_y -= self.opponent_speed
            if self.opponent_y < 0:
                self.opponent_y = 0
            if self.opponent_y + self.pad_size > self.screen_height:
                self.opponent_y = self.screen_height - self.pad_size

            self.opponent.y = self.opponent_y

        if self.render == 1:
            self.screen.fill((0, 0, 0))
            pygame.draw.rect(self.screen, (255, 255, 255), self.ball)
            pygame.draw.rect(self.screen, (255, 255, 255), self.player)
            pygame.draw.rect(self.screen, (255, 255, 255), self.opponent)

            pygame.display.flip()
            self.clock.tick(60 * self.offset)

        # Returns.
        done = False
        if self.ball_x + 8 > self.screen_width:
            if self.game_mode == "human_ai":
                self.opponent_score += 1
            else:
                self.player_score += 1
            reward = -1 if self.game_mode == "human_ai" else 1
            self.reset_game()
        if self.ball_x < 0:
            if self.game_mode == "human_ai":
                self.player_score += 1
            else:
                self.opponent_score += 1
            reward = 1 if self.game_mode == "human_ai" else -1
            self.reset_game()

        info = {"player": self.player_score, "opponent": self.opponent_score}
        if self.player_score >= 20 or self.opponent_score >= 20:
            done = True

        state = (self.ball_x, self.ball_y, self.ball_dir, self.player_y)

        return state, reward, done, info

    def action_space(self):
        return 3

    def sample_action(self):
        return random.randint(0, self.action_space() - 1)


if __name__ == "__main__":
    game = Game(game_mode="human", render=1)
    game.reset()