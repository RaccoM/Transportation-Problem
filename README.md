# Transportation Simplex Method

This project implements the Transportation Simplex Method to solve transportation problems.

## Description

This Python program solves transportation problems using the Transportation Simplex Method. It reads a CSV file containing the supply, demand, and cost matrices, calculates the optimal solution, and outputs the solution  with the total cost.

The CSV file should have the following structure:
- The cost matrix is the main part of the file.
- The last column contains the supply values.
- The last row contains the demand values.

### Example CSV format:

8;6;10;9;35
9;12;13;7;50
14;9;16;5;40
45;20;30;30

## How it works

1. **Input**: The program reads the CSV file to extract the supply, demand, and cost data. (Here are some example with "matrix" and "matrix 2"
2. **North-West Corner Method**: The program starts by finding an initial feasible solution using the North-West Corner Method.
3. **Transportation Simplex Method**: The program then uses the Transportation Simplex Method to iteratively improve the solution by finding loops and pivoting.
4. **Output**: The optimal solution and the total transportation cost are printed.
