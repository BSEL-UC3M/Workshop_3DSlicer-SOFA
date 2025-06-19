# Script: 003_vtkunstructuredgrid_1.py (ctrl+g in slicer)
#   requires the SlicerSOFA extension

# Load the dataset
import SampleData
liverScene = SampleData.downloadSample('RightLungLowTetra')

# Get model from MRML Scene
modelNode = slicer.util.getNode('RightLung')

# Get polydata from model
unstructuredGrid = modelNode.GetMesh()

# Iterate over points in the mesh (geometry)
for i in range(unstructuredGrid.GetNumberOfPoints()):
    print(unstructuredGrid.GetPoint(i))

# Iterate over cells in the mesh (topology)
for i in range(unstructuredGrid.GetNumberOfCells()):
    print(unstructuredGrid.GetCellType(i),
          unstructuredGrid.GetCell(i).GetPointId(0),
          unstructuredGrid.GetCell(i).GetPointId(1),
          unstructuredGrid.GetCell(i).GetPointId(2),
          unstructuredGrid.GetCell(i).GetPointId(3))
