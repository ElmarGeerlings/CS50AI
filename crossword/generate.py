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
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Loop over every variable
        for var in self.domains:
            # List to store words to remove from variable domain
            removelist = []
            # Check for every word if its length matches the variable length
            for word in self.domains[var]:
                # Add word to removal list if it doesn't match the variable length
                if var.length != len(word):
                    removelist.append(word)
            # Remove the words from the removal list
            for word in removelist:
                self.domains[var].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Set revision as false
        revision = False
        
        # Find overlap between variable x and y
        overlap = self.crossword.overlaps.get((x,y))
        
        # Ensure arc consistency if there is overlap between x an y
        if overlap:
            # List to store words to remove from x-domain
            removelist = []
            for xword in self.domains[x]:
                # Set arc consistency from xword to False
                ac = False
                for yword in self.domains[y]:
                    # Check if overlap is possible between word from x-domain and y
                    if xword[overlap[0]] == yword[overlap[1]]:
                        ac = True
                        break
                # If xword is not arc consistent with y, add to removelist and set revision to true
                if ac == False:
                    removelist.append(xword)
                    revision = True
            # Remove words froms x-domain
            for word in removelist:
                self.domains[x].remove(word)
        # Return whether there has been made a revision to the domain of "x"
        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Initial list of all arcs in the problem if arcs is empty
        if not arcs:
            arcs = []
            # Loop over every variable and its neighbors
            for var in self.domains:
                for neighbor in self.crossword.neighbors(var):
                    # Add arc to list
                    if var != neighbor:
                        arcs.append((var, neighbor))
        
        # Loop while there are arcs
        while arcs:
            x, y = arcs.pop()
            # Check if a revision has been made
            if self.revise(x, y):
                # Return False if there are no values in x-domain left
                if not self.domains[x]:
                    return False
                # Add all arcs between x and z(!= y) to the queue
                for z in self.crossword.neighbors(x):
                    if z != y:
                       arcs.append((z,x))     
        
        # Return True if arc consistency is enforced and no domains are empty
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Loop over every variable in assignment
        for var in self.domains:
            # Return False if a variable has not a value assigned to it
            if var not in assignment:
                return False
        
        # Return True if every variable has a value assigned to it
        return True
    
    
    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # A list to save all the words in
        words = []
        # Loop over every variable in assignment
        for var in assignment:            
            word = assignment[var]
            # Inconsistent if variable length is not the correct length or words are not distinct
            if var.length != len(word) or word in words:
                return False
            # Add word to words list
            words.append(word)
            # Check if there are no conflicts between neighboring variables.
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    if word[i] != assignment[neighbor][j]:
                        return False
        
        # Return True is assignment is consistent
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Initialise list to save variable and number of restictions associated with it
        reslist = []
        # Loop over every value in the domain of "var"
        for value in self.domains[var]:
            # Check if value is already assigned
            if value not in assignment:
                # Initialise variable to count the number of restictions associated with value
                counter = 0
                # Loop over every neighbor
                for neighbor in self.crossword.neighbors(var):
                    # Add 1 to counter if variable rules out neighbour
                    if value in self.domains[neighbor]:
                        counter += 1
            # Append value and restriction counter to reslist
            reslist.append((value, counter))
        
        # Sort based on fewest number of restrictions
        sortedlist = sorted(reslist, key=lambda item: item[1])
        
        # Make a list of only the values without the number of retrictions
        vlist = []
        for v in sortedlist:
            vlist.append(v[0])
        
        # Return a sorted list of all values
        return vlist

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Initialise a list to store variable with the least values in its domain
        minvalues = [[99999, 99999]]
        # Loop over every variable
        for var in self.domains:
            # Continue if variable is already assigned
            if var in assignment:
                continue
            # Count the number of values in variable domain
            count = 0
            for value in self.domains[var]:
                count += 1
            # Save variable and number of values in domain in minvalues list if it's the current minimum
            if count < minvalues[0][1]:
                minvalues = [[var, count]]
            # If it's a tied minimum, add variable and number of values to minvalues list
            elif count == minvalues[0][1]:
                minvalues.append([var, count])
        
        # Find value with highest degree out of minvalues list if there is more than one variable left
        if len(minvalues) > 1:
            minvalues[0][1] = 0
            # Loop over every variable left
            for minvalue in minvalues:
                var = minvalue[0]
                # Initialise variable n to count number of neighbours
                n = 0
                # Count neighbours
                for neighbor in self.crossword.neighbors(var):
                    n += 1
                # Save variable and neighbourcount if n is current maximum
                if n > minvalues[0][1]:
                    minvalues[0] = [var, n]
        
        # Return variable
        return minvalues[0][0]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Return assignment if complete
        if self.assignment_complete(assignment):
            return assignment
        # Select unnassigned variable
        var = self.select_unassigned_variable(assignment)
        # Loop over ordered values
        for value in self.order_domain_values(var, assignment):
            # Add var and value to assignment
            assignment.update({var: value})
            # Check if assignment is consistent
            if self.consistent(assignment):
                # Use recursion
                result = self.backtrack(assignment)
                if result:
                    return result
            # Remove var and value from assignment
            assignment.pop(var)
        
        # Return None if no solution
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

#%%
"""
import random
import numpy as np
    
plist = [
    ('Alison', 50, 18),
    ('Terence', 75, 12),
    ('David', 75, 20),
    ('Jimmy', 90, 22),
    ('John', 45, 12)
]

pplist = []

for p in plist:
    name = p[0]
    number = random.randint(1, 10)
    pplist.append([int(number), name])

ppplist = np.sort(pplist)

print(ppplist[0:len(pplist)])
"""
