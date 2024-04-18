import random
import numpy as np
class Game:
    def __init__(self, game_mode):
        self.game_mode = game_mode
        self.action_space_size = 3
        
    def reset(self):
        self.state = np.zeros([210, 160])
        self.state[0,:] = 4
        self.state[0,:] = 5
        self.state[1,100:111] = 3
        self.state[158,100:111] = 2
        self.reward = 0
        self.done = False
        self.frame = 0
    
    def step(self, action):
        self.action = action
        assert 0 <= action <= self.action_space_size-1, f"Error: Action values should fall within the interval [0, {self.action_space_size-1}]."
        assert self.done == False, "The game has ended."

    
    def action_space(self):
        return np.arange(self.action_space_size)

    def sample_action(self):
        return np.random.choice(self.action_space(), 1).item()

