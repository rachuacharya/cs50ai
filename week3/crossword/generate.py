import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        print("Solving...")
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        print("Node consistency")
        for var in self.domains:
            to_stay = set()
            for word in self.domains[var]:
                if len(word) == var.length:
                    to_stay.add(word)

            self.domains[var] = to_stay


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Initialize revised
        revised = False

        # Over lapping points of two variable
        i, j = self.crossword.overlaps[x, y]
        
        # Check if words consistent with overlap and remove accordingly
        domainsX = self.domains[x].copy()
        
        for xword in domainsX:

            stays = False

            for yword in self.domains[y]:
                if xword[i] == yword[j] and xword != yword:
                    # xword satisfies arc consistency and can stay
                    stays = True
                    break
                
            if not stays:
                self.domains[x].remove(xword)
                revised = True

        return revised

        
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        print("Deploying AC3...")

        if arcs is None:
            # Create initial queue of all arcs 
            queue = set()
            for x in self.crossword.variables:
                neighbor = self.crossword.neighbors(x)
                for y in neighbor:
                    queue.add((x, y))
        else:
            # Use the given initial queue
            queue = set(arcs)
            
        while(len(queue) != 0):
            # Dequeue x, y 
            x, y = queue.pop()

            if self.revise(x, y):
                # if changes have been made to make x arc consistent with y
                # Check if x domain empty, problem has no solution
                if len(self.domains[x]) == 0:
                    # No solution
                    return False

                # If x non-empty after change, check arc consistency of x with remaining neighbors
                for z in self.crossword.neighbors(x):
                    if z != y:
                        queue.add((x, z))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        variables = list(assignment.keys())

        # Check if words are consistent with variable length
        for var in variables:
            for word in self.domains[var]:
                if var.length != len(word):
                    return False
            
        # Check if all variables are assigned distinct words
        if len(set(assignment.values())) != len(assignment.values()):
            return False
        
        # Check if neighbors conflict in charaters
        for x in variables:
            for y in self.crossword.neighbors(x):
                if y in variables:
                    i, j = self.crossword.overlaps[x, y]
                    if assignment[x][i] != assignment[y][j]:
                        # i.e. if neighbors don't have same character in overlap points
                        return False
        return True
        
    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Initialize list to record the no of neighbors 
        # affected by a choice in variable domain
        count_dict = dict()

        xwords = self.domains[var]

        for xword in xwords:
            # Check how many words in neighbor's domain have to be ruled out
            # on selection of x word
            count = 0
            for y in self.crossword.neighbors(var):
                if y not in assignment:
                    for yword in self.domains[y]:
                        i, j = self.crossword.overlaps[var, y]
                        if xword[i] != yword[j]:
                            # no overlap betn xword and yword, hence rule out yword
                            count += 1
                            
            count_dict[xword] = count

        # Sort values of var domain based on their counts
        # key is a lambda function that takes each word in the domain
        # and returns its count
        domain_lst = list(self.domains[var])
        domain_lst.sort(key = lambda x:count_dict[x])
        self.domains[var] = set(domain_lst)


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Remaining values of all variables
        remaining = [
            var for var in self.crossword.variables
            if var not in assignment
        ] 

        # No. of remaining values of each variable
        domain_num = [len(self.domains[var]) for var in remaining]
        minimum = min(domain_num)

        # degree of remaining domain
        domain_degree = {
            var:len(self.crossword.neighbors(var)) for var in remaining
        }

        # Sort variales based on domain num
        zipped = sorted(zip(remaining, domain_num), key = lambda x:x[1])
        
        # Check if more than one variable have minimum count
        min_count = domain_num.count(minimum)

        if min_count == 1:
            return zipped[0][0]
        
        else: 
            # Multiple domains with min num of values
            # list of such domains
            top_min = [zipped[i][0] for i in range(0, min_count)]
            # sort domains by highest order of degree
            top_min.sort(key = lambda x:domain_degree[x], reverse=True)

            return top_min[0]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        print("Backtracking...")
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)

        self.order_domain_values(var, assignment)

        for word in self.domains[var]:
            
            assignment[var] = word

            if self.consistent(assignment):
                                    
                # Call Backtrack recursively
                result = self.backtrack(assignment)

                # If result is not None but an assignment
                if result is not None:
                    return result

            # if result is false then remove the previous assignment
            else:
                assignment.pop(var)
        
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
