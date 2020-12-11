
import os, sys

from run import *

USAGE = '\n\tpython3 test.py [draft|final]\n'
EXPECTED_VAR_MIN = 10
EXPECTED_CONS_MIN = 50

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

def test_theory():

    state = GameState(1, 1, 0)

    roll = random_roll(3)

    T = move_from_roll(roll, state)

    assert len(T.vars()) > EXPECTED_VAR_MIN, "Only %d variables -- your theory is likely not sophisticated enough for the course project." % len(T.vars())
    assert T.size() > EXPECTED_CONS_MIN, "Only %d operators in the formula -- your theory is likely not sophisticated enough for the course project." % T.size()
    assert not T.valid(), "Theory is valid (every assignment is a solution). Something is likely wrong with the constraints."
    assert not T.negate().valid(), "Theory is inconsistent (no solutions exist). Something is likely wrong with the constraints."

def file_checks(stage):
    proofs_jp = os.path.isfile(os.path.join('.','documents',stage,'proofs.jp'))
    modelling_report_docx = os.path.isfile(os.path.join('.','documents',stage,'modelling_report.docx'))
    modelling_report_pptx = os.path.isfile(os.path.join('.','documents',stage,'modelling_report.pptx'))
    report_txt = os.path.isfile(os.path.join('.','documents',stage,'report.txt'))
    report_pdf = os.path.isfile(os.path.join('.','documents',stage,'report.pdf'))

    assert proofs_jp, "Missing proofs.jp in your %s folder." % stage
    assert modelling_report_docx or modelling_report_pptx or (report_txt and report_pdf), \
            "Missing your report (Word, PowerPoint, or OverLeaf) in your %s folder" % stage

def test_draft_files():
    file_checks('draft')

def test_final_files():
    file_checks('final')

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ['draft', 'final']:
        print(USAGE)
        #exit(1)
    test_theory()
    file_checks(sys.argv[1])
