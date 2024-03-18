import random
class Game:
    def __init__(self, is_slippery):
        
        self.state = (0,0)
        self.is_slippery = is_slippery

    def reset(self):
        self.state = (0, 0)
        return self.state

    def step(self, action):
        assert 0 <= action <= 3, "Error: Action values should fall within the interval [0, 3]."
        self.action = random.randrange(action - self.is_slippery, action + self.is_slippery, self.is_slippery) 
        if self.actionaction == 0:
            self.state = (self.state[0] + 1, self.state[1])
        elif self.action == 1:
            self.state = (self.state[0], self.state[1] - 1)
        elif self.action == 2:
            self.state = (self.state[0] - 1, self.state[1])
        elif self.action == 3:
            self.state = (self.state[0], self.state[1] + 1) 
        return self.state
