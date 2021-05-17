import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | VP | S Conj S
NP -> N | Det NP| Adj NP | P NP | Adv NP | Conj NP| N Adv | N NP
VP -> V | V NP | Adv VP | V Adv
"""
# S can be a simple sentence with subject and a verb, e.g Holmes smiled.
# S can be just a verb phrase, e.g. never walked
# S can be a combination of two simpler sentences joined using Conj
# Det NP e.g The door 
# Adj NP e.g dreadful mess
# P NP e.g at the door
# NP Adv e.g "... door here"
# Conj NP e.g "(she) and Holmes"
# N NP e.g Holmes and the small pipe
# V NP "... came at the door"
# Adv VP e.g "never came"
# VP Adv e.g "sat here"

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # Tokenize the sentences into individual words
    ngrams = nltk.word_tokenize(sentence)
    words = []

    # Iterate throught the words to check if they contain alphabets
    for gram in ngrams:

        contains_alphabet = False
        
        for letter in gram:
            
            # If any one of the letter/character is an alphabet
            if letter.isalpha():
                contains_alphabet = True
                break

        if contains_alphabet:
            words.append(gram.lower())

    return words

def contains_NP(subtree):

    # Check recursively if any branches contain NP node  
    # if the root node is NP
    if subtree.label() == "NP":
        return True

    # If only on subtree exits which isn't a sentence  
    if len(subtree) == 1 and subtree.label not in ["NP", "VP", "S"]:
        return False

    # Iterate recursively through subsubtrees checking for NP 
    for subsub in subtree:
        if contains_NP(subsub):
            return True

    return False

def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    chunks = []

    # Iterate through subtrees to store all the NP chunks 
    for subtree in tree:

        if not contains_NP(subtree):
            continue

        subsubtrees = np_chunk(subtree)

        for subsubtree in subsubtrees:

            chunks.append(subsubtree)
        
    # If terminal node with label NP
    if tree.label() == "NP" and not contains_NP(subtree):

        chunks.append(tree)

    return chunks
    

if __name__ == "__main__":
    main()
