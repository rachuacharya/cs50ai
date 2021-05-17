from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A person can be knight or a knave but not both
# if a person is knight, what he is saying is true and vice-versa
# if a person in a knave, what he is saying is false and vice-versa

# A says "I am both a knight and a knave."
Asays0 = And(AKnave, AKnight)

# Knowledge base for puzzle0
knowledge0 = And(
    Biconditional(AKnight,Not(AKnave)),
    Or(Biconditional(Asays0, AKnight),
        Biconditional(Not(Asays0), AKnave))
)

# Puzzle 1
# A says "We are both knaves."
Asays1 = And(AKnave, BKnave)

# B says nothing.

# Knowledge base for puzzle 1
knowledge1 = And(
    Biconditional(AKnight,Not(AKnave)),
    Biconditional(BKnight, Not(BKnave)),
    Or(Biconditional(Asays1, AKnight),
        Biconditional(Not(Asays1), AKnave))
    
)

# Puzzle 2

# A says "We are the same kind."
Asays2 = Or(And(AKnave, BKnave), And(AKnight, BKnight))

# B says "We are of different kinds."
Bsays2 = Or(And(AKnave, BKnight), And(AKnight, BKnave))

# Knowledge base for puzzle 2
knowledge2 = And(
    Biconditional(AKnight,Not(AKnave)),
    Biconditional(BKnight, Not(BKnave)),
    Or(Biconditional(Asays2, AKnight),
        Biconditional(Not(Asays2), AKnave)),
    Or(Biconditional(Bsays2, BKnight),
        Biconditional(Not(Bsays2), BKnave))
)



# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
Asays3 = Or(AKnave, AKnight)

# B says "A said 'I am a knave'."
# B says "C is a knave."
Bsays3 = Or(Biconditional(AKnight, AKnave),
             Biconditional(AKnave, Not(AKnave)))
Bsays4 = CKnave

# C says "A is a knight."
Csays3 = AKnight

# Knowledge base for Puzzle 3
knowledge3 = And(
    Biconditional(AKnight, Not(AKnave)), 
    Biconditional(BKnight, Not(BKnave)), 
    Biconditional(CKnight, Not(CKnave)), 
    Or(Biconditional(Asays3, AKnight),
        Biconditional(Not(Asays3), AKnave)),
    Or(Biconditional(Bsays3, BKnight),
        Biconditional(Not(Bsays3), BKnave)),
    Or(Biconditional(BKnight, Bsays4),
        Biconditional(BKnave, Not(Bsays4))),
    Or(Biconditional(Csays3, CKnight),
        Biconditional(Not(Csays3), CKnave)))

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
