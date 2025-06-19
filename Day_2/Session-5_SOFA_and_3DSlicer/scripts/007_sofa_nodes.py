# Script: 007_sofa_nodes.py (ctrl+g in slicer)
#   requires the SlicerSOFA extension
import Sofa.Core
import numpy as np

#Create the root node
rootNode = Sofa.Core.Node('root')

# Required plugins can be added here

inputNode = rootNode.addChild('InputSurfaceNode')
container = inputNode.addObject('TriangleSetTopologyContainer',
                                name='Container', position=np.zeros(10*3).reshape(-1,3),
                                triangles=np.zeros(100))

# Access to container geometry
print(container.position.array())
print(rootNode['InputSurfaceNode']['Container']['position'].array())
print(rootNode['InputSurfaceNode.Container.position'].array())
