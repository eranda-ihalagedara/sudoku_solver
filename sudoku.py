import numpy as np


def solve_sudoku(puzzle):
    puzzle_orig = puzzle.copy()
    remaining_cells = np.sum(puzzle==0)
    solved_cells = 0
    return_puzzle = False
    iteration = 1
    while not return_puzzle:
        print(iteration)
        iteration+=1

        if remaining_cells == 0:
            return_puzzle=True
            break
            
        candidates = get_candidate_list(puzzle)
        puzzle = fill_candidates(puzzle, candidates)
        solved_cells = remaining_cells-np.sum(puzzle==0)

        if solved_cells > 0:
            remaining_cells -= solved_cells 
            continue

        else:
            candidates = refine_candidates(candidates)
            puzzle = fill_candidates(puzzle, candidates)

            solved_cells = remaining_cells-np.sum(puzzle==0)

            if solved_cells > 0:
                remaining_cells -= solved_cells 

            else:
                candidates, filled = fill_dual_cells(puzzle, candidates)

                if filled:
                    puzzle = fill_candidates(puzzle, candidates)
                    solved_cells = remaining_cells-np.sum(puzzle==0)
                    remaining_cells -= solved_cells 

                else:
                    candidates, filled = fill_triple_cells(puzzle, candidates)

                    if filled:
                        puzzle = fill_candidates(puzzle, candidates)
                        solved_cells = remaining_cells-np.sum(puzzle==0)
                        remaining_cells -= solved_cells 

                    else :
                        # candidates = fill_first_possibility(candidates)
                        # puzzle = fill_candidates(puzzle, candidates)
    
                        # solved_cells = remaining_cells-np.sum(puzzle==0)
            
                        # if solved_cells > 0:
                        #     remaining_cells -= solved_cells 
    
                        # else:
                        return_puzzle = True

    return puzzle

    
def get_candidate_list(puzzle):
    candidates = np.empty((9,9), dtype=object)
    numbers = set(range(1,10))
    for i in range(9):
        for j in range(9):
            if puzzle[i,j] == 0:
                candidates[i,j] = list(numbers - set(puzzle[i,:]) - set(puzzle[:,j]) - set(puzzle[(i//3)*3 : (i//3)*3+3,(j//3)*3 : (j//3)*3+3].flatten()))

    return candidates


def fill_candidates(puzzle, candidates):
    filled_puzzle = puzzle.copy()
    for i in range(9):
        for j in range(9): 
            if candidates[i,j] is not None and len(candidates[i,j])==1:
                filled_puzzle[i,j] = candidates[i,j][0]

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
                
                cleaned_list = list(set(candidates[i,j]) - set(row_candidates) - set(col_candidates) - set(block_candidates))
                
                if len(cleaned_list) > 0:
                    refined_candidates[i,j] = cleaned_list

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


def count_occurances(element, selection):
    count = 0
    # Loop through the array and check for elements
    for item in selection:
      if item is not None and item == element:
        count += 1
    return count


def fill_dual_cells(puzzle, candidates):
    filled=False
    
    for i in range(9):
        for j in range(9):
            if candidates[i,j] is not None and len(candidates[i,j])==2:
                # Check row for duplicates and uniqueness
                dcount = count_occurances(candidates[i,j], candidates[i,:])
                if dcount==2:
                    rcd = get_row_candidates(candidates, i, j)
                    if rcd.count(candidates[i,j][0]) == 1 and rcd.count(candidates[i,j][1]) == 1:
                        candidates[i,j] = [candidates[i,j][0]]
                        filled = True
                        return candidates, filled

                # Check column for duplicates and uniqueness
                dcount = count_occurances(candidates[i,j], candidates[:,j])
                if dcount==2:
                    ccd = get_col_candidates(candidates, i, j)
                    if ccd.count(candidates[i,j][0]) == 1 and ccd.count(candidates[i,j][1]) == 1:
                        candidates[i,j] = [candidates[i,j][0]]
                        filled = True
                        return candidates, filled

                # Check block for duplicates and uniqueness
                dcount = count_occurances(candidates[i,j], candidates[(i//3)*3 : (i//3)*3+3,(j//3)*3 : (j//3)*3+3].flatten())
                if dcount==2:
                    bcd = get_block_candidates(candidates, i, j)
                    if bcd.count(candidates[i,j][0]) == 1 and bcd.count(candidates[i,j][1]) == 1:
                        candidates[i,j] = [candidates[i,j][0]]
                        filled = True
                        return candidates, filled

    return candidates, filled


def fill_first_possibility(candidates):
    for i in range(9):
        for j in range(9):
            if candidates[i,j] is not None and len(candidates[i,j])==2:
                candidates[i,j] = [candidates[i,j][0]]
    return candidates


def fill_triple_cells(puzzle, candidates):
    filled=False
    
    for i in range(9):
        for j in range(9):
            if candidates[i,j] is not None and len(candidates[i,j])==3:
                # Check row for duplicates and uniqueness
                dcount = count_occurances(candidates[i,j], candidates[i,:])
                if dcount==3:
                    rcd = get_row_candidates(candidates, i, j)
                    if rcd.count(candidates[i,j][0]) == 2 and rcd.count(candidates[i,j][1]) == 2 and rcd.count(candidates[i,j][2]) == 2:
                        candidates[i,j] = [candidates[i,j][0]]
                        filled = True
                        return candidates, filled

                # Check column for duplicates and uniqueness
                dcount = count_occurances(candidates[i,j], candidates[:,j])
                if dcount==3:
                    ccd = get_col_candidates(candidates, i, j)
                    if ccd.count(candidates[i,j][0]) == 2 and ccd.count(candidates[i,j][1]) == 2 and ccd.count(candidates[i,j][2]) == 2:
                        candidates[i,j] = [candidates[i,j][0]]
                        filled = True
                        return candidates, filled

                # Check block for duplicates and uniqueness
                dcount = count_occurances(candidates[i,j], candidates[(i//3)*3 : (i//3)*3+3,(j//3)*3 : (j//3)*3+3].flatten())
                if dcount==3:
                    bcd = get_block_candidates(candidates, i, j)
                    if bcd.count(candidates[i,j][0]) == 2 and bcd.count(candidates[i,j][1]) == 2 and bcd.count(candidates[i,j][2]) == 2:
                        candidates[i,j] = [candidates[i,j][0]]
                        filled = True
                        return candidates, filled

    return candidates, filled