import numpy as np


def solve_sudoku(puzzle: np.ndarray , level=1, verbose = True) -> (np.ndarray, int):
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
    
    remaining_cells = np.sum(puzzle==0)
    solved_cells = 0
    return_puzzle = False
    iteration = 1
    candidates = get_candidate_list(puzzle)
    
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
            candidates, is_refined = refine_candidates(candidates)
            if not is_refined: break
                

    # Fill a vacant cell and pass into recursive function if puzzle not filled in iterations
    if remaining_cells > 0:
        
        i,j = get_branching_position(candidates)

        if candidates[i,j] is not None and len(candidates[i,j])>1:
            for candidate in candidates[i,j]:                   
                puzzle_copy = puzzle.copy()
                puzzle_copy[i,j] = candidate
                puzzle_reduced, reduced_cells = solve_sudoku(puzzle_copy, level+1, verbose)
                
                if reduced_cells == 0:
                    puzzle = puzzle_reduced
                    remaining_cells = 0
                    break
    if verbose: 
        if remaining_cells == 0:
            if level==1:
                print('\nPuzzle solved')
        else:
            print('\n'+(level-1)*'\t'+'Dead end')

    return puzzle, remaining_cells

    
def get_candidate_list(puzzle: np.ndarray) -> np.ndarray:
    """
    Generates a candidate list for each empty cell in the Sudoku puzzle.

    Parameters:
    - puzzle: numpy.ndarray
        The Sudoku puzzle as a 9x9 numpy array.

    Returns:
    - numpy.ndarray:
        A 9x9 numpy array each element containing a list of the candidates for each empty cell.
    """

    numbers = {1,2,3,4,5,6,7,8,9}
    candidates = np.empty((9,9), dtype=object)
    
    for i in range(9):
        for j in range(9):
            if puzzle[i,j] == 0:
                candidates[i,j] = list(numbers - set(puzzle[i,:]) - set(puzzle[:,j]) - set(puzzle[(i//3)*3 : (i//3)*3+3,(j//3)*3 : (j//3)*3+3].flatten()))
                    
    return candidates


def update_candidate_list(puzzle, candidates, r, c):

    filled_set = {puzzle[r,c]}
    
    for i in range(9):
        if puzzle[i,c] == 0:
            candidates[i,c] = list(set(candidates[i,c]) - filled_set)
            
    for j in range(9):
        if puzzle[r,j] == 0:
            candidates[r,j] = list(set(candidates[r,j]) - filled_set)
            
    for i in range((r//3)*3, (r//3)*3+3):
        for j in range((c//3)*3, (c//3)*3+3):
            if i == r or j == c or puzzle[i,j] > 0:
                continue
            candidates[i,j] = list(set(candidates[i,j]) - filled_set)
            
    return candidates

    
def fill_candidates(puzzle: np.ndarray, candidates: np.ndarray, remaining_cells):
    """
    Fills the empty cell the Sudoku puzzle if there is only one candidate/possible value.

    Parameters:
    - puzzle (numpy.ndarray): The Sudoku puzzle as a 9x9 numpy array.
    - candidates (numpy.ndarray): A 9x9 numpy array, each element containing a list of the candidates for each empty cell.

    Returns:
    - numpy.ndarray: Updated puzzle after filling in candidates.
    """

    filled_puzzle = puzzle.copy()
    for i in range(9):
        for j in range(9): 
            if candidates[i,j] is not None and len(candidates[i,j])==1:
                filled_puzzle[i,j] = candidates[i,j].pop()
                remaining_cells-=1
                candidates = update_candidate_list(filled_puzzle, candidates, i, j)
                
    return filled_puzzle, remaining_cells, candidates


def refine_candidates(candidates: np.ndarray) -> np.ndarray:
    """
    Refines the candidate list for each empty cell by eliminating candidates based on the other candidates in relevant row, column and block.

    Parameters:
    - candidates: numpy.ndarray
        A 9x9 numpy array, each element containing a list of the candidates for each empty cell.

    Returns:
    - numpy.ndarray:
        Refined candidate list after eliminating invalid candidates.
    """

    refined_candidates = candidates.copy()
    is_refined = False
    for i in range(9):
        for j in range(9):
            if candidates[i,j] is not None and len(candidates[i,j])>1:
                row_candidates = get_row_candidates(candidates, i, j)
                col_candidates = get_col_candidates(candidates, i, j)
                block_candidates = get_block_candidates(candidates, i, j)
                
                row_cleaned_list = list(set(candidates[i,j]) - set(row_candidates))
                col_cleaned_list = list(set(candidates[i,j]) - set(col_candidates))
                block_cleaned_list = list(set(candidates[i,j]) - set(block_candidates))
                all_cleaned_list = list(set(candidates[i,j]) - set(row_candidates) - set(col_candidates) - set(block_candidates))
                
                if len(row_cleaned_list) == 1:
                    refined_candidates[i,j] = row_cleaned_list
                    is_refined = True
                elif len(col_cleaned_list) == 1:
                    refined_candidates[i,j] = col_cleaned_list
                    is_refined = True
                elif len(block_cleaned_list) == 1:
                    refined_candidates[i,j] = block_cleaned_list
                    is_refined = True
                elif len(all_cleaned_list) == 1:
                    refined_candidates[i,j] = all_cleaned_list
                    is_refined = True

    return refined_candidates, is_refined


def get_row_candidates(candidates: np.ndarray, i, j) -> list:
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

    row = []
    for k in range(9):
        if k == j:
            continue
        if candidates[i, k] is not None and len(candidates[i, k])>0:
            row.extend(candidates[i, k])
    return row


def get_col_candidates(candidates: np.ndarray, i, j) -> list:
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

    col = []
    for k in range(9):
        if k == i:
            continue
        if candidates[k, j] is not None and len(candidates[k,j])>0:
            col.extend(candidates[k,j])
    return col


def get_block_candidates(candidates: np.ndarray, i, j) -> list:
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

    block = []
    i1, i2, j1, j2 = (i//3)*3, (i//3)*3+3, (j//3)*3, (j//3)*3+3
    
    for k in range(i1,i2):
        for l in range(j1,j2):
            if k == i and l == j:
                continue
            if candidates[k, l] is not None and len(candidates[k, l])>0:
                block.extend(candidates[k,l])
    return block


def get_branching_position(candidates: np.ndarray) -> (int, int):
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
            if candidates[i,j] is not None and 1 < len(candidates[i,j])<num_candidates:
                ib,jb = i,j
                num_candidates = len(candidates[i,j])
                if num_candidates == 2:
                    return ib,jb
        
    return ib,jb


