import numpy as np
import random
class Game:
    def __init__(self, game_mode="human", render=1, width=4, height=4):
        self.game_mode = game_mode
        self.render = render
        self.width = width
        self.height = height
        
    def reset(self):
        self.state = np.zeros((self.width, self.height))
        self.state[(random.randrange(0, 4, 1),random.randrange(0, 4, 1))] = 2
        return self.state
    
    def step(self, action):
        assert 0 <= action <= 3, "Error: Action values should fall within the interval [0, 3]"
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

        if moved == True:
            zero_positions = np.argwhere(self.state == 0)
            if zero_positions.size > 0:
                random_index = np.random.choice(len(zero_positions))
                random_position = zero_positions[random_index]    
                self.state[random_position[0], random_position[1]] = 2
            
                    
        return self.state 
    



