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
rootNode.dt = 0.1
with container.position.writeable() as geometry:
    geometry[:] = np.random.rand(10*3).reshape(-1,3) #Note: Copy!!
    geometry[0][0] = 10
