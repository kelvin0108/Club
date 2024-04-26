from environments import frozen_lake

game = frozen_lake.Game(1, 150)
state = game.reset()

while True:
    print(state)
    print(game.show_map())
    action = int(input("action: "))
    state, _, _ = game.step(action)
