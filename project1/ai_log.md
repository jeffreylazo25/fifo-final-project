# Project 1 AI Log

I used ChatGPT to help with parts of my FIFO verification project, including the verification plan, directed testbench, constrained random testing, and coverage model. 
I asked it to work with the professor's FIFO specification and starter code while keeping the implementation simple. Some possible issues were missing coverage combinations,
incorrect scoreboard checks, and errors with the coverage model. The first coverage test failed because the occupancy coverpoint was not registered correctly before creating 
the cross. I corrected this by registering the coverpoints separately and rerunning the simulation. I also fixed a syntax error when adding different random seeds and updated 
the coverage test to reuse the driver, monitor, and scoreboard. After making these changes, the directed tests passed, including the reset test. The constrained random 
regression passed using seeds 1, 2, and 3, with 3,000 transactions per seed. The final coverage test reached 100% operation, occupancy, and cross coverage. 
The testbench also detected all 8 released mutants. Overall, AI helped with developing and organizing the testbench, but the code still needed to be tested and corrected. 
I verified the results using the simulation logs, coverage reports, and mutation testing.

**Evidence:** `directed_final.log`, `crv_seed1.log`, `crv_seed2.log`, `crv_seed3.log`, `coverage_final_layered.log`, and `mutation_layered.log` in the `evidence/` folder.
