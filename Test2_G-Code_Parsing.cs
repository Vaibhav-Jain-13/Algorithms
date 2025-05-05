using System;
using System.Collections.Generic;
using System.IO;
using System.Text.RegularExpressions;
using System.Windows.Forms;

public class GCodeParser
{
    public static List<(string, List<string>)> ParseGCode(string gcode)
    {
        var commands = new List<(string, List<string>)>();
        foreach (var line in gcode.Split('\n'))
        {
            var trimmedLine = line.Trim();
            if (!string.IsNullOrEmpty(trimmedLine) && !trimmedLine.StartsWith(";"))
            {
                var parts = trimmedLine.Split(';')[0].Trim().Split();
                var command = parts[0];
                var parameters = new List<string>(parts[1..]);
                commands.Add((command, parameters));
            }
        }
        return commands;
    }

    [STAThread]
    public static void Main()
    {
        var openFileDialog = new OpenFileDialog
        {
            Title = "Select the input G-code file",
            Filter = "Text Files|*.txt"
        };

        string inputFilePath = string.Empty;
        if (openFileDialog.ShowDialog() == DialogResult.OK)
        {
            inputFilePath = openFileDialog.FileName;
        }

        var gcodeProgram = File.ReadAllText(inputFilePath);
        var parsedCommands = ParseGCode(gcodeProgram);

        // Uncomment the following lines if you want to save the parsed commands to a file
        // var saveFileDialog = new SaveFileDialog
        // {
        //     Title = "Save the parsed commands as",
        //     DefaultExt = "txt",
        //     Filter = "Text Files|*.txt"
        // };
        // if (saveFileDialog.ShowDialog() == DialogResult.OK)
        // {
        //     File.WriteAllText(saveFileDialog.FileName, string.Join("\n", parsedCommands));
        // }

        Console.Write("Give the value of the rapid feed of the machine: ");
        int rapidFeed = int.Parse(Console.ReadLine());
        var coordinateCommands = CoordinateCode(parsedCommands, rapidFeed);

        var saveFileDialog = new SaveFileDialog
        {
            Title = "Save the parsed commands as",
            DefaultExt = "txt",
            Filter = "Text Files|*.txt"
        };
        if (saveFileDialog.ShowDialog() == DialogResult.OK)
        {
            File.WriteAllText(saveFileDialog.FileName, string.Join("\n", coordinateCommands));
            Console.WriteLine($"Coordinate commands have been written to {saveFileDialog.FileName}");
            System.Diagnostics.Process.Start("explorer.exe", saveFileDialog.FileName);
        }
    }

    public static List<List<object>> CoordinateCode(List<(string, List<string>)> gcode, int rapidFeed)
    {
        var toolpath = new List<List<object>>();
        foreach (var line in gcode)
        {
            var sublist = new List<object> { new List<double> { 0.0, 0.0, 0.0 }, 0.0 };
            if (line.Item1 == "G00")
            {
                sublist[1] = rapidFeed;
                foreach (var element in line.Item2)
                {
                    var match = Regex.Match(element, @"([A-Za-z]+)(-?\d+(\.\d+)?)");
                    if (match.Success)
                    {
                        var number = double.Parse(match.Groups[2].Value);
                        var stringPart = match.Groups[1].Value;
                        if (stringPart == "X")
                        {
                            ((List<double>)sublist[0])[0] = number;
                        }
                        if (stringPart == "Z")
                        {
                            ((List<double>)sublist[0])[2] = number;
                        }
                    }
                }
            }
            else if (line.Item1 == "G01")
            {
                foreach (var element in line.Item2)
                {
                    var match = Regex.Match(element, @"([A-Za-z]+)(-?\d+(\.\d+)?)");
                    if (match.Success)
                    {
                        var number = double.Parse(match.Groups[2].Value);
                        var stringPart = match.Groups[1].Value;
                        if (stringPart == "X")
                        {
                            ((List<double>)sublist[0])[0] = number;
                        }
                        if (stringPart == "Z")
                        {
                            ((List<double>)sublist[0])[2] = number;
                        }
                        if (stringPart == "F")
                        {
                            sublist[1] = number;
                        }
                    }
                }
            }
            toolpath.Add(sublist);
        }
        return toolpath;
    }
}

