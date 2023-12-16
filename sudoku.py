import numpy as np


def solve_sudoku(puzzle_orig, level=1):
    print('\n'+(level-1)*'\t'+f'Level {level}:')
    puzzle = puzzle_orig.copy()
    remaining_cells = np.sum(puzzle==0)
    solved_cells = 0
    return_puzzle = False
    iteration = 1

    print('\t'*level+'Iterations:',end=' ')
    
    while not return_puzzle:
        if remaining_cells == 0:
            return_puzzle=True
            break

        print(iteration, end=' ')
        iteration+=1
            
        candidates = get_candidate_list(puzzle)
        puzzle = fill_candidates(puzzle, candidates)
        solved_cells = remaining_cells-np.sum(puzzle==0)

        if solved_cells > 0:
            remaining_cells -= solved_cells 
            # print('Candidate fill')

        else:
            candidates = refine_candidates(candidates)
            puzzle = fill_candidates(puzzle, candidates)

            solved_cells = remaining_cells-np.sum(puzzle==0)

            if solved_cells > 0:
                remaining_cells -= solved_cells 
                # print('Refined candidates')

            else:
                return_puzzle = True

    if remaining_cells > 0:
        # Fill first vacant cell and pass into resursive function
        candidates = get_candidate_list(puzzle)
        i,j = get_branching_position(candidates)

        if candidates[i,j] is not None and len(candidates[i,j])>1:
            for candidate in candidates[i,j]:                   
                puzzle_copy = puzzle.copy()
                puzzle_copy[i,j] = candidate
                puzzle_reduced, reduced_cells = solve_sudoku(puzzle_copy, level+1)
                
                if reduced_cells == 0:
                    puzzle = puzzle_reduced
                    remaining_cells = 0
                    break
            

    if remaining_cells == 0:
        if level==1:
            print('\nPuzzle solved')
    else:
        print('Dead end')
    return puzzle, remaining_cells

    
def get_candidate_list(puzzle):
    candidates = np.empty((9,9), dtype=object)
    numbers = set(range(1,10))
    for i in range(9):
        for j in range(9):
            if puzzle[i,j] == 0:
                candidates[i,j] = list(numbers - set(puzzle[i,:]) - set(puzzle[:,j]) - set(puzzle[(i//3)*3 : (i//3)*3+3,(j//3)*3 : (j//3)*3+3].flatten()))
    # print(candidates[0,1], candidates[0,0], puzzle[0,0], puzzle[0,1])
    return candidates


def fill_candidates(puzzle, candidates):
    filled_puzzle = puzzle.copy()
    for i in range(9):
        for j in range(9): 
            if candidates[i,j] is not None and len(candidates[i,j])==1:
                filled_puzzle[i,j] = candidates[i,j][0]
                candidates = get_candidate_list(filled_puzzle)
    return filled_puzzle


def refine_candidates(candidates):
    refined_candidates = candidates.copy()
    for i in range(9):
        for j in range(9):
            if candidates[i,j] is not None and len(candidates[i,j])>1:
                # print(i,j)
                row_candidates = get_row_candidates(candidates, i, j)
                col_candidates = get_col_candidates(candidates, i, j)
                block_candidates = get_block_candidates(candidates, i, j)
                
                row_cleaned_list = list(set(candidates[i,j]) - set(row_candidates))
                col_cleaned_list = list(set(candidates[i,j]) - set(col_candidates))
                block_cleaned_list = list(set(candidates[i,j]) - set(block_candidates))
                all_cleaned_list = list(set(candidates[i,j]) - set(row_candidates) - set(col_candidates) - set(block_candidates))
                
                if len(row_cleaned_list) == 1:
                    refined_candidates[i,j] = row_cleaned_list
                elif len(col_cleaned_list) == 1:
                    refined_candidates[i,j] = col_cleaned_list
                elif len(block_cleaned_list) == 1:
                    refined_candidates[i,j] = block_cleaned_list
                elif len(all_cleaned_list) == 1:
                    refined_candidates[i,j] = all_cleaned_list

    return refined_candidates


def get_row_candidates(candidates, i, j):
    row = []
    for k in range(9):
        if k == j:
            continue
        if candidates[i, k] is not None and len(candidates[i, k])>0:
            row.extend(candidates[i, k])
    return row


def get_col_candidates(candidates, i, j):
    col = []
    for k in range(9):
        if k == i:
            continue
        if candidates[k, j] is not None and len(candidates[k,j])>0:
            col.extend(candidates[k,j])
    return col


def get_block_candidates(candidates, i, j):
    block = []
    i1, i2, j1, j2 = (i//3)*3, (i//3)*3+3, (j//3)*3, (j//3)*3+3
    
    for k in range(i1,i2):
        for l in range(j1,j2):
            if k == i and l == j:
                continue
            if candidates[k, l] is not None and len(candidates[k, l])>0:
                block.extend(candidates[k,l])
    return block


def get_branching_position(candidates):
    i,j = 0,0
    position_found = False

    for num_candidates in range(2,9):
        for i in range(9):
            for j in range(9):
                if candidates[i,j] is not None and len(candidates[i,j])==num_candidates:
                    position_found = True
                    break
            if position_found:
                break
        if position_found:
                break
            
    return i,j


def count_occurances(element, selection):
    count = 0
    # Loop through the array and check for elements
    for item in selection:
      if item is not None and item == element:
        count += 1
    return count

