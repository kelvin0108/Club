class Game:
    def __init__(self, action):
        self.action = action
        self.state = (0,0)

    def reset(self):
        self.state = (0, 0)
        return self.state

    def step(self):
        if 0 <= self.action <= 3 and (0, 0) <= self.state <= (4, 4):
            if self.action == 0:
                self.state = (self.state[0] + 1, self.state[1])
            elif self.action == 1:
                self.state = (self.state[0], self.state[1] - 1)
            elif self.action == 2:
                self.state = (self.state[0] - 1, self.state[1])
            elif self.action == 3:
                self.state = (self.state[0], self.state[1] + 1)
        return self.state
