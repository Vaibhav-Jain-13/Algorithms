import tkinter as tk
from tkinter import filedialog
import re
import ast
import os

def parse_gcode(gcode):
    commands = []
    for line in gcode.split('\n'):
        line = line.strip()     # Removes the empty spaces
        if line and not line.startswith(';'):
            # Ignore comments starting with ';'
            line = line.split(';')[0].strip()
            parts = line.split()
            command = parts[0]
            params = parts[1:]
            commands.append((command, params))
    return commands

# Open a dialog box to ask for the path of the input G-code file
root = tk.Tk()
root.withdraw()  # Hide the root window
input_file_path = filedialog.askopenfilename(title="Select the input G-code file", filetypes=[("Text Files", "*.txt")])

# Read the input G-code from the selected file
with open(input_file_path, 'r') as file:
    gcode_program = file.read()

# Parse the G-code
parsed_commands = parse_gcode(gcode_program)

# Uncomment the following lines if you want to save the parsed commands to a file
# output_file_path = filedialog.asksaveasfilename(title="Save the parsed commands as", defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
# with open(output_file_path, 'w') as file:
#     file.write(str(parsed_commands))

def coordinate_code(gcode,rapid_feed):
    
    l1 = list(gcode)
    toolpath = [[] for _ in range(len(l1))]  # Initialize toolpath with empty sublists
    i = 0
    for line in l1:
        # Toolpath for rapid move G00
        if line[0] == "G00":
            toolpath[i].append([0.0, 0.0, 0.0])
            toolpath[i].append(rapid_feed)
            for element in line[1]:
                input_string = element
                match = re.match(r'([A-Za-z]+)(-?\d+(\.\d+)?)', input_string)
                if match:
                    number = (match.group(2))
                    
                    string_part = match.group(1)
                    if string_part == "X":
                        toolpath[i][0][0] = float(number)
                    if string_part == "Z":
                        toolpath[i][0][2] = float(number)
            i += 1
        # Toolpath for linear interpolation G01
        elif line[0] == "G01":
            toolpath[i].append([0.0, 0.0, 0.0])
            toolpath[i].append(0.0)
            for element in line[1]:
                input_string = element
                match = re.match(r'([A-Za-z]+)(-?\d+(\.\d+)?)', input_string)
                if match:
                    number = (match.group(2))
                    string_part = match.group(1)
                    if string_part == "X":
                        toolpath[i][0][0] = float(number)
                    if string_part == "Z":
                        toolpath[i][0][2] = float(number)
                    if string_part == "F":
                        toolpath[i][1] = float(number)
            i += 1
    # Remove empty sublists
    toolpath = [sublist for sublist in toolpath if sublist]
    print(toolpath)
    return toolpath

# Parse the G-code
rapid_feed = int(input("Give the value of the rapid feed of the machine:"))
coordinate_commands = coordinate_code(parsed_commands,rapid_feed)

# Open a dialog box to ask for the save location of the output file
output_file_path = filedialog.asksaveasfilename(title="Save the parsed commands as", defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
with open(output_file_path, 'w') as file:
    file.write(str(coordinate_commands))

print(f"Coordinate commands have been written to {output_file_path}")
# Open the file automatically
os.startfile(output_file_path)