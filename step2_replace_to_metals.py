import os
import numpy as np
from scipy.spatial import distance_matrix

# Directories
xyz_dir = './big_xyz'
output_dir = './pedaling_ghosts'
os.makedirs(output_dir, exist_ok=True)

# Thresholds
cn_identification_threshold = 1.3  # Bond length for identifying central C-N
cn_deletion_threshold = 1.8        # Bond length for deleting connected central molecule

# Function to calculate the distance between two points
def calculate_distance(point1, point2):
    return np.linalg.norm(point1 - point2)

# Function to process each .xyz file
def process_xyz_file(filepath):
    with open(filepath, 'r') as file:
        lines = file.readlines()

        # Read atom data
        atom_count = int(lines[0].strip())
        atoms = [(line.split()[0], np.array(list(map(float, line.split()[1:4]))))
                 for line in lines[2:2 + atom_count]]

        coords_array = np.array([coord for _, coord in atoms])
        dist_matrix = distance_matrix(coords_array, coords_array)

        # Find central C-N pairs based on identification threshold
        cn_pairs = []
        for i, (atom1, coord1) in enumerate(atoms):
            if atom1 != 'C':
                continue
            for j, (atom2, coord2) in enumerate(atoms):
                if atom2 == 'N' and i != j and dist_matrix[i, j] < cn_identification_threshold:
                    cn_pairs.append((i, j))

        # Handle multiple or no C-N pairs
        if len(cn_pairs) == 0:
            print(f"No central C-N pair found in {filepath}")
            return
        elif len(cn_pairs) > 1:
            # Find the most central C-N pair
            center_coord = np.mean(coords_array, axis=0)
            central_pair = min(cn_pairs, key=lambda pair: calculate_distance(
                (atoms[pair[0]][1] + atoms[pair[1]][1]) / 2, center_coord))
        else:
            central_pair = cn_pairs[0]  # Only one pair

        central_c_index, central_n_index = central_pair

        # Depth-first search to find the connected central molecule
        visited = set()

        def find_connected_atoms(start_idx):
            """Recursively find connected atoms within the deletion threshold."""
            molecule = []
            stack = [start_idx]
            while stack:
                idx = stack.pop()
                if idx not in visited:
                    visited.add(idx)
                    molecule.append(idx)
                    for neighbor_idx in range(len(atoms)):
                        if neighbor_idx != idx and dist_matrix[idx, neighbor_idx] < cn_deletion_threshold:
                            stack.append(neighbor_idx)
            return molecule

        # Find the central molecule connected to both central C and N atoms
        central_molecule = set(find_connected_atoms(central_c_index)).union(
            find_connected_atoms(central_n_index)
        )

        # Identify the atom closest to Carbon
        closest_to_c_index = min(
            (idx for idx in central_molecule if idx != central_c_index),
            key=lambda idx: dist_matrix[central_c_index][idx],
            default=None
        )

        # Prepare for replacement
        c_coord = atoms[central_c_index][1]
        n_coord = atoms[central_n_index][1]
        fe_coord = atoms[closest_to_c_index][1] if closest_to_c_index is not None else c_coord

        # Remove central molecule atoms
        modified_atoms = [(atom, coord) for i, (atom, coord) in enumerate(atoms) if i not in central_molecule]

        # Add Ni, Co, Fe replacements
        modified_atoms.extend([
            ('Co', c_coord),  # Replace C with Co
            ('Ni', n_coord),  # Replace N with Ni
            ('Fe', fe_coord)  # Replace closest atom to C with Fe
        ])

        # Save the modified molecule to a new .xyz file
        output_filepath = os.path.join(output_dir, os.path.basename(filepath))
        with open(output_filepath, 'w') as output_file:
            output_file.write(f"{len(modified_atoms)}\n")
            output_file.write(f"Modified molecule from {os.path.basename(filepath)}\n")
            for atom_type, coord in modified_atoms:
                output_file.write(f"{atom_type} {coord[0]} {coord[1]} {coord[2]}\n")

        print(f"Processed file: {os.path.basename(filepath)}")

# Process all .xyz files in the input directory
for filename in os.listdir(xyz_dir):
    if filename.endswith('.xyz'):
        process_xyz_file(os.path.join(xyz_dir, filename))
