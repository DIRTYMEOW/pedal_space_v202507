# pedal_space_v202507<br>
Analyze *.cif (single crystal) of acyl salicylhydrazone to identify free space for pedaling<br>
Download and install anaconda<br>
pip3 everything needed to run step1-3 in anaconda<br>
use anaconda to open terminal<br>
place *.cif of acylsalicylhydrazone in /single_crystal<br>
in anaconda, open terminal, "python step1_grep_cif_to_xyz.py", to generate supercells, output in /big_xyz<br>
"python step2_replace_to_metals.py" to output in/pedaling_ghosts, cenetral molecule will be removed and pedaling moiety will be replaced with three metallic atoms for positioning. t0.xyz is complete cheese, just a check point, see if a free cheese has the right volume. Manual checking of correct positioning of indexing metals is crucial.<br> If not correctly indexed, modify cn_identification_min = 1.yy & cn_identification_max = 1.xx to precisely locate the C=N<br>


"python step3_pillar_void.py" to calculate the pedaling cheese size. Multiprocessing function may heat up laptop. Larger volume takes longer.<br>

d05223110@ntu.edu.tw for code modification or questions.<br>
