# pedal_space_v202507
Analyze *.cif (single crystal) of acyl salicylhydrazone to identify free space for pedaling
Download and install anaconda
pip3 everything needed to run step1-3 in anaconda
use anaconda to open terminal
place *.cif of acylsalicylhydrazone in /single_crystal
in anaconda, open terminal, "python step1_grep_cif_to_xyz.py", to generate supercells, output in /big_xyz
"python step2_replace_to_metals.py" to output in/pedaling_ghosts, cenetral molecule will be removed and pedaling moiety will be replaced with three metallic atoms for positioning. t0.xyz is complete cheese, just a check point, see if a free cheese has the right volume. Manual checking of correct positioning of indexing metals is crucial. If not correctly indexed, modify cn_identification_min = 1.yy & cn_identification_max = 1.xx to precisely locate the C=N


"python step3_pillar_void.py" to calculate the pedaling cheese size. Multiprocessing function may heat up laptop. Larger volume takes longer.

d05223110@ntu.edu.tw for code modification or questions.
