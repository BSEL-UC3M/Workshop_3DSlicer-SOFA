# Script: 005_sofa_nodex.py (ctrl+g in slicer)
#   requires the SlicerSOFA extension
import Sofa.Core
import numpy as np

#Create the root node
rootNode = Sofa.Core.Node('root')

plugins=["Sofa.Component.IO.Mesh",
         "Sofa.Component.StateContainer",
         "Sofa.Component.Mapping.NonLinear",
         "Sofa.Component.Topology.Container.Constant",
         "Sofa.Component.Topology.Mapping",
         #Other plugins
         ]

for plugin_name in plugins:
    rootNode.addObject('RequiredPlugin', name=plugin_name)


inputNode = rootNode.addChild('InputSurfaceNode')
container = inputNode.addObject('TriangleSetTopologyContainer',
                                name='Container',
                                position=np.zeros(10*3).reshape(-1,3),
                                triangles=np.zeros(100))
