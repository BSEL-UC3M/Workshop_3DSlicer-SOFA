# Script: 008_example_1.py
#  - requires SlicerSOFA
#  - requires adjusting path for mesh files

import numpy as np
import Sofa
import Sofa.Core
import Sofa.Simulation

from slicer.util import arrayFromModelPoints
from slicer.util import arrayFromModelPolyIds # For Polydata cells
from SlicerSofaUtils.Mappings import (
    arrayFromModelGridCells,             # To get tetrahedral unstructured grid cells
    arrayFromMarkupsROIPoints,           # To get ROI points from markups ROI node
    sofaMechanicalObjectToMRMLModelGrid  # Transfer mechanical object to unstructured grid
    )

############################################
###### Simulation Hyperparameters
############################################

# Input data parameters
liver_mesh_file = "/tmp/hackathon_liver_tetra.vtk"
roi_file = "/tmp/boundary.mrk.json"
liver_mesh_node = None
roi_node = None
sphereNode = None
liver_mass = 60.0
liver_youngs_modulus = 1.0 * 1000.0 * 0.001
liver_poisson_ratio = 0.45
force_vector = np.array([-1000.0, 0.0, 0.0])

# Simulatlon hyperparameters
root_node = None
dt = 0.01

# Simulation control parameters
iteration = 0
iterations = 30
simulating = True

##############################################
###### Load Simulation Data
############################################
def loadSimulationData():
    global liver_mesh_node, roi_node
    liver_mesh_node = slicer.util.loadModel(liver_mesh_file)
    roi_node = slicer.util.loadMarkups(roi_file)

############################################
###### Create Sofa Scene
############################################

# This simulation scene is largely based on the
# SoftTissueSimulation.py included in SlicerSOFA
def createSofaScene():
    global root_node, roi_node, force_vector

    # Initialize the root node of the SOFA scene
    root_node = Sofa.Core.Node("Root")

    # Initialize main scene headers with necessary plugins for SOFA components
    plugins=["Sofa.Component.IO.Mesh",
             "Sofa.Component.LinearSolver.Direct",
             "Sofa.Component.LinearSolver.Iterative",
             "Sofa.Component.Mapping.Linear",
             "Sofa.Component.Mass",
             "Sofa.Component.ODESolver.Backward",
             "Sofa.Component.Setting",
             "Sofa.Component.SolidMechanics.FEM.Elastic",
             "Sofa.Component.StateContainer",
             "Sofa.Component.Topology.Container.Dynamic",
             "Sofa.GL.Component.Rendering3D",
             "Sofa.Component.AnimationLoop",
             "Sofa.Component.Collision.Detection.Algorithm",
             "Sofa.Component.Collision.Detection.Intersection",
             "Sofa.Component.Collision.Geometry",
             "Sofa.Component.Collision.Response.Contact",
             "Sofa.Component.Constraint.Lagrangian.Solver",
             "Sofa.Component.Constraint.Lagrangian.Correction",
             "Sofa.Component.LinearSystem",
             "Sofa.Component.MechanicalLoad",
             "Sofa.Component.SolidMechanics.Spring",
             "Sofa.Component.Constraint.Lagrangian.Model",
             "Sofa.Component.Mapping.NonLinear",
             "Sofa.Component.Topology.Container.Constant",
             "Sofa.Component.Topology.Mapping",
             "Sofa.Component.Topology.Container.Dynamic",
             "Sofa.Component.Engine.Select",
             "Sofa.Component.Constraint.Projective",
             "MultiThreading",]

    for plugin_name in plugins:
         root_node.addObject("RequiredPlugin", name=plugin_name)

    # Set gravity vector for the simulation (no gravity in this case)

    # with root_node.gravity.writeable() as gravity:
    #     gravity[:] = force_vector.copy()
    root_node.gravity = [0, 1000, 0]

    # Add animation and constraint solver objects to the root node
    root_node.addObject('FreeMotionAnimationLoop', parallelODESolving=True, parallelCollisionDetectionAndFreeMotion=True)
    root_node.addObject('GenericConstraintSolver', maxIterations=10, multithreading=True, tolerance=1.0e-3)

    # Define a deformable Finite Element Method (FEM) object
    femNode = root_node.addChild('FEM')
    femNode.addObject('EulerImplicitSolver', firstOrder=False, rayleighMass=0.1, rayleighStiffness=0.1)
    femNode.addObject('SparseLDLSolver', name="precond", template="CompressedRowSparseMatrixd", parallelInverseProduct=True)
    femNode.addObject('TetrahedronSetTopologyContainer', name="Container",
                      position=slicer.util.arrayFromModelPoints(liver_mesh_node),
                      tetrahedra=arrayFromModelGridCells(liver_mesh_node))
    femNode.addObject('TetrahedronSetTopologyModifier', name="Modifier")
    femNode.addObject('MechanicalObject', name="mstate", template="Vec3d")
    femNode.addObject('TetrahedronFEMForceField', name="FEM", youngModulus=1.5, poissonRatio=0.45, method="large")
    femNode.addObject('MeshMatrixMass', totalMass=1)

    # Add a region of interest (ROI) with fixed constraints in the FEM node
    fixedROI = femNode.addChild('FixedROI')
    fixedROI.addObject('BoxROI', template="Vec3", box=arrayFromMarkupsROIPoints(roi_node), drawBoxes=False,
                       position="@../mstate.rest_position", name="BoxROI",
                       computeTriangles=False, computeTetrahedra=False, computeEdges=False)
    fixedROI.addObject('FixedConstraint', indices="@BoxROI.indices")

    # Set up collision detection within the FEM node
    collisionNode = femNode.addChild('Collision')
    collisionNode.addObject('TriangleSetTopologyContainer', name="Container")
    collisionNode.addObject('TriangleSetTopologyModifier', name="Modifier")
    collisionNode.addObject('Tetra2TriangleTopologicalMapping', input="@../Container", output="@Container")
    collisionNode.addObject('TriangleCollisionModel', name="collisionModel", proximity=0.001, contactStiffness=20)
    collisionNode.addObject('MechanicalObject', name='dofs', rest_position="@../mstate.rest_position")
    collisionNode.addObject('IdentityMapping', name='visualMapping')

    # Apply a linear solver constraint correction in the FEM node
    femNode.addObject('LinearSolverConstraintCorrection', linearSolver="@precond")

    # Initialize the simulation
    Sofa.Simulation.init(root_node)

############################################
###### Update Simulation
############################################
def updateSimulation():
    global iteration, iterations, simulating, root_node, liver_mesh_node

    Sofa.Simulation.animate(root_node, root_node.dt.value)

    # Transfer new coordinates from sofa mechanical object to slicer MRML model node
    sofaMechanicalObjectToMRMLModelGrid(liver_mesh_node, root_node['FEM.mstate'])

    # This is needed to notify slicer that changes to the mesh have occurred
    slicer.util.arrayFromModelPointsModified(liver_mesh_node)

    # iteration management
    iteration += 1
    simulating = iteration < iterations
    if iteration % 10 == 0:
        print(f"Iteration {iteration}")
    if simulating:
        qt.QTimer.singleShot(10, updateSimulation)
    else:
        print("Simlation stopped")

############################################
###### Execution flow
############################################

# This will clear the scene, in case we want to
# load the script over and over in the same Slicer instance
slicer.mrmlScene.Clear()

loadSimulationData()
createSofaScene()
updateSimulation()
