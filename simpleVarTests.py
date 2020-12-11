import random
from nnf import Var
from lib204 import Encoding

if __name__ == "__main__":

    t = Var("hi", True)
    print(t.true)
    t.negate()
    print(t.true)

    s = Var("hi", False)
    print(s.true)
    #used incorrectly
    print(t.negate())