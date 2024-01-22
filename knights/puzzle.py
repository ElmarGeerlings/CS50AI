from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    Or(AKnight, AKnave),    # A is either a knight or a knave
    Not(And(AKnight, AKnave)),  # A is not both a knight and a knave at the same time
    Biconditional(And(AKnight, AKnave), AKnight)    # A is a knight if he speaks the truth
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    Or(AKnight, AKnave),    # A is either a knight or a knave
    Not(And(AKnight, AKnave)),  # A is not both a knight and a knave at the same time
    Or(BKnight, BKnave),    # B is either a knight or a knave
    Not(And(BKnight, BKnave)),  # B is not both a knight and a knave at the same time
    Biconditional(And(AKnave, BKnave), AKnight),  # A is a knight if he speaks the truth
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    Or(AKnight, AKnave),    # A is either a knight or a knave
    Not(And(AKnight, AKnave)),  # A is not both a knight and a knave at the same time
    Or(BKnight, BKnave),    # B is either a knight or a knave
    Not(And(BKnight, BKnave)),  # B is not both a knight and a knave at the same time
    Biconditional(Or(And(AKnight, BKnight), And(AKnave, BKnave)), AKnight),  # A is a knight if he speaks the truth
    Biconditional(Or(And(AKnight, BKnave), And(AKnave, BKnight)), BKnight),   # B is a knight if he speaks the truth
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Or(AKnight, AKnave),    # A is either a knight or a knave
    Not(And(AKnight, AKnave)),  # A is not both a knight and a knave at the same time
    Or(BKnight, BKnave),    # B is either a knight or a knave
    Not(And(BKnight, BKnave)),  # B is not both a knight and a knave at the same time
    Or(CKnight, CKnave),    # C is either a knight or a knave
    Not(And(CKnight, CKnave)),  # C is not both a knight and a knave at the same time   
    Biconditional(Or(Biconditional(AKnave, AKnight), Biconditional(Not(AKnave), AKnave)), BKnight), # B is a knight if he speaks the truth
    Biconditional(CKnave, BKnight), # B is a knight if he speaks the truth
    Biconditional(AKnight, CKnight) # C is a knight if he speaks the truth
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
