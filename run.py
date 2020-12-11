import random
from nnf import Var
from lib204 import Encoding

# RUN main.py TO SEE PROGRAM IMPLEMENTATION

# This file shows a sample encoding solution for the player position after a random from the starting position, square 1,1
# This should produce only one solution since there should only be one place for the player to move after a dice roll
# We created a few other encoding which can be seen in main.py


# Key parameters for the game
# Game only currently works completely for these defined values
num_squares_x = 4
num_squares_y = 2
num_turns = 3


# used to construct a new GameState every turn as Vars are imutable, and can only have their boolean value set once
class GameState:

    # self = this GameState instance,
    # x_pos = int for index in x_positions of current x position,
    # y_pos = int for index in y_positions of current y position,
    # turn_num = int to indicate turn number
    # win = bool true if won, false else
    # loss = bool true if loss, false else
    def __init__(self, x_pos, y_pos, turn_num, win=False, loss=False):
        # We can generalize the board size by initializing and setting x positions with a loop.
        # Obviously this will only work if we can also generalize the constraints but I'm doing this because it doesn't
        # affect execution and it will save us time later if we want to take it that direction.
        self.x_positions = []
        self.y_positions = []
        self.turns = []
        for i in range(1, num_squares_x + 1):
            if i == x_pos:
                self.x_positions.append(Var('x' + i.__str__(), True))
            else:
                self.x_positions.append(Var('x' + i.__str__(), False))
        # Initialize and set y
        for i in range(1, num_squares_y + 1):
            if i == y_pos:
                self.y_positions.append(Var('y' + i.__str__(), True))
            else:
                self.y_positions.append(Var('y' + i.__str__(), False))
        # Initialize and set turns
        for i in range(0, num_turns + 1):
            if i == turn_num:
                self.turns.append(Var('turn' + i.__str__(), True))
            else:
                self.turns.append(Var('turn' + i.__str__(), False))

        self.win = Var('win', False)
        self.loss = Var('loss', False)

# returns win as true and loss as false if player wins, loss as true and win as false if player loses or both win and loss as false otherwise
def check_game_over(state):

    xvar = Var("xvar")
    yvar = Var("yvar")
    win = Var("win")

    turn0 = Var("turn0")
    turn1 = Var("turn1")
    turn2 = Var("turn2")
    turn3 = Var("turn3")
    loss = Var("loss")

    # default value for turn, used mainly in two player game
    this_turn = 0


    # encoding for player winning
    winner = Encoding()
    winner.add_constraint((xvar & yvar & win) | ((~xvar | ~yvar) & ~win))


    x, y = get_current_square(state)

    if(x == 0):
        winner.add_constraint(xvar)
    else:
        winner.add_constraint(~xvar)

    if(y == 1):
        winner.add_constraint(yvar)
    else:
        winner.add_constraint(~yvar)


    # encoding for player losing
    lost = Encoding()
    lost.add_constraint((turn0 & ~turn1 & ~turn2 & ~turn3 & ~loss) | (~turn0 & ~turn1 & ~turn2 & turn3 & loss) | (~turn0 & ~turn1 & turn2 & ~turn3 & ~loss) | (~turn0 & turn1 & ~turn2 & ~turn3 & ~loss))

    # get current turn number
    for turn in state.turns:
        if turn.true:
            this_turn = int(turn.name[4])

    if (this_turn == 0):
        lost.add_constraint(turn0)
    elif (this_turn == 1):
        lost.add_constraint(turn1)
    elif (this_turn == 2):
        lost.add_constraint(turn2)
    elif (this_turn == 3):
        lost.add_constraint(turn3)


    return winner.solve()["win"], lost.solve()["loss"]


# returns and int Tuple x,y representing the indices of the current True position
def get_current_square(state):
    for i in range(num_squares_x):
        # finds the one true x position
        if state.x_positions[i].true:
            x = i
    for i in range(num_squares_y):
        # finds the one true y position
        if state.y_positions[i].true:
            y = i
    return x, y


# calculates the next position of the player using the previous state and the roll value
def move_from_roll(roll, prev_state):
    next_pos = Encoding()
    x, y = get_current_square(prev_state)

    x_pos = [Var("x1"), Var("x2"), Var("x3"), Var("x4")]
    y_pos = [Var("y1"), Var("y2")]

    next_pos.add_constraint(
        (x_pos[0] & ~x_pos[1] & ~x_pos[2] & ~x_pos[3]) | (~x_pos[0] & x_pos[1] & ~x_pos[2] & ~x_pos[3]) | (
                    ~x_pos[0] & ~x_pos[1] & x_pos[2] & ~x_pos[3]) | (~x_pos[0] & ~x_pos[1] & ~x_pos[2] & x_pos[3]))
    next_pos.add_constraint((y_pos[0] & ~y_pos[1]) | (~y_pos[0] & y_pos[1]))

    if x == 0:
        # constraints that apply when on x1
        if y == 0:
            if roll == 1:
                next_pos.add_constraint(x_pos[1] & y_pos[0])
            if roll == 2:
                next_pos.add_constraint(x_pos[2] & y_pos[1])
            if roll == 3:
                next_pos.add_constraint(x_pos[3] & y_pos[0])

    if (x == 1):
        # constraints that apply when on x2
        if (y == 0):
            if (roll == 1):
                next_pos.add_constraint(x_pos[2] & y_pos[1])
            if (roll == 2):
                next_pos.add_constraint(x_pos[3] & y_pos[0])
            if (roll == 3):
                next_pos.add_constraint(x_pos[3] & y_pos[1])

    if (x == 2):
        # constraints that apply when on x3
        if (y == 1):
            if (roll == 1):
                next_pos.add_constraint(x_pos[1] & y_pos[0])
            if (roll == 2):
                next_pos.add_constraint(x_pos[0] & y_pos[1])
            if (roll == 3):
                next_pos.add_constraint(x_pos[1] & y_pos[0])

    if (x == 3):
        # constraints that apply when on x4
        if (y == 0):
            if (roll == 1):
                next_pos.add_constraint(x_pos[3] & y_pos[1])
            if (roll == 2):
                next_pos.add_constraint(x_pos[2] & y_pos[1])
            if (roll == 3):
                next_pos.add_constraint(x_pos[1] & y_pos[0])
        elif (y == 1):
            if (roll == 1):
                next_pos.add_constraint(x_pos[2] & y_pos[1])
            if (roll == 2):
                next_pos.add_constraint(x_pos[1] & y_pos[0])
            if (roll == 3):
                next_pos.add_constraint(x_pos[0] & y_pos[1])

    return next_pos


# generates random roll number
def random_roll(n):
    return random.randint(1, n)


if __name__ == "__main__":

    state = GameState(1, 1, 0)

    roll = random_roll(3)

    T = move_from_roll(roll, state)

    print("If you roll a " + str(roll) + " from positions 1,1 the encoding produces the following result:")

    print("\nSatisfiable: %s" % T.is_satisfiable())
    print("# Solutions: %d" % T.count_solutions())
    print("   Solution: %s" % T.solve())

    print()
