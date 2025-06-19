# Script: 007_example_1.py
#  - requires SlicerSOFA
#  - requires adjusting path for mesh files

import numpy
import Sofa
import Sofa.Core
import Sofa.Simulation

from slicer.util import arrayFromModelPoints
from SlicerSofaUtils.Mappings import arrayFromModelGridCells

############################################
###### Simulation Hyperparameters
############################################

# Input data parameters
liver_mesh_file = "/tmp/originalMesh.vtk"
sphere_surface_file = "/tmp/biggerCavity.obj"
originalMeshNode = None
sphereNode = None
liver_mass = 30.0
liver_youngs_modulus = 1.0 * 1000.0 * 0.001
liver_poisson_ratio = 0.45

# Simulatlon hyperparameters
root = None
dt = 0.01
collision_detection_method = "LocalMinDistance"
alarm_distance = 10.0
contact_distance = 0.8

# Simulation control parameters
iteration = 0
iterations = 30
simulating = True

############################################
###### Load Simulation Data
############################################
def loadSimulationData():
    global originalMeshNode
    originalMeshNode = slicer.util.loadModel(liver_mesh_file)
    sphereNode = slicer.util.loadModel(sphere_surface_file)
    sphereNode.GetDisplayNode().SetRepresentation(slicer.vtkMRMLDisplayNode.WireframeRepresentation)

############################################
###### Create Sofa Scene
############################################
def createSofaScene():
    global root

    # Create a root node
    root = Sofa.Core.Node("root")

    plugin_list = [
        "MultiThreading",
        "Sofa.Component.AnimationLoop",
        "Sofa.Component.Collision.Detection.Algorithm",
        "Sofa.Component.Collision.Detection.Intersection",
        "Sofa.Component.Collision.Geometry",
        "Sofa.Component.Collision.Response.Contact",
        "Sofa.Component.Constraint.Lagrangian.Correction",
        "Sofa.Component.Constraint.Lagrangian.Solver",
        "Sofa.Component.IO.Mesh",
        "Sofa.Component.LinearSolver.Direct",
        "Sofa.Component.Mass",
        "Sofa.Component.MechanicalLoad",
        "Sofa.Component.ODESolver.Backward",
        "Sofa.Component.SolidMechanics.FEM.Elastic",
        "Sofa.Component.StateContainer",
        "Sofa.Component.Topology.Container.Dynamic",
        "Sofa.Component.Topology.Mapping",
        "Sofa.Component.Visual",
        "Sofa.Component.Constraint.Projective",
    ]
    for plugin in plugin_list:
        root.addObject("RequiredPlugin", name=plugin)

#def createSofaScene() continues
    # The simulation scene
    root.gravity = [-9.81 * 10.0, 0.0, 0.0]
    root.dt = dt

    root.addObject("FreeMotionAnimationLoop")
    root.addObject("VisualStyle", displayFlags=["showForceFields", "showBehaviorModels", "showCollisionModels", "showWireframe"])

    root.addObject("CollisionPipeline")
    root.addObject("ParallelBruteForceBroadPhase")
    root.addObject("ParallelBVHNarrowPhase")
    root.addObject(collision_detection_method, alarmDistance=alarm_distance, contactDistance=contact_distance)

    root.addObject("CollisionResponse", response="FrictionContactConstraint", responseParams=0.001)
    root.addObject("GenericConstraintSolver")

    scene_node = root.addChild("scene")

#def createSofaScene() continues
    #### Liver ####
    liver_node = scene_node.addChild("liver")

    liver_node.addObject('TetrahedronSetTopologyContainer', name="Container",
                         position=arrayFromModelPoints(originalMeshNode),
                         tetrahedra=arrayFromModelGridCells(originalMeshNode))

    liver_node.addObject("TetrahedronSetTopologyModifier")
    liver_node.addObject("EulerImplicitSolver")
    liver_node.addObject("SparseLDLSolver", template="CompressedRowSparseMatrixMat3x3d")
    liver_node.addObject("MechanicalObject")
    liver_node.addObject("TetrahedralCorotationalFEMForceField", youngModulus=liver_youngs_modulus, poissonRatio=liver_poisson_ratio)
    liver_node.addObject("UniformMass", totalMass=liver_mass)
    liver_node.addObject("LinearSolverConstraintCorrection")

    liver_collision_node = liver_node.addChild("collision")
    liver_collision_node.addObject("TriangleSetTopologyContainer")
    liver_collision_node.addObject("TriangleSetTopologyModifier")
    liver_collision_node.addObject("Tetra2TriangleTopologicalMapping")
    liver_collision_node.addObject("PointCollisionModel")
    liver_collision_node.addObject("LineCollisionModel")
    liver_collision_node.addObject("TriangleCollisionModel")

#def createSofaScene() continues
    #### Sphere ####
    sphere_node = scene_node.addChild("sphere")
    sphere_node.addObject("MeshOBJLoader", filename=sphere_surface_file, scale=1.0)
    sphere_node.addObject("TriangleSetTopologyContainer", src=sphere_node.MeshOBJLoader.getLinkPath())
    sphere_node.addObject("TriangleSetTopologyModifier")
    sphere_node.addObject("MechanicalObject")
    # NOTE: The important thing is to set bothSide=True for the collision models, so that both sides of the triangle are considered for collision.
    sphere_node.addObject("TriangleCollisionModel", bothSide=True)
    sphere_node.addObject("PointCollisionModel")
    sphere_node.addObject("LineCollisionModel")
    sphere_node.addObject("FixedProjectiveConstraint")

#def createSofaScene() continues

    # Initialize the simulation
    Sofa.Simulation.init(root)

    with sphere_node.MechanicalObject.position.writeable() as sphereArray:
        sphereArray *= [-1,-1,1]

############################################
###### Update Simulation
############################################
def updateSimulation():
    global iteration, iterations, simulating, root, originalMeshNode

    for step in range(10):
        Sofa.Simulation.animate(root, root.dt.value)

    # update model from mechanical state
    meshPointsArray = root['scene.liver'].getMechanicalState().position.array()
    modelPointsArray = slicer.util.arrayFromModelPoints(originalMeshNode)
    modelPointsArray[:] = meshPointsArray #Note the slice operator (copy!)
    slicer.util.arrayFromModelPointsModified(originalMeshNode)

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
loadSimulationData()
createSofaScene()
updateSimulation()
