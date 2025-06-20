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
#liver_mesh_file = "A:/Projects/UC3M_Lectures/2025_Workshop_3DSlicer-SOFA/Day_2/Session-5_SOFA_and_3DSlicer/datasets/originalMesh.vtk"
sphere_surface_file = "A:/Projects/UC3M_Lectures/2025_Workshop_3DSlicer-SOFA/Day_2/Session-5_SOFA_and_3DSlicer/datasets/biggerCavity.obj"
originalMeshNode = None
sphereNode = None
liver_mass = 30.0
liver_youngs_modulus = 1.0 * 1000.0 * 0.001
liver_poisson_ratio = 0.45

# Simulatlon hyperparameters
rootNode = None
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
    originalMeshNode = slicer.util.getNode("Model")

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


def CreateScene() -> Sofa.Core.Node:
    """
    Creates the main SOFA scene with required components for simulation.

    Returns:
        Sofa.Core.Node: The root node of the SOFA simulation scene.
    """
    global rootNode
    from stlib3.scene import MainHeader, ContactHeader
    from stlib3.solver import DefaultSolver
    from stlib3.physics.deformable import ElasticMaterialObject
    from stlib3.physics.rigid import Floor
    from splib3.numerics import Vec3

    vonMisesMode = {
        "none": 0,
        "corotational": 1,
        "fullGreen": 2
    }

    # Initialize the root node of the SOFA scene
    rootNode = Sofa.Core.Node("Root")

    # Initialize main scene headers with necessary plugins for SOFA components
    MainHeader(rootNode, plugins=[
        "Sofa.Component.IO.Mesh",
        "Sofa.Component.LinearSolver.Direct",
        "Sofa.Component.LinearSolver.Iterative",
        "Sofa.Component.Mapping.Linear",
        "Sofa.Component.Mass",
        "Sofa.Component.ODESolver.Backward",
        "Sofa.Component.Setting",
        "Sofa.Component.SolidMechanics.FEM.Elastic",
        "Sofa.Component.StateContainer",
        "Sofa.Component.Topology.Container.Dynamic",
        "Sofa.Component.Visual",
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
        "MultiThreading",
        "Sofa.Component.SolidMechanics.Spring",
        "Sofa.Component.Constraint.Lagrangian.Model",
        "Sofa.Component.Mapping.NonLinear",
        "Sofa.Component.Topology.Container.Constant",
        "Sofa.Component.Topology.Mapping",
        "Sofa.Component.Topology.Container.Dynamic",
        "Sofa.Component.Engine.Select",
        "Sofa.Component.Constraint.Projective",
        "SofaIGTLink"
    ])

    # Set gravity vector for the simulation (no gravity in this case)
    rootNode.gravity = [0, 0, 0]

    # Add animation and constraint solver objects to the root node
    rootNode.addObject('FreeMotionAnimationLoop', parallelODESolving=True, parallelCollisionDetectionAndFreeMotion=True)
    rootNode.addObject('GenericConstraintSolver', maxIterations=10, multithreading=True, tolerance=1.0e-3)

    # Define a deformable Finite Element Method (FEM) object
    femNode = rootNode.addChild('FEM')
    femNode.addObject('EulerImplicitSolver', firstOrder=False, rayleighMass=0.1, rayleighStiffness=0.1)
    femNode.addObject('SparseLDLSolver', name="precond", template="CompressedRowSparseMatrixd", parallelInverseProduct=True)
    femNode.addObject('TetrahedronSetTopologyContainer', name="Container", position=arrayFromModelPoints(originalMeshNode),
                         tetrahedra=arrayFromModelGridCells(originalMeshNode))
    femNode.addObject('TetrahedronSetTopologyModifier', name="Modifier")
    femNode.addObject('MechanicalObject', name="mstate", template="Vec3d")
    femNode.addObject('TetrahedronFEMForceField', name="FEM", youngModulus=1.5, poissonRatio=0.45, method="large", computeVonMisesStress=vonMisesMode['fullGreen'])
    femNode.addObject('MeshMatrixMass', totalMass=1)

    # Add a region of interest (ROI) with fixed constraints in the FEM node
    fixedROI = femNode.addChild('FixedROI')
    fixedROI.addObject('BoxROI', template="Vec3", box=[0.0]*6, drawBoxes=False,
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

    # Add a node for attaching points to the mouse interactor
    attachPointNode = rootNode.addChild('AttachPoint')
    attachPointNode.addObject('PointSetTopologyContainer', name="Container")
    attachPointNode.addObject('PointSetTopologyModifier', name="Modifier")
    attachPointNode.addObject('MechanicalObject', name="mstate", template="Vec3d", drawMode=2, showObjectScale=0.01, showObject=False)
    attachPointNode.addObject('iGTLinkMouseInteractor', name="mouseInteractor", pickingType="constraint", reactionTime=20, destCollisionModel="@../FEM/Collision/collisionModel")

    return rootNode

############################################
###### Update Simulation
############################################
def updateSimulation():
    global iteration, iterations, simulating, rootNode, originalMeshNode

    for step in range(10):
        Sofa.Simulation.animate(rootNode, rootNode.dt.value)

    # update model from mechanical state
    meshPointsArray = rootNode['scene.liver'].getMechanicalState().position.array()
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
#createSofaScene()
CreateScene()
updateSimulation()
