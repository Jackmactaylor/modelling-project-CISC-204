import random
from nnf import Var
from lib204 import Encoding

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


# Returns a new GameState object with the parameters of the state after the given roll
def process_turn(prev_state, roll):
    # Variables are initialized to 0 for now to make sure the string parsing below works for yielding an int
    new_x = 0
    new_y = 0
    next_turn = 0

    # move from roll encoding processing #
    next_model = move_from_roll(roll, prev_state)

    # Gets the next x and y positions from the model that satisfied the prev_state + roll
    for var in next_model:
        if var[0] == 'y':
            if next_model[var]:
                new_y = int(var[1])
        if var[0] == 'x':
            if next_model[var]:
                new_x = int(var[1])

    # Game over encoding processing #
    win, loss = check_game_over(prev_state)

    for turn in prev_state.turns:
        if turn.true:
            next_turn = int(turn.name[4]) + 1

    next_state = GameState(new_x, new_y, next_turn, win, loss)
    return next_state


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

    return next_pos.solve()


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


# returns number of turns remaining
def get_remaining_turns(state):
    for turn in state.turns:
        if turn.true:
            this_turn = int(turn.name[4])
    return (3 - this_turn)


# prints one player board to console
# Board dimensions are based on num_squares_x and num_squares_y
# Can print snake and ladder in different position if given different default parameters
def print1pBoard(x, y, x_ladder_pos=3, y_ladder_bottom=2, y_ladder_top=1, x_snake_pos=2, y_snake_bottom=2, y_snake_top=1):
    y_pos = False
    x_pos = False
    forward_slash = True
    pos_printed = False
    for i in range(num_squares_x):
        print("========", end="")
    for j in range(num_squares_y):
        if (num_squares_y - j == y):
            y_pos = True
        print()
        for k in range(num_squares_x + 1):
            if (k + 1 == x_ladder_pos and j + 1 <= y_ladder_bottom and j + 1 > y_ladder_top):
                print("|  |_|  ", end="")
            elif (k + 1 == x_snake_pos and j + 1 <= y_snake_bottom and j + 1 > y_snake_top and forward_slash):
                print("|   /   ", end="")
                forward_slash = False
            elif (k + 1 == x_snake_pos and j + 1 <= y_snake_bottom and j + 1 > y_snake_top and forward_slash == False):
                print("|   \   ", end="")
                forward_slash = True
            else:
                print("|       ", end="")
        print()
        for k in range(num_squares_x + 1):
            if (k + 1 == x):
                x_pos = True
            if (x_pos and y_pos and pos_printed == False):
                print("|   P   ", end="")
                pos_printed = True
            elif (k + 1 == x_ladder_pos and j + 1 >= y_ladder_top and j + 1 <= y_ladder_bottom):
                print("|  |_|  ", end="")
            elif (k + 1 == x_snake_pos and j + 1 >= y_snake_top and j + 1 <= y_snake_bottom and forward_slash):
                print("|   /   ", end="")
                forward_slash = False
            elif (k + 1 == x_snake_pos and j + 1 >= y_snake_top and j + 1 <= y_snake_bottom and forward_slash == False):
                print("|   \   ", end="")
                forward_slash = True
            else:
                print("|       ", end="")
        print()
        x_pos = False
        for k in range(num_squares_x + 1):
            if (k + 1 == x_ladder_pos and j + 1 >= y_ladder_top and j + 1 < y_ladder_bottom):
                print("|  |_|  ", end="")
            elif (k + 1 == x_snake_pos and j + 1 >= y_snake_top and j + 1 < y_snake_bottom and forward_slash):
                print("|   /   ", end="")
                forward_slash = False
            elif (k + 1 == x_snake_pos and j + 1 >= y_snake_top and j + 1 < y_snake_bottom and forward_slash == False):
                print("|   \   ", end="")
                forward_slash = True
            else:
                print("|       ", end="")
        print()
        for a in range(num_squares_x):
            print("========", end="")
        y_pos = False
    print()


# prints two player board to console
# Board dimensions are based on num_squares_x and num_squares_y
# Can print snake and ladder in different position if given different default parameters
def print2pBoard(x1, y1, x2, y2, x_ladder_pos=3, y_ladder_bottom=2, y_ladder_top=1, x_snake_pos=2, y_snake_bottom=2, y_snake_top=1):
    y1_pos = False
    x1_pos = False
    y2_pos = False
    x2_pos = False
    forward_slash = True
    pos1_printed = False
    pos2_printed = False

    for i in range(num_squares_x):
        print("========", end="")
    for j in range(num_squares_y):
        if (num_squares_y - j == y1):
            y1_pos = True
        if (num_squares_y - j == y2):
            y2_pos = True

        print()
        for k in range(num_squares_x + 1):
            if (k + 1 == x_ladder_pos and j + 1 <= y_ladder_bottom and j + 1 > y_ladder_top):
                print("|  |_|  ", end="")
            elif (k + 1 == x_snake_pos and j + 1 <= y_snake_bottom and j + 1 > y_snake_top and forward_slash):
                print("|   /   ", end="")
                forward_slash = False
            elif (k + 1 == x_snake_pos and j + 1 <= y_snake_bottom and j + 1 > y_snake_top and forward_slash == False):
                print("|   \   ", end="")
                forward_slash = True
            else:
                print("|       ", end="")
        print()
        for k in range(num_squares_x + 1):
            if (k + 1 == x1):
                x1_pos = True
            if (k + 1 == x2):
                x2_pos = True

            if (x1_pos and y1_pos and pos1_printed == False and x2_pos and y2_pos and pos2_printed == False):
                print("| P1 P2 ", end="")
                pos1_printed = True
                pos2_printed = True
            elif (x1_pos and y1_pos and pos1_printed == False):
                print("|   P1  ", end="")
                pos1_printed = True
            elif (x2_pos and y2_pos and pos2_printed == False):
                print("|   P2  ", end="")
                pos2_printed = True
            elif (k + 1 == x_ladder_pos and j + 1 >= y_ladder_top and j + 1 <= y_ladder_bottom):
                print("|  |_|  ", end="")
            elif (k + 1 == x_snake_pos and j + 1 >= y_snake_top and j + 1 <= y_snake_bottom and forward_slash):
                print("|   /   ", end="")
                forward_slash = False
            elif (k + 1 == x_snake_pos and j + 1 >= y_snake_top and j + 1 <= y_snake_bottom and forward_slash == False):
                print("|   \   ", end="")
                forward_slash = True
            else:
                print("|       ", end="")
        print()
        x1_pos = False
        x2_pos = False
        for k in range(num_squares_x + 1):
            if (k + 1 == x_ladder_pos and j + 1 >= y_ladder_top and j + 1 < y_ladder_bottom):
                print("|  |_|  ", end="")
            elif (k + 1 == x_snake_pos and j + 1 >= y_snake_top and j + 1 < y_snake_bottom and forward_slash):
                print("|   /   ", end="")
                forward_slash = False
            elif (k + 1 == x_snake_pos and j + 1 >= y_snake_top and j + 1 < y_snake_bottom and forward_slash == False):
                print("|   \   ", end="")
                forward_slash = True
            else:
                print("|       ", end="")
        print()
        for a in range(num_squares_x):
            print("========", end="")
        y1_pos = False
        y2_pos = False
    print()


# generates random roll number
def random_roll(n):
    return random.randint(1, n)


# prints game rules to console
def print_rules():
    print("===================================================================================================")
    print("\nThis is a brief guide to how to play our snakes and ladders game\n")
    print("General Gameplay")
    print("The game contains a 2x4 board with one snake and one ladder, as seen below:")
    print1pBoard(1, 1)
    print("The player will press enter to roll the dice and move through the board")
    print("The player will start moving to the right, then up, and finally to the left.")
    print("The player wins when they land exactly on the top left position.")
    print("If the player is two spaces away from the last square and rolls a three\nthey will move two spaces forward and one space backward, without winning.")
    print("If the player lands on the bottom of a ladder they will climb up it,\nhowever, if they land on the top of a snake they will slide down it.")

    print("\nGame Modes")
    print("There are two different game modes, solo and 1v1")
    print("In solo, the one player has three turns to get to the last square and win.")
    print("If they don't make it to the last square in three turns or less they lose.\n")

    print("In 1v1 there are no turn limits, instead each player takes a turn until one player reaches the last square")
    print("The first player to reach the final square wins.")

    input("\nPress enter to return to the main menu.")


# runs the game and handles user input
def main():
    valid_input = False
    game_over = False
    solo = False
    multiplayer = False

    print("\nWelcome to Snakes and Ladders!")

    # while loop to find out what user wants to do
    while (valid_input == False):
        answer = input("\nPlease select one of the following options: play a game [1], read rules [2], exit game [3]: ")
        if (answer == "1"):
            valid_input = True
        elif (answer == "2"):
            print_rules()
        elif (answer == "3"):
            print("Thanks for playing")
            exit()
        else:
            print("invalid input, please enter either 1, 2 or 3.\n")

    valid_input = False
    # while loop to get number of players (1 or 2)
    while (valid_input == False):

        answer = input("How many people are playing the game? [1/2]: ")
        if (answer == "1"):
            valid_input = True
            solo = True
            print("Here is the starting state of the board: \n")
            print1pBoard(1, 1)
        elif (answer == "2"):
            valid_input = True
            multiplayer = True
            print("Here is the starting state of the board: \n")
            print2pBoard(1, 1, 1, 1)
        else:
            print("invalid input, please enter either 1 or 2.\n")

    # Code for one player game
    if(solo):
        state = GameState(1, 1, 0)
        while (game_over == False):

            print("==============================================================")

            # print number of turns remaining
            print("You have " + str(get_remaining_turns(state)) + " turns remaining")

            input("\nPress Enter to roll the dice, the dice can roll a 1, 2, or 3")

            roll = random_roll(3)

            print("\nYou rolled a " + str(roll))

            # set new state using dice roll
            state = process_turn(state, roll)

            new_x, new_y = get_current_square(state)

            print("The Current board can be seen below:")

            # print new board
            print1pBoard(new_x + 1, new_y + 1)

            win, lost = check_game_over(state)

            # check if player won or lost
            if(win == True):
                print("Congratulations you won")
                game_over = True
            elif(lost == True):
                print("Sorry you ran out of turns")
                game_over = True

    
    # Code for two player game
    if(multiplayer):
        p1state = GameState(1, 1, 0)
        p2state = GameState(1, 1, 0)

        p1Turn = True
        p2Turn = False

        while (game_over == False):

            print("==============================================================")

            if(p1Turn):
                print("It is now P1's turn")
            elif(p2Turn):
                print("It is now P2's turn")

            input("\nPress Enter to roll the dice, the dice can roll a 1, 2, or 3")

            roll = random_roll(3)

            if(p1Turn):
                print("\nP1 rolled a " + str(roll))
            elif(p2Turn):
                print("\nP2 rolled a " + str(roll))

            # update state using dice roll
            if(p1Turn):
                p1state = process_turn(p1state, roll)
            elif(p2Turn):
                p2state = process_turn(p2state, roll)

            p1x, p1y = get_current_square(p1state)
            p2x, p2y = get_current_square(p2state)

            print("The Current board can be seen below:")

            # print new board
            print2pBoard(p1x + 1, p1y + 1, p2x + 1, p2y + 1)

            # change player turns
            p1Turn = not p1Turn
            p2Turn = not p2Turn

            p1_win, p1_lost = check_game_over(p1state)
            p2_win, p2_lost = check_game_over(p2state)

            # check if a player won
            if(p1_win == True):
                print("P1 won the game")
                game_over = True
            elif(p2_win == True):
                print("P2 won the game")
                game_over = True


    valid_input = False
    # while loop to check if user wants to play again or exit
    while(valid_input == False):
        answer = input("would you like to return to the main menu? [y/n]: ")
        if (answer == "y"):
            valid_input = True
            print("====================================================")
            main()
            exit()
        elif (answer == "n"):
            valid_input = True
            print("Thanks for playing.")
            exit()
        else:
            print("invalid input, please type the letter y or n.\n")


if __name__ == "__main__":
    main()
