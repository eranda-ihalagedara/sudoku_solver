import copy

def solve(puzzle, verbose=True):
    puzzle = int_to_bitwise(puzzle)
    solved_puzzle, rcells = solve_sudoku(puzzle, 1, verbose)
    if rcells > 0:
        print('Puzzle unsolved', rcells)
        return None

    return bitwise_to_int(solved_puzzle)

    
def int_to_bitwise(puzzle):

    for i in range(9):
        for j in range(9):
            if puzzle[i][j]>2:
                puzzle[i][j] = 2**(puzzle[i][j]-1)
    return puzzle

    
def bitwise_to_int(puzzle):
    bit_map = {4:3, 8:4, 16:5, 32:6, 64:7, 128:8, 256:9}
    for i in range(9):
        for j in range(9):
            if puzzle[i][j]>2: puzzle[i][j] = bit_map[puzzle[i][j]]

    return puzzle


    
def solve_sudoku(puzzle, level=1, verbose = True):
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

    remaining_cells = sum([1 for row in puzzle for x in row if x == 0])
    solved_cells = 0
    candidates = get_candidates(puzzle)

    iteration = 1
    
    if verbose:
        print('\n'+(level-1)*'\t'+f'Level {level}:')
        print('\t'*level+'Iterations:',end=' ')
    
    # Get candidates for each unfilled cell, fill ones with only one possibility iterate 
    while True:
        if remaining_cells == 0: break
        
        if verbose: print(iteration, end=' ')
        iteration+=1
        
        puzzle, remaining_cells_new, candidates = fill_candidates(puzzle, candidates, remaining_cells)
        solved_cells = remaining_cells-remaining_cells_new
        remaining_cells = remaining_cells_new

        if solved_cells == 0:
            if not refine_candidates(candidates): 
                break
                

    # Fill a vacant cell and pass into recursive function if puzzle not filled in iterations
    if remaining_cells > 0:
        
        i,j = get_branching_position(candidates)

        if int.bit_count(candidates[i][j])>1 and puzzle[i][j] == 0:
            candidate = candidates[i][j]
            
            for k in range(9):
                if candidate % 2:
                    puzzle_copy = copy.deepcopy(puzzle)
                    puzzle_copy[i][j] = 2**k
                    puzzle_reduced, reduced_cells = solve_sudoku(puzzle_copy, level+1, verbose)
                    
                    if reduced_cells == 0:
                        puzzle = puzzle_reduced
                        remaining_cells = 0
                        break
                    
                candidate >>= 1
                
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


def update_candidate_list(puzzle, candidates, r, c):

    filled_val = puzzle[r][c]^0b111111111
    
    for k in range(9):
        if puzzle[k][c] == 0: candidates[k][c] &= filled_val
        if puzzle[r][k] == 0: candidates[r][k] &= filled_val
            
    for i in range((r//3)*3, (r//3)*3+3):
        for j in range((c//3)*3, (c//3)*3+3):
            if i == r or j == c or puzzle[i][j] > 0: continue
            candidates[i][j] &= filled_val
            
    return candidates

    
def fill_candidates(puzzle, candidates, remaining_cells):
    """
    Fills the empty cell the Sudoku puzzle if there is only one candidate/possible value.

    Parameters:
    - puzzle (numpy.ndarray): The Sudoku puzzle as a 9x9 numpy array.
    - candidates (numpy.ndarray): A 9x9 numpy array, each element containing a list of the candidates for each empty cell.

    Returns:
    - numpy.ndarray: Updated puzzle after filling in candidates.
    """

    nums = {1, 2, 4, 8, 16, 32, 64, 128, 256}
    
    for i in range(9):
        for j in range(9): 
            if candidates[i][j] in nums:
                puzzle[i][j] = candidates[i][j]
                candidates[i][j] = 0
                remaining_cells-=1
                candidates = update_candidate_list(puzzle, candidates, i, j)
                
    return puzzle, remaining_cells, candidates


def refine_candidates(candidates) -> bool:
    """
    Refines the candidate list for each empty cell by eliminating candidates based on the other candidates in relevant row, column and block.

    Parameters:
    - candidates: numpy.ndarray
        A 9x9 numpy array, each element containing a list of the candidates for each empty cell.

    Returns:
    - numpy.ndarray:
        Refined candidate list after eliminating invalid candidates.
    """
    nums = {1, 2, 4, 8, 16, 32, 64, 128, 256}
    
    is_refined = False
    for i in range(9):
        for j in range(9):
            if candidates[i][j] > 1:
                row_candidates = get_row_candidates(candidates, i, j)
                col_candidates = get_col_candidates(candidates, i, j)
                block_candidates = get_block_candidates(candidates, i, j)
                
                row_cleaned_list = candidates[i][j] & (row_candidates^0b111111111)
                col_cleaned_list = candidates[i][j] & (col_candidates^0b111111111)
                block_cleaned_list = candidates[i][j] & (block_candidates^0b111111111)

                if row_cleaned_list in nums:
                    candidates[i][j] = row_cleaned_list
                    is_refined = True
                elif col_cleaned_list in nums:
                    candidates[i][j] = col_cleaned_list
                    is_refined = True
                elif block_cleaned_list in nums:
                    candidates[i][j] = block_cleaned_list
                    is_refined = True

    return is_refined


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


