import os
import numpy as np
import trimesh
import multiprocessing

# Directories
input_dir = './pedaling_ghosts'
output_dir = './output'

# Cylinder parameters
cylinder_heights = 1.5  # Ångstroms
cylinder_radius_range = np.arange(2.7, 2.71, 0.1)  # Radii from 2.5 to 2.6 Å with 0.1 interval

# Van der Waals radii (excluding Ni, Co, Fe for volume calculation)
vdw_radii = {
    'H': 1.2, 'C': 1.7, 'N': 1.55, 'O': 1.52,
    'F': 1.47, 'Cl': 1.75, 'Br': 1.85, 'I': 1.98,
    'S': 1.8, 'P': 1.8
}

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

def create_cylinder(center, co_ni_vector, co_fe_vector, radius, height, segments=256):
    # Function to create the cylinder mesh (same as before)
    co_ni_normalized = co_ni_vector / np.linalg.norm(co_ni_vector)
    co_fe_normalized = co_fe_vector / np.linalg.norm(co_fe_vector)
    average_vector = (co_ni_normalized + co_fe_normalized) / 2
    axis = average_vector / np.linalg.norm(average_vector)

    cylinder = trimesh.creation.cylinder(radius, height, sections=segments)
    cylinder.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], axis))
    cylinder.apply_translation(center)
    return cylinder

def calculate_unoccupied_volume(cylinder_mesh, atom_meshes):
    # Function to calculate unoccupied volume (same as before)
    modified_cylinder = cylinder_mesh
    for atom_mesh in atom_meshes:
        try:
            modified_cylinder = trimesh.boolean.difference([modified_cylinder, atom_mesh])
        except Exception as e:
            print(f"Warning: Boolean difference failed for one atom: {e}")
    return modified_cylinder.volume, modified_cylinder

def process_file(filepath):
    # Function to process a single .xyz file for all radii and save results (same as before)
    with open(filepath, 'r') as file:
        lines = file.readlines()
        atom_count = int(lines[0].strip())
        atoms = [
            (parts[0], np.array([float(parts[1]), float(parts[2]), float(parts[3])]))
            for parts in (line.split() for line in lines[2:2 + atom_count])
        ]

    # Identify Co, Ni, and Fe positions
    co_coord = next(coord for atom, coord in atoms if atom == 'Co')
    ni_coord = next(coord for atom, coord in atoms if atom == 'Ni')
    fe_coord = next(coord for atom, coord in atoms if atom == 'Fe')

    # Calculate cylinder midpoint
    midpoint = (co_coord + ni_coord) / 2
    co_ni_vector = ni_coord - co_coord
    co_fe_vector = fe_coord - co_coord

    # Create atom meshes
    atom_meshes = []
    for atom, coord in atoms:
        if atom in vdw_radii:
            sphere = trimesh.creation.icosphere(radius=vdw_radii[atom], subdivisions=3)
            sphere.apply_translation(coord)
            atom_meshes.append(sphere)

    # Process each radius
    results = []
    for radius in cylinder_radius_range:
        cylinder_mesh = create_cylinder(midpoint, co_ni_vector, co_fe_vector, radius, cylinder_heights)
        unoccupied_volume, caved_cylinder = calculate_unoccupied_volume(cylinder_mesh, atom_meshes)

        # Set cylinder color to (1.0, 0.9, 0.0, 1.0)
        caved_cylinder.visual.face_colors = [255 * 1.0, 255 * 0.9, 255 * 0.0, 255]

        # Save caved cylinder mesh as .glb and .obj
        output_filename_glb = os.path.join(
            output_dir,
            f"{os.path.basename(filepath).replace('.xyz', '')}_r{radius:.1f}_cylinder.glb"
        )
        output_filename_obj = os.path.join(
            output_dir,
            f"{os.path.basename(filepath).replace('.xyz', '.obj')}"
        )

        caved_cylinder.export(output_filename_glb, file_type='glb')
        caved_cylinder.export(output_filename_obj, file_type='obj')

        # Store results for this radius
        results.append((radius, unoccupied_volume, filepath, output_filename_glb, output_filename_obj))

    return results

def process_all_files(input_dir):
    # Function to process all files in the input directory using multiprocessing (same as before)
    xyz_files = [os.path.join(input_dir, filename) for filename in os.listdir(input_dir) if filename.endswith('.xyz')]

    # Use multiprocessing to process the files in parallel
    with multiprocessing.Pool() as pool:
        all_results = pool.map(process_file, xyz_files)

    # Flatten the results list
    flat_results = [item for sublist in all_results for item in sublist]
    return flat_results

def write_cheese_dtm(results, output_filename):
    # Write the results to the cheese.dtm file
    with open(output_filename, 'w') as f:
        for radius in cylinder_radius_range:
            f.write(f"radius={radius:.1f}\n")
            for volume, filepath, output_filepath_glb, output_filepath_obj in results:
                if volume == radius:
                    f.write(f"{filepath} {volume:.2f}\n")

if __name__ == "__main__":
    # Process all .xyz files in the input directory
    all_results = process_all_files(input_dir)

    # Group results by radius
    grouped_results = {radius: [] for radius in cylinder_radius_range}
    for radius, volume, filepath, output_filepath_glb, output_filepath_obj in all_results:
        grouped_results[radius].append((volume, filepath, output_filepath_glb, output_filepath_obj))

    # Sort results by volume within each radius
    for radius in grouped_results:
        grouped_results[radius].sort(key=lambda x: x[0])  # Sort by volume

    # Flatten the grouped results
    flat_results = [item for sublist in grouped_results.values() for item in sublist]

    # Write results to cheese.dtm
    write_cheese_dtm(flat_results, os.path.join(output_dir, 'cheese.dtm'))

    # Print results
    print("\nSorted Unoccupied Volumes by Radius:")
    for radius in sorted(grouped_results.keys()):
        print(f"\nRadius: {radius:.1f} Å")
        for volume, filepath, output_filepath_glb, output_filepath_obj in grouped_results[radius]:
            print(f"  File: {filepath}, Unoccupied Volume: {volume:.2f} Å³")

