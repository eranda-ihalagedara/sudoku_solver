#ifndef SOLVER_H
#define SOLVER_H

#include <iostream> 
#include <string>
#include <unordered_set>
#include <unordered_map>

class Solver {
    public:
        Solver()=default;
        ~Solver(){};
        void Solve(int puzzle[][9]);
        void IntToBitwise(int puzzle[][9]);

    protected:
        // void IntToBitwise(int puzzle[][9]);
        void BitwiseToInt(int puzzle[][9]);
        void PrintPuzzle(int puzzle[][9]);
        int SolveSudoku(int puzzle[][9],int candidates[][9], int& remaining_cells);
        void getCandidates(int puzzle[][9], int candidates[][9]);
        bool FillCandidates(int puzzle[][9], int candidates[][9], int& remaining_cells);
        void UpdateCandidates(int puzzle[][9], int candidates[][9], int r, int c);
        bool FindHiddenSingles(int candidates[][9]);
        void getBranchingPosition(int candidates[][9], int& ib, int& jb);

    private:
        std::unordered_set<int> NUMS = {1, 2, 4, 8, 16, 32, 64, 128, 256};
        std::unordered_map<int,int> bitwisemap = {{4,3}, {8,4}, {16,5}, {32,6}, {64,7}, {128,8}, {256,9}};

};

#endif