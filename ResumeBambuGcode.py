import re
import os


def extract_block(lines, start_marker, end_marker):
    inside_block = False
    block = []
    for line in lines:
        if start_marker in line:
            inside_block = True
        if inside_block:
            block.append(line)
        if end_marker in line and inside_block:
            break
    return block


def find_layers(lines):
    layers = []
    for idx, line in enumerate(lines):
        if line.startswith('; Z_HEIGHT:'):
            z_height = float(line.split(':')[1].strip())
            layers.append((idx, z_height))
    return layers


def clean_wipe_sections(lines):
    cleaned = []
    inside_wipe = False
    for line in lines:
        if '; WIPE_START' in line:
            inside_wipe = True
            continue
        if '; WIPE_END' in line:
            inside_wipe = False
            continue
        if not inside_wipe:
            cleaned.append(line)
    return cleaned


def main():
    input_path = input('Enter path to original G-code file: ').strip()
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    with open(input_path, 'r') as f:
        lines = f.readlines()

    header = extract_block(lines, '; HEADER_BLOCK_START', '; HEADER_BLOCK_END')
    config = extract_block(lines, '; CONFIG_BLOCK_START', '; CONFIG_BLOCK_END')

    layers = find_layers(lines)
    if not layers:
        print("No layers found in G-code!")
        return

    target_height = float(input('Enter resume height (in mm): ').strip())

    # Find nearest layer
    closest_idx = min(range(len(layers)), key=lambda i: abs(layers[i][1] - target_height))
    chosen_idx = closest_idx

    while True:
        idx, z = layers[chosen_idx]
        print(f"Nearest Z height: {z}mm at line {idx}")
        choice = input("Accept (Enter), Up (u), Down (d)? ").strip().lower()
        if choice == '' or choice == 'y':
            break
        elif choice == 'u' and chosen_idx < len(layers) - 1:
            chosen_idx += 1
        elif choice == 'd' and chosen_idx > 0:
            chosen_idx -= 1
        else:
            print("Invalid input or out of bounds.")

    print(f"Try Home Z-axis (beta)?")
    choice = input("Yes (y), No (n)? ").strip().lower()
    if choice == 'y' or choice == 'yes':
        home = True
    else:
        home = False

    if home == True:
        while True:
            home_x = float(input(f"Enter X position for homing (in mm): ").strip())
            home_y = float(input(f"Enter Y position for homing (in mm): ").strip())
            print(f"Confirm X: {home_x}mm Y: {home_y}mm")
            choice = input("Yes (y), No (n)? ").strip().lower()
            if choice == 'y' or choice == 'yes':
                break

        

    start_idx = layers[chosen_idx][0]

    resume_block = [
        '; --- Resume print after failure ---\n',
        'M140 S65\n',
        'M104 S220\n',
        'M190 S65\n',
        'M109 S220\n',
        'M1002 set_gcode_claim_speed_level : 5\n',
        'M975 S1\n',
        'M981 S1 P20000\n',
        'M412 S1\n',
        'M73 P0 R300\n',
        'M106 P2 S100\n',
        'M106 P3 S180\n',
        'M221 X0 Y0 Z0\n',
        'G90\n',
        'M83\n',
        'G28 X Y\n',
        'G1 Z10 F3000\n',
        'G1 X125 Y125 F6000\n',
        f'G1 Z{layers[chosen_idx][1]} F300\n',
        'G92 E0\n',
        'G1 E5 F300\n',
        'G92 E0\n',
    ]

    resume_block_home = [
        '; --- Resume print after failure ---\n',
        'M140 S65\n',
        'M104 S220\n',
        'M190 S65\n',
        'M109 S220\n',
        'M1002 set_gcode_claim_speed_level : 5\n',
        'M975 S1\n',
        'M981 S1 P20000\n',
        'M412 S1\n',
        'M73 P0 R300\n',
        'M106 P2 S100\n',
        'M106 P3 S180\n',
        'M221 X0 Y0 Z0\n',
        'G90\n',
        'M83\n',
        'G28 X Y\n',
        f'G1 X{home_x} Y{home_y}\n',
        'G28 Z\n',
        f'G1 Z{layers[chosen_idx][1] + 10}\n',
        'G1 X125 Y125 F6000\n',
        f'G1 Z{layers[chosen_idx][1]} F300\n',
        'G92 E0\n',
        'G1 E5 F300\n',
        'G92 E0\n',
    ]

    remainder = lines[start_idx:]
    cleaned_remainder = clean_wipe_sections(remainder)

    base_name, ext = os.path.splitext(os.path.basename(input_path))
    output_name = f"{base_name}_resume_at_{str(layers[chosen_idx][1]).replace('.', '_')}mm.gcode"
    output_path = os.path.join(os.path.dirname(input_path), output_name)

    with open(output_path, 'w') as f:
        f.writelines(header)
        f.write('\n')
        f.writelines(config)
        f.write('\n')
        if home:
            f.writelines(resume_block_home)
        else:
            f.writelines(resume_block)
        f.write('\n')
        f.writelines(cleaned_remainder)

    print(f"Resume G-code saved to: {output_path}")


if __name__ == "__main__":
    main()
