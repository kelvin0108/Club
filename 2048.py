import numpy as np
import random
import pygame
import sys
class Game:
    def __init__(self, game_mode="human", render=1, width=4, height=4):
        self.game_mode = game_mode
        self.render = render
        self.width = width
        self.height = height
        self.right = False
        self.left = False
        self.up = False
        self.down = False
        if render == 1:
            pygame.init()
            self.clock = pygame.time.Clock()
            self.screen_width = 300
            self.screen_height = 300
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption("2048") 
            self.main_loop()       
    def reset(self):
        self.state = np.zeros((self.width, self.height))
        self.state[(random.randrange(0, 4, 1),random.randrange(0, 4, 1))] = 2
        self.done = False
        self.checked = False
        self.total_score = 0
        self.current_score = 0
        self.previous_score = 0
        self.reward = 0
        self.up, self.right, self.down, self.left = False, False, False, False
        return self.state, self.done, self.reward, {"score":self.total_score}
    
    def step(self, action):
        assert 0 <= action <= 3, "Error: Action values should fall within the interval [0, 3]"
        if not any(self.check_move(act) for act in range(4)):
            self.done = True            
        assert self.done == False, "The game has ended."
        self.previous_score = self.current_score
        self.current_score = 0
        self.reward = 0
        merged = False
        moved = False
        if action == 0: #right
            for i_h in range(self.height):
                for i_w in range(self.width-1):
                    for i in range(i_w+1):
                        if self.state[i_h, self.width-i_w-1+i] == 0 :
                            self.state[i_h, self.width-i_w-1+i] = self.state[i_h, self.width-i_w-2+i]
                            self.state[i_h, self.width-i_w-2+i] = 0
                            moved = True
                        elif self.state[i_h, self.width-i_w-1+i] == self.state[i_h, self.width-i_w-2+i] and merged == False:
                            self.current_score += self.state[i_h, self.width-i_w-1+i]
                            self.state[i_h, self.width-i_w-1+i] += self.state[i_h, self.width-i_w-2+i]
                            self.state[i_h, self.width-i_w-2+i] = 0
                            merged = True
                            moved = True
        if action == 1: #down
            for i_w in range(self.width):
                for i_h in range(self.height-1):
                    for i in range(i_h+1):
                        if self.state[self.height-i_h-1+i, i_w] == 0 :
                            self.state[self.height-i_h-1+i, i_w] = self.state[self.height-i_h-2+i, i_w]
                            self.state[self.height-i_h-2+i, i_w] = 0
                            moved = True
                        elif self.state[self.height-i_h-1+i, i_w] == self.state[self.height-i_h-2+i, i_w] and merged == False:
                            self.current_score += self.state[self.height-i_h-1+i, i_w]
                            self.state[self.height-i_h-1+i, i_w] += self.state[self.height-i_h-2+i, i_w]
                            self.state[self.height-i_h-2+i, i_w] = 0
                            merged = True
                            moved = True
        if action == 2: #left
            for i_h in range(self.height):
                for i_w in range(self.width-1):
                    for i in range(i_w+1):
                        if self.state[i_h, i_w-i] == 0 :
                            self.state[i_h, i_w-i] = self.state[i_h, i_w-i+1]
                            self.state[i_h, i_w-i+1] = 0
                            moved = True
                        elif self.state[i_h, i_w-i] == self.state[i_h, i_w-i+1] and merged == False:
                            self.current_score += self.state[i_h, i_w-i]
                            self.state[i_h, i_w-i] += self.state[i_h, i_w-i+1]
                            self.state[i_h, i_w-i+1] = 0
                            merged = True
                            moved = True
        if action == 3: #up
            for i_w in range(self.width):
                for i_h in range(self.height-1):
                    for i in range(i_h+1):
                        if self.state[i_h-i, i_w] == 0 :
                            self.state[i_h-i, i_w] = self.state[i_h-i+1, i_w]
                            self.state[i_h-i+1, i_w] = 0
                            moved = True
                        elif self.state[i_h-i, i_w] == self.state[i_h-i+1, i_w] and merged == False:
                            self.current_score += self.state[i_h-i, i_w]
                            self.state[i_h-i, i_w] += self.state[i_h-i+1, i_w]
                            self.state[i_h-i+1, i_w] = 0
                            merged = True
                            moved = True                                                   

        if moved == True:
            zero_positions = np.argwhere(self.state == 0)
            if zero_positions.size > 0:
                random_index = np.random.choice(len(zero_positions))
                random_position = zero_positions[random_index]    
                self.state[random_position[0], random_position[1]] = 2
        
        self.total_score += self.current_score
        self.reward = self.current_score - self.previous_score
        info = {"score":self.total_score}
        return self.state, self.done, self.reward, info
    

    def check_move(self, action):
        moved = False
        merged = False
        temp_state = self.state.copy()
        if action == 0: #right
            for i_h in range(self.height):
                for i_w in range(self.width-1):
                    for i in range(i_w+1):
                        if self.state[i_h, self.width-i_w-1+i] == 0 :
                            self.state[i_h, self.width-i_w-1+i] = self.state[i_h, self.width-i_w-2+i]
                            self.state[i_h, self.width-i_w-2+i] = 0
                            moved = True
                        elif self.state[i_h, self.width-i_w-1+i] == self.state[i_h, self.width-i_w-2+i] and merged == False:
                            self.state[i_h, self.width-i_w-1+i] += self.state[i_h, self.width-i_w-2+i]
                            self.state[i_h, self.width-i_w-2+i] = 0
                            merged = True
                            moved = True
        if action == 1: #down
            for i_w in range(self.width):
                for i_h in range(self.height-1):
                    for i in range(i_h+1):
                        if self.state[self.height-i_h-1+i, i_w] == 0 :
                            self.state[self.height-i_h-1+i, i_w] = self.state[self.height-i_h-2+i, i_w]
                            self.state[self.height-i_h-2+i, i_w] = 0
                            moved = True
                        elif self.state[self.height-i_h-1+i, i_w] == self.state[self.height-i_h-2+i, i_w] and merged == False:
                            self.state[self.height-i_h-1+i, i_w] += self.state[self.height-i_h-2+i, i_w]
                            self.state[self.height-i_h-2+i, i_w] = 0
                            merged = True
                            moved = True
        if action == 2: #left
            for i_h in range(self.height):
                for i_w in range(self.width-1):
                    for i in range(i_w+1):
                        if self.state[i_h, i_w-i] == 0 :
                            self.state[i_h, i_w-i] = self.state[i_h, i_w-i+1]
                            self.state[i_h, i_w-i+1] = 0
                            moved = True
                        elif self.state[i_h, i_w-i] == self.state[i_h, i_w-i+1] and merged == False:
                            self.state[i_h, i_w-i] += self.state[i_h, i_w-i+1]
                            self.state[i_h, i_w-i+1] = 0
                            merged = True
                            moved = True
        if action == 3: #up
            for i_w in range(self.width):
                for i_h in range(self.height-1):
                    for i in range(i_h+1):
                        if self.state[i_h-i, i_w] == 0 :
                            self.state[i_h-i, i_w] = self.state[i_h-i+1, i_w]
                            self.state[i_h-i+1, i_w] = 0
                            moved = True
                        elif self.state[i_h-i, i_w] == self.state[i_h-i+1, i_w] and merged == False:
                            self.state[i_h-i, i_w] += self.state[i_h-i+1, i_w]
                            self.state[i_h-i+1, i_w] = 0
                            merged = True
                            moved = True
        self.state = temp_state.copy()
        return moved
    def render(self):
        square_size = min(self.screen_width, self.screen_height) // max(self.width, self.height)
        for x in range(0, self.screen_width, square_size):
            pygame.draw.line(self.screen, (200, 200, 200), (x, 0), (x, self.screen_height))
        for y in range(0, self.screen_height, square_size):
            pygame.draw.line(self.screen, (200, 200, 200), (0, y), (self.screen_width, y))
        pygame.display.flip()
        self.clock.tick(60)

    def main_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.down = True
                    elif event.key == pygame.K_UP:
                        self.up = True
                    elif event.key == pygame.K_LEFT:
                        self.left = True
                    elif event.key == pygame.K_RIGHT:
                        self.right = True
                if self.right:
                    action = 0
                elif self.down:
                    action = 1
                elif self.left:
                    action = 2
                elif self.up:
                    action = 3
                self.state, self.done, self.reward, info = self.step(action)
                if self.done:
                    self.reset() 
                


game = Game()
print(game.reset())

