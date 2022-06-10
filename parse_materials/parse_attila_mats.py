import openmc

mcnp_input = '../mcnp/libra1.mcnp.i'

cells, surfaces, data = openmc.model.mcnp.parse(mcnp_input)

mcnp_materials = openmc.model.mcnp.get_openmc_materials(data['materials'])

mcnp_materials

material_names = {1 : 'Steel_1',
                  2 : 'Copper_2',
                  3 : 'PortlandConc_3',
                  4 : 'Air_4',
                  5 : 'Be_5',
                  6 : 'Lead_6',
                  7 : 'firebrick_7',
                  8 : 'Flibe_natural_8',
                  9 : 'aluminum_9',
                  10 : 'plastic_10'}

def parse_material_assignments(mcnp_input):
    lines_per_entry = 13

    with open(mcnp_input, 'r') as inp:
        lines = inp.readlines()

    # find line index for start of attila info
    attila_regions = None
    for start_idx, line in enumerate(lines):
        if 'Number of Attila Regions' in line:
            attila_regions = int(line.split(':')[-1].strip())
        if 'Mesh Region/Pseudo-Cell Information' in line:
            break
    assert attila_regions is not None

    assignments = []

    idx = start_idx

    for i in range(attila_regions):

         # get the lines for the next assignment
        assignment_lines = []
        while True:
            idx += 1
            line = lines[idx]
            if 'c' == line.strip():
                break
            assignment_lines.append(line)

        assignment = {}
        for line in assignment_lines:
            if 'Mesh Data' in line:
                continue
            if 'c' == line.strip():
                break
            try:
                value, key = line[1:].split(':')
            except ValueError as e:
                print('Broken line {}'.format(line))
                raise e

            assignment[value.strip().replace('"','')] = key.strip().replace('"', '')
        assignments.append(assignment)

    return assignments
material_assignments = parse_material_assignments(mcnp_input)

final_materials = openmc.Materials()
for assignment in material_assignments:
    if 'void' in assignment['Material'].lower():
        continue
    mat_name = assignment['Attila Region Name'].upper()
    material_id = int(assignment['MCNP Material'][1:])
    rho_val, rho_units = assignment['Density'].split(' ')

    new_mat = mcnp_materials[material_id].clone()
    new_mat.name = mat_name
    new_mat.set_density(rho_units, float(rho_val))
    final_materials.append(new_mat)

final_materials.export_to_xml()
