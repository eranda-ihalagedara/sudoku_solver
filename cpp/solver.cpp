#include "solver.h"

#include <iostream> 
#include <string>
#include <unordered_set>
#include <unordered_map>

void Solver::IntToBitwise(int puzzle[][9]){
  for (int i=0; i<9; i++){
    for(int j=0; j<9; j++){
      if (puzzle[i][j] > 2)
        puzzle[i][j] = 1 <<(puzzle[i][j]-1);
    }
  }
}


void Solver::BitwiseToInt(int puzzle[][9]){
  for (int i=0; i<9; i++){
    for(int j=0; j<9; j++){
      if (puzzle[i][j] > 2)
        puzzle[i][j] = bitwisemap.at(puzzle[i][j]);
    }
  }
}


void Solver::PrintPuzzle(int puzzle[][9]){
  std::cout << "\n";
  for (int i=0; i<9;i++){
    for(int j=0; j<9; j++){
      std::cout << puzzle[i][j] << " ";
    }
    std::cout << std::endl;
  }
}


void Solver::Solve(int puzzle[][9], bool verbose){
 
  IntToBitwise(puzzle);

  int candidates[9][9] {};
  getCandidates(puzzle, candidates);
  
  int remaining_cells = 0;
  for (int i=0; i<9;i++){
    for(int j=0; j<9; j++){
      if (puzzle[i][j] == 0) remaining_cells++;
    }
  }

  SolveSudoku(puzzle, candidates, remaining_cells, 1, verbose);
  if (remaining_cells>0){
    std::cout << "Puzzle unsolved";
    return;
  }
  
  BitwiseToInt(puzzle);
  std::cout << "\n\nPuzzle solved:" << std::endl;
  PrintPuzzle(puzzle);
}

int Solver::SolveSudoku(int puzzle[][9],int candidates[][9], int& remaining_cells, int level, bool verbose){
  int solved_cells = 0,remaining_cells_new  = remaining_cells;
  int iteration = 1;

  if (verbose) {
    std::cout << '\n' + std::string(level-1, '\t') + "Level " + std::to_string(level) + ":" << std::endl;
    std::cout << std::string(level, '\t') + "Iterations: ";
  }

  while(true){
    if (remaining_cells_new == 0) return 0;

    if (verbose) std::cout << iteration << " ";
    iteration++;
    
    if (!FillCandidates(puzzle, candidates, remaining_cells))
      return remaining_cells;
    solved_cells = remaining_cells_new - remaining_cells;
    remaining_cells_new = remaining_cells;

    if( solved_cells == 0)
      if (not FindHiddenSingles(candidates)) break;
  }

  int i = 0, j = 0;
  getBranchingPosition(candidates, i, j);

  //std::cout << "branch:" << i << "," <<  j << " val: " << puzzle[i][j] << " candidates "<<candidates[i][j]<<std::endl;
  if (puzzle[i][j] == 0){
    int candidate = candidates[i][j];
    int reduced_cells;
    
     for (int k=0; k<9; k++){
        if ((candidate & (1<<k)) > 0){
            int puzzle_copy[9][9] {};
            std::copy(&puzzle[0][0], &puzzle[0][0]+81, &puzzle_copy[0][0]);
            int candidates_copy[9][9] {};
            std::copy(&candidates[0][0], &candidates[0][0]+81, &candidates_copy[0][0]);
            
            puzzle_copy[i][j] = (1<<k);                    
            candidates_copy[i][j] = 0;
            
            UpdateCandidates(puzzle_copy, candidates_copy, i, j);
            reduced_cells = remaining_cells-1;

            SolveSudoku(puzzle_copy, candidates_copy, reduced_cells, level+1, verbose);

            if (reduced_cells == 0){
              remaining_cells = 0;
              std::copy(&puzzle_copy[0][0], &puzzle_copy[0][0]+81, &puzzle[0][0]);
              return 0;
              }
        }
      }
  }

  if (verbose) {
    if (remaining_cells == 0 && level == 1){
      std::cout << "\nPuzzle solved" << std::endl;
    } else if (remaining_cells != 0){
      std::cout << "\n" << std::string(level-1, '\t') << "Dead end" << std::endl;
    }
  }
  
  return remaining_cells;
}


void Solver::getCandidates(int puzzle[][9], int candidates[][9]){

  for (int i=0; i<9;i++){
    for(int j=0; j<9; j++){
      if (puzzle[i][j] == 0 ){
        candidates[i][j] = 511 - ((puzzle[0][j]) | (puzzle[1][j]) | (puzzle[2][j]) 
                                | (puzzle[3][j]) | (puzzle[4][j]) | (puzzle[5][j]) 
                                | (puzzle[6][j]) | (puzzle[7][j]) | (puzzle[8][j]) 
                                | (puzzle[i][0]) | (puzzle[i][1]) | (puzzle[i][2]) 
                                | (puzzle[i][3]) | (puzzle[i][4]) | (puzzle[i][5]) 
                                | (puzzle[i][6]) | (puzzle[i][7]) | (puzzle[i][8]) 
                                | (puzzle[(i/3)*3][(j/3)*3]) | (puzzle[(i/3)*3+1][(j/3)*3]) | (puzzle[(i/3)*3+2][(j/3)*3]) 
                                | (puzzle[(i/3)*3][(j/3)*3+1]) | (puzzle[(i/3)*3+1][(j/3)*3+1]) | (puzzle[(i/3)*3+2][(j/3)*3+1]) 
                                | (puzzle[(i/3)*3][(j/3)*3+2]) | (puzzle[(i/3)*3+1][(j/3)*3+2]) | (puzzle[(i/3)*3+2][(j/3)*3+2]));
      }
    }
  }
}


bool Solver::FillCandidates(int puzzle[][9], int candidates[][9], int& remaining_cells){
  for (int i=0; i<9;i++){
    for(int j=0; j<9; j++){
      if( puzzle[i][j] | candidates[i][j] > 0){ // If a blank puzzle cell has candidates
          if(NUMS.contains(candidates[i][j])){
              puzzle[i][j] = candidates[i][j];
              candidates[i][j] = 0;
              remaining_cells -= 1;
              UpdateCandidates(puzzle, candidates, i, j);
          }
      }else return false;    // If a blank puzzle cell has no candidates
    }
  }
  return true;
}


void Solver::UpdateCandidates(int puzzle[][9], int candidates[][9], int r, int c){
  int filled_val_inverse = 511-puzzle[r][c];
  
  for (int k=0; k<9; k++){
    if (puzzle[k][c] == 0) candidates[k][c] &= filled_val_inverse;
    if (puzzle[r][k] == 0) candidates[r][k] &= filled_val_inverse;
  }
          
  for (int i =(r/3)*3; i < (r/3)*3+3; i++){
    for (int j = (c/3)*3; j<(c/3)*3+3; j++){
      if ((i == r) || (j == c) || (puzzle[i][j] > 0)) continue;
      candidates[i][j] &= filled_val_inverse;
    }
  }
        
}


bool Solver::FindHiddenSingles(int candidates[][9]){
  bool hs_available = false;
  int candidate, row_candidates, col_candidates, block_candidates;
  int remaining_candidate, ib, jb;

  for (int i=0; i<9;i++){
    for(int j=0; j<9; j++){
      if (std::popcount((unsigned int)candidates[i][j])>1){
        candidate = candidates[i][j];
        candidates[i][j] = 0;
        
        row_candidates = candidates[i][0] | candidates[i][1] | candidates[i][2] | candidates[i][3] | candidates[i][4] | candidates[i][5] | candidates[i][6] | candidates[i][7] | candidates[i][8];
        remaining_candidate = candidate & (511-row_candidates);
        if (NUMS.contains(remaining_candidate)){
          candidates[i][j] = remaining_candidate;
          hs_available = true;
          continue;
        }

        col_candidates = candidates[0][j] | candidates[1][j] | candidates[2][j] | candidates[3][j] | candidates[4][j] | candidates[5][j] | candidates[6][j] | candidates[7][j] | candidates[8][j];
        remaining_candidate = candidate & (511-col_candidates);
        if (NUMS.contains(remaining_candidate)){
          candidates[i][j] = remaining_candidate;
          hs_available = true;
          continue;
        }

        ib = (i/3)*3;
        jb = (j/3)*3;
        block_candidates = candidates[ib][jb] | candidates[ib][jb+1] | candidates[ib][jb+2] | candidates[ib+1][jb] | candidates[ib+1][jb+1] | candidates[ib+1][jb+2] | candidates[ib+2][jb] | candidates[ib+2][jb+1] | candidates[ib+2][jb+2];
        remaining_candidate = candidate & (511-block_candidates);
        if (NUMS.contains(remaining_candidate)){
          candidates[i][j] = remaining_candidate;
          hs_available = true;
          continue;
        }

        candidates[i][j] = candidate;
      }
    }
  }

  return hs_available;
}


void Solver::getBranchingPosition(int candidates[][9], int& ib, int& jb){
  int num_candidates = 0;
  int num_candidates_min = 9;
  for (int i=0; i<9;i++){
    for(int j=0; j<9; j++){
      num_candidates = std::popcount((unsigned int)candidates[i][j]);
      if (1 < num_candidates && num_candidates < num_candidates_min){
          ib = i;
          jb = j;
          num_candidates_min = num_candidates;
          if (num_candidates == 2) 
              return;
      }
    }
  }
}