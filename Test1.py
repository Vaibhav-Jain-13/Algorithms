import FreeCAD
import Path
import PartDesignGui
import Path.Main.Gui.Job
import PathScripts.PathProfile as PathProfile
import PathScripts.PathToolBit as PathToolBit
import PathScripts.PathToolController as PathToolController

# Your existing script follows...


# Create a new document
doc = FreeCAD.newDocument("CNC_Toolpath")

# Add a simple part (e.g., a box)
box = doc.addObject("Part::Box", "Box")
box.Length = 50
box.Width = 50
box.Height = 10

# Open CAM
Gui.activateWorkbench("CAMWorkbench")
import PartDesignGui

# Create a job for the part
job = Path.Main.Gui.Job.Create(['Box'], None)
import Path.Main.Gui.Job

import Path.Main.Job

#Profile Command
Gui.runCommand('CAM_Profile',0)

#CAM Simulator
Gui.runCommand('CAM_SimulatorGL',0)

#Saving G-code
Gui.Selection.addSelection('Unnamed','Job')
Gui.runCommand('CAM_Post',0)


