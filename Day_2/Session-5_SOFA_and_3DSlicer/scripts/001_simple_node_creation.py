# Scrip: 001_simple_node_creation.py (ctrl+g in slicer)

# Create a model node (Method I)
modelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode')

# Create a model node (Method II)
modelNode = slicer.vtkMRMLModelNode()
slicer.mrmlScene.AddNode(modelNode)

# Create display node (regardless of the method)
print(modelNode)
