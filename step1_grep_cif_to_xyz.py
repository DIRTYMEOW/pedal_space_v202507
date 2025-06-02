import os
import numpy as np
from ase.io import read, write

# Define input and output directories
input_directory = 'single_crystal'  # Directory containing CIF files
output_directory = 'big_xyz'         # Directory to save XYZ files

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Define the desired dimensions in Angstroms
desired_dimensions = np.array([30, 30, 30])  # Dimensions for the supercell in Ångströms

# Loop through all .cif files in the input directory
for filename in os.listdir(input_directory):
    if filename.endswith('.cif'):
        input_file = os.path.join(input_directory, filename)
        output_file = os.path.join(output_directory, filename.replace('.cif', '.xyz'))  # Change extension

        # Read the CIF file
        atoms = read(input_file)

        # Get the current cell dimensions
        cell = atoms.get_cell()

        # Calculate the number of unit cells needed in each direction
        num_cells = np.ceil(desired_dimensions / np.array([cell[0, 0], cell[1, 1], cell[2, 2]])).astype(int)

        # Repeat the unit cell to create a supercell
        atoms = atoms.repeat(tuple(num_cells))

        # Write the XYZ file in standard format
        comment = "Generated from CIF file"

        # Write the XYZ file
        write(output_file, atoms, format='xyz', comment=comment)

        print(f"Successfully saved {input_file} as {output_file}.")
