import copy

# List of numbers (1,2,3,4,5,6,7,8,9) that can fit into a cell in bitwise representation
NUMS = {1, 2, 4, 8, 16, 32, 64, 128, 256}

def solve(puzzle, verbose=True):
    puzzle = int_to_bitwise(puzzle)
    solved_puzzle, rcells = solve_sudoku(puzzle, 1, verbose)
    if rcells > 0:
        print('Puzzle unsolved', rcells)
        return None

    return bitwise_to_int(solved_puzzle)

# Convert puzzle values to bitwise representation
def int_to_bitwise(puzzle):

    for i in range(9):
        for j in range(9):
            if puzzle[i][j]>2:
                puzzle[i][j] = 2**(puzzle[i][j]-1)
    return puzzle

# Convert bitwise representation back to puzzle values
def bitwise_to_int(puzzle):
    bit_map = {4:3, 8:4, 16:5, 32:6, 64:7, 128:8, 256:9}
    for i in range(9):
        for j in range(9):
            if puzzle[i][j]>2: puzzle[i][j] = bit_map[puzzle[i][j]]

    return puzzle


def solve_sudoku(puzzle, level=1, verbose = True, candidates=None, remaining_cells=None):
    """
    Solves a Sudoku puzzle using a backtracking algorithm  and elimination of candidates.

    Parameters:
    - puzzle_orig: numpy.ndarray
        The initial Sudoku puzzle as a 9x9 numpy array.
    - level: int, optional, default:1
        The backtracking level of the puzzle (default is 1).
    - verbose: bool, optional, default: True
        Whether to print backtracking levels and iteration details

    Returns:
    - numpy.ndarray:
        The solved Sudoku puzzle.
    - int:
        The number of remaining cells.
    """
    
    solved_cells = 0
    iteration = 1
    
    if verbose:
        print('\n'+(level-1)*'\t'+f'Level {level}:')
        print('\t'*level+'Iterations:',end=' ')
    
    # Get candidates for each unfilled cell
    if not candidates:
        candidates = get_candidates(puzzle)

    if not remaining_cells:
        remaining_cells = sum([1 for row in puzzle for x in row if x == 0])
    
    # Fill ones with only one candidate and iterate 
    while True:
        if remaining_cells == 0: break
        
        if verbose: print(iteration, end=' ')
        iteration+=1
        
        valid, remaining_cells_new = fill_candidates(puzzle, candidates, remaining_cells)
        if not valid:
            return puzzle, remaining_cells_new
        solved_cells = remaining_cells-remaining_cells_new
        remaining_cells = remaining_cells_new

        if solved_cells == 0:
            if not find_hidden_singles(candidates): 
                break
                

    # Fill a vacant cell and pass into recursive function if puzzle not filled in iterations
    if remaining_cells > 0:
        
        i,j = get_branching_position(candidates)

        if int.bit_count(candidates[i][j])>1 and puzzle[i][j] == 0:
            candidate = candidates[i][j]
            
            for k in range(9):
                if candidate & 2**k > 0:
                    puzzle_copy = copy.deepcopy(puzzle)
                    candidates_copy = copy.deepcopy(candidates)
                    puzzle_copy[i][j] = 2**k                    
                    candidates_copy[i][j] = 0
                    update_candidate_list(puzzle_copy, candidates_copy, i, j)
                    
                    puzzle_reduced, reduced_cells = solve_sudoku(puzzle = puzzle_copy,
                                                                 level=level+1, verbose=verbose,
                                                                 candidates=candidates_copy,
                                                                 remaining_cells=remaining_cells-1)
                    
                    if reduced_cells == 0:
                        return puzzle_reduced, 0

                
    if verbose: 
        if remaining_cells == 0:
            if level==1:
                print('\nPuzzle solved')
        else:
            print('\n'+(level-1)*'\t'+'Dead end')

    return puzzle, remaining_cells

    
def get_candidates(puzzle):
    """
    Generates a candidate list for each empty cell in the Sudoku puzzle.

    Parameters:
    - puzzle: numpy.ndarray
        The Sudoku puzzle as a 9x9 numpy array.

    Returns:
    - numpy.ndarray:
        A 9x9 numpy array each element containing a list of the candidates for each empty cell.
    """

    candidates = [[0b111111111]*9 for _ in range(9)]
    
    for i in range(9):
        for j in range(9):
            if puzzle[i][j] == 0:
                candidates[i][j] -= ((puzzle[0][j]) | (puzzle[1][j]) | (puzzle[2][j]) 
                | (puzzle[3][j]) | (puzzle[4][j]) | (puzzle[5][j]) 
                | (puzzle[6][j]) | (puzzle[7][j]) | (puzzle[8][j]) 
                | (puzzle[i][0]) | (puzzle[i][1]) | (puzzle[i][2]) 
                | (puzzle[i][3]) | (puzzle[i][4]) | (puzzle[i][5]) 
                | (puzzle[i][6]) | (puzzle[i][7]) | (puzzle[i][8]) 
                | (puzzle[(i//3)*3][(j//3)*3]) | (puzzle[(i//3)*3+1][(j//3)*3]) | (puzzle[(i//3)*3+2][(j//3)*3]) 
                | (puzzle[(i//3)*3][(j//3)*3+1]) | (puzzle[(i//3)*3+1][(j//3)*3+1]) | (puzzle[(i//3)*3+2][(j//3)*3+1]) 
                | (puzzle[(i//3)*3][(j//3)*3+2]) | (puzzle[(i//3)*3+1][(j//3)*3+2]) | (puzzle[(i//3)*3+2][(j//3)*3+2]))
            else: 
                candidates[i][j] = 0
                
    return candidates

    
def fill_candidates(puzzle, candidates, remaining_cells):
    """
    Fills the empty cell the Sudoku puzzle if there is only one candidate/possible value.

    Parameters:
    - puzzle: The Sudoku puzzle as a 9x9 list with bitwise representation.
    - candidates: A 9x9 list, each element containing a list of the candidates for each empty cell.

    Returns:
    - numpy.ndarray: Updated puzzle after filling in candidates.
    """
    
    for i in range(9):
        for j in range(9):
            if puzzle[i][j] | candidates[i][j] > 0: # If a blank puzzle cell has candidates
                if candidates[i][j] in NUMS:
                    puzzle[i][j] = candidates[i][j]
                    candidates[i][j] = 0
                    remaining_cells-=1
                    candidates = update_candidate_list(puzzle, candidates, i, j)
            else: 
                return False, remaining_cells    # If a blank puzzle cell has no candidates
    
    return True, remaining_cells


def update_candidate_list(puzzle, candidates, r, c):
    """
    Update the candidates when a cell is filled

    Parameters:
    -puzzle
    -candidates
    -r,c: row , column of filled value
    """
    filled_val = 0b111111111-puzzle[r][c]
    
    for k in range(9):
        if puzzle[k][c] == 0: candidates[k][c] &= filled_val
        if puzzle[r][k] == 0: candidates[r][k] &= filled_val
            
    for i in range((r//3)*3, (r//3)*3+3):
        for j in range((c//3)*3, (c//3)*3+3):
            if i == r or j == c or puzzle[i][j] > 0: continue
            candidates[i][j] &= filled_val
            
    return candidates

    
def find_hidden_singles(candidates) -> bool:
    """
    Find hidden singles for each empty cell by eliminating candidates based on the other candidates in relevant row, column and block.

    Parameters:
    - candidates: A 9x9 list, each element containing a list of the candidates for each empty cell.

    Returns:
    - bool: If a hidden single found or not.
    """
    nums = {1, 2, 4, 8, 16, 32, 64, 128, 256}
    
    hs_availabe = False
    
    for i in range(9):
        for j in range(9):
            if candidates[i][j] > 1:
                row_candidates = get_row_candidates(candidates, i, j)
                row_cleaned_list = candidates[i][j] & (0b111111111-row_candidates)
                if row_cleaned_list in nums:
                    candidates[i][j] = row_cleaned_list
                    hs_availabe = True
                    continue
                
                col_candidates = get_col_candidates(candidates, i, j)
                col_cleaned_list = candidates[i][j] & (0b111111111-col_candidates)
                if col_cleaned_list in nums:
                    candidates[i][j] = col_cleaned_list
                    hs_availabe = True
                    continue
                
                block_candidates = get_block_candidates(candidates, i, j)
                block_cleaned_list = candidates[i][j] & (0b111111111-block_candidates)
                if block_cleaned_list in nums:
                    candidates[i][j] = block_cleaned_list
                    hs_availabe = True

    return hs_availabe


def get_row_candidates(candidates, i, j) -> list:
    """
    Gets the list of all the other candidates in the row index-i except for the candidates in row index-i and column index-j.

    Parameters:
    - candidates: numpy.ndarray
        A 9x9 numpy array, each element containing a list of the candidates for each empty cell.
    - i: int
        Row index.
    - j: int
        Column index.

    Returns:
    - list: The list of all the other candidates in the row index-i.
    """

    row = 0
    for k in range(9):
        if k == j: continue
        row |= candidates[i][k]

    return row


def get_col_candidates(candidates, i, j) -> list:
    """
    Gets the list of all the other candidates in the column index-j except for the candidates in row index-i and column index-j.

    Parameters:
    - candidates: numpy.ndarray
        A 9x9 numpy array, each element containing a list of the candidates for each empty cell.
    - i: int
        Row index.
    - j: int
        Column index.

    Returns:
    - list: The list of all the other candidates in the column index-j.
    """

    col = 0
    for k in range(9):
        if k == i: continue
        col |= candidates[k][j]
        
    return col


def get_block_candidates(candidates, i, j) -> list:
    """
    Gets the list of all the other candidates in the relevant 3x3 block except for the candidates in row index-i and column index-j.

    Parameters:
    - candidates: numpy.ndarray
        A 9x9 numpy array, each element containing a list of the candidates for each empty cell.
    - i: int
        Row index.
    - j: int
        Column index.

    Returns:
    - list: The list of all the other candidates in the relevant block cell i,j belongs to.
    """

    block = 0
    i1, i2, j1, j2 = (i//3)*3, (i//3)*3+3, (j//3)*3, (j//3)*3+3
    for k in range(i1,i2):
        for l in range(j1,j2):
            if k == i and l == j: continue
            block |= candidates[k][l]
            
    return block


def get_branching_position(candidates) -> (int, int):
    """
    Finds the position (row, column) with the minimum number of candidates for branching.

    Parameters:
    - candidates: numpy.ndarray
        A 9x9 numpy array, each element containing a list of the candidates for each empty cell.

    Returns:
    - tuple: The row and column indices of the first cell with the minimum candidates.
    """

    ib,jb = 0,0
    num_candidates = 9

    for i in range(9):
        for j in range(9):
            if 1 < int.bit_count(candidates[i][j]) < num_candidates:
                ib,jb = i,j
                num_candidates = int.bit_count(candidates[i][j])
                if num_candidates == 2: 
                    return ib,jb
                    
    return ib,jb


