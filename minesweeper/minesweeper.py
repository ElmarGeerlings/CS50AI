import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # If count of mines is equal to count of cells, all cells are mines
        if len(self.cells) == self.count and self.count > 0:
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If count is zero, then all cells are safe
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # If cell is in the sentence, remove it and decrease count by 1
        if cell in self.cells:
            self.cells.remove(cell)
            self.count = self.count - 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # If cell is in the sentence, remove it (without decreasing the count)
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # Mark the cell as a move that has been made
        self.moves_made.add(cell)
        
        # Mark the cell as safe
        self.mark_safe(cell)        
        
        # Make a set of all neighbouring cells
        neighbours = set()
        for i in range(-1,2):
            for j in range(-1,2):
                a, b = cell
                neighbour = (a+i, b+j)
                
                # Ignore cell and substract 1 from count if it contains a mine
                if neighbour in self.mines:
                    count = count - 1
                    continue
                
                # Ignore cell if it's safe
                if neighbour in self.safes:
                    continue
                
                # If cell is within bounds, add to the set
                if 0 <= neighbour[0] < self.height and 0 <= neighbour[1] < self.width:
                    neighbours.add(neighbour)
        
        # Add a new sentence to knowledge base
        self.knowledge.append(Sentence(neighbours, count))
        
        # Variable to check if knowledgebase is changed
        knowledgechange = True
        
        # Add new sentence to knowledge base
        while knowledgechange:
            knowledgechange = False
                
            # Make a new set for all mines and safe spaces
            mines = set()
            safes = set()

            # Get set of mines and safe spaces from knowledge base
            for sentence in self.knowledge:
                mines = mines.union(sentence.known_mines())
                safes = safes.union(sentence.known_safes())
            
            # Mark any mines or safe spaces
            if mines:
                knowledgechange = True
                for mine in mines:
                    self.mark_mine(mine)
            if safes:
                knowledgechange = True
                for safe in safes:
                    self.mark_safe(safe)
            
            # Remove any empty sentences from knowledge base:
            empty = Sentence(set(), 0)
            self.knowledge[:] = [x for x in self.knowledge if x != empty]
            
            # Add new sentences from inference
            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    # Error if sentence with no cells and count > 0
                    if sentence1.cells == set() and sentence1.count > 0:  
                        raise ValueError
                    # New sentence can be created if one is a subset of the other
                    if sentence1 != sentence2 and sentence1.cells.issubset(sentence2.cells):
                        # Create new sentence by inference
                        knowledgechange = True
                        cells = sentence2.cells - sentence1.cells
                        count = sentence2.count - sentence1.count
                        newsentence = Sentence(cells, count)
                        
                        # Add new sentence to knowledgebase, if it doesn't already exist
                        if newsentence not in self.knowledge:
                            knowledgechange = True
                            self.knowledge.append(newsentence)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Make a set of safe moves that haven't been already made
        safe_moves = self.safes - self.moves_made
        
        # Return a random safe move if there are any
        if safe_moves:
            return random.sample(safe_moves, 1)[0]
        # Return None if no save moves are possible
        else:
            return None
        

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        
        # Create a set with all possible options
        all_moves = set()
        for i in range(self.height):
            for j in range(self.width):
                all_moves.add((i,j))
        
        # Create a set of all moves that have not been chosen and are not mines
        possible_moves = all_moves - self.moves_made - self.mines
        
        # Return None if no possible moves
        if not possible_moves:
            return None
        
        
        # Pick a random move
        best_move = random.sample(possible_moves, 1)[0]
        
        # Return random move if no knowledge base
        if not self.knowledge:          
            return best_move
        
        # Find out least risky move
        n_mines = 8-len(self.mines)
        n_moves = len(possible_moves)
        # Risk of an uncovered square is mines/(possible moves)
        risk = n_mines/n_moves
        # Iterate over all possible moves and all sentences
        for move in possible_moves:
            for sentence in self.knowledge:
                # Check risk of a move (count/number of cells) if move is in a sentence
                if move in sentence.cells:
                    newrisk = sentence.count / len(sentence.cells)
                    # Update risk and best_move if it's smaller than the previous risk
                    if newrisk < risk:
                        risk = newrisk
                        best_move = move
        # Return least risky move
        return best_move
        
        
