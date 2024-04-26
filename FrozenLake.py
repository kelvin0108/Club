import random
import numpy as np

H = np.array([[1, 1], [3, 1], [3, 2], [0, 3]])
G = np.array([3, 3])
MAP = [
    "S", "F", "F", "F",
    "F", "H", "F", "H",
    "F", "F", "F", "H",
    "H", "F", "F", "G"
]


class Game:
    def __init__(self, is_slippery, max_step):
        assert is_slippery == 0 or is_slippery == 1, "Error: is_slippery values should fall within the interval [0, 1]."
        self.is_slippery = is_slippery
        self.action_space_size = 4
        self.max_step = max_step

    def reset(self):
        self.step_count = 0
        self.state = np.array([0, 0])
        self.reward = 0
        self.done = False
        return self.get_state()

    def step(self, action):
        assert 0 <= action <= self.action_space_size - 1, f"Error: Action values should fall within the interval [0, {self.action_space_size - 1}]."
        assert self.done == False, "The game has ended."
        self.step_count += 1
        self.action = random.randrange(action - self.is_slippery,
                                       action + self.is_slippery + 1, 1)
        old_state = self.state.copy()
        if self.action == 0 or self.action == 4:
            self.state[0] += 1
        elif self.action == 1:
            self.state[1] += 1
        elif self.action == 2:
            self.state[0] -= 1
        elif self.action == 3 or self.action == -1:
            self.state[1] -= 1
        if (self.state > np.array([3, 3])).any() or (self.state < np.array([0, 0])).any():
            self.state = old_state
        if (self.state == G).all():
            self.reward = 1
            self.done = True
        for i in range(4):
            if (self.state == H[i]).all():
                self.reward = 0
                self.done = True
        if self.step_count > self.max_step:
            self.reward = 0
            self.done = True

        return self.get_state(), self.done, self.reward

    def get_state(self):
        # state = np.zeros((1, 4, 4))
        # state[0][self.state[1]][self.state[0]] = 1
        state = np.zeros(16)
        state[4 * self.state[1] + self.state[0]] = 1
        return state

    def action_space(self):
        return np.arange(self.action_space_size)

    def sample_action(self):
        return np.random.choice(self.action_space(), 1).item()

    def show_map(self):
        MAP = [
            "F", "F", "F", "F",
            "F", "H", "F", "H",
            "F", "F", "F", "H",
            "H", "F", "F", "G"
        ]
        MAP[self.state[0] + self.state[1] * 4] = "\033[30m\033[42mP\033[0m"
        map = ""
        for i in range(0, len(MAP), 4):
            map += " ".join(MAP[i:i + 4]) + "\n"
        return map
