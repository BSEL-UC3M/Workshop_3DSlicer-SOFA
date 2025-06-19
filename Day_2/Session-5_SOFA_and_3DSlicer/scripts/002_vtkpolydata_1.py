# Script: 002_vtkpolydata_1.py (ctrl+g in slicer)
#   requires the SlicerSOFA extension

# Load the dataset
import SampleData
liverScene = SampleData.downloadSample('LiverSimulationScene')

# Get model from MRML Scene
modelNode = slicer.util.getNode('liver_dec')

# Get polydata from model
polyData = modelNode.GetPolyData()

# Iterate over points in the mesh (geometry)
for i in range(polyData.GetNumberOfPoints()):
    print(polyData.GetPoint(i))

# Iterate over cells in the mesh (topology)
for i in range(polyData.GetNumberOfCells()):
    print(polyData.GetCellType(i),
          polyData.GetCell(i).GetPointId(0),
          polyData.GetCell(i).GetPointId(1),
          polyData.GetCell(i).GetPointId(2))
