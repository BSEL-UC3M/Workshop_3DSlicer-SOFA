import logging
import os

import vtk

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

#
# MyModule
#
class MyModule(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "MyModule"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["SurgicalNavigation-MIHE"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["Your Name (Institution)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#MyModule">module documentation</a>."""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """Departamento de Bioingenieria, Universidad Carlos III de Madrid"""

#
# MyModuleWidget
#
class MyModuleWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/MyModule.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = MyModuleLogic()

        # Connections

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
        # (in the selected parameter node).
         # ------ 2. CONNECT BUTTONS WITH FUNCTIONS ------
        self.ui.loadModel1Button.connect('clicked(bool)', self.onLoadModel1Button) # when the button is pressed we call the function onLoadModel1Button
        # ---- FILL ----
        # self.loadModel1Button...
        # ----

        self.ui.model1_checkBox.connect('stateChanged(int)', self.onModel1VisibilityChecked)
        # ---- FILL ----
        # self.model2_checkBox...
        # ----

        self.ui.opacityValueSliderWidget_1.connect("valueChanged(double)", self.onOpacityValueSliderWidget1Changed)
        # ---- FILL ----
        # self.opacityValueSliderWidget_2...
        # ----
        # ---- FILL ----
        # self.applyTransformButton...
        # self.undoTransformButton...
        # ----

    # ------ 3. DEFINITION OF FUNTIONS CALLED WHEN PRESSING THE BUTTONS ------

    def onLoadModel1Button(self):
        model_name = 'Model1.stl' # indicate name of model to be loaded
        data_path = slicer.modules.mymodule.path.replace("MyModule.py","") + 'Resources/Data' # indicate the path from which we want to load the model
        self.logic.loadModelFromFile(data_path, model_name, [1,0,0], True) # call function from logic
        self.ui.model1_checkBox.checked = True
        self.ui.opacityValueSliderWidget_1.value = 100
        
    # ---- FILL ----
    # def onLoadModel2Button(self): ...
    # ----

    def onModel1VisibilityChecked(self, checked):  
        model1 = slicer.util.getNode('Model1') # retrieve Model1
        self.logic.updateVisibility(model1, checked)

    # ---- FILL ----
    # def onModel2VisibilityChecked(self, checked): ...
    # ----
    
    def onOpacityValueSliderWidget1Changed(self, opacityValue):
        model1 = slicer.util.getNode('Model1') # retrieve Model1

        # Get opacity value and normalize it to get values in [0,100]
        opacityValue_norm = opacityValue/100.0

        self.logic.updateModelOpacity(model1, opacityValue_norm) # Update model opacity


    # ---- FILL ----
    #def onOpacityValueSliderWidget2Changed(self, opacityValue):
    # ----


    def onApplyTransformButton(self):
        # Load the model to which we want to apply the transform
        # ---- FILL ----
        model2 = None # retrieve Model2
        # ----
        transform_name = 'transform.h5'
        # ---- FILL ----
        data_path = '' # indicate the path from which we want to load the transform
        # ----
        transform_node = self.logic.loadTransformFromFile(data_path, transform_name)
        model2.SetAndObserveTransformNodeID(transform_node.GetID())
        self.ui.undoTransformButton.enabled = True
        self.ui.applyTransformButton.enabled = False
    # ----    

    # ---- FILL ----
    def onUndoTransformButton(self):
        # Load the model to which we want to apply the transform
        # ---- FILL ----
        # ...
        # ----
        model2.SetAndObserveTransformNodeID(None)
        #self.ui.undoTransformButton.enabled = ...
        #self.ui.applyTransformButton.enabled = ...

#
# MyModuleLogic
#
class MyModuleLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual computation done by your module.  The interface
    should be such that other python code can import this class and make use of the functionality without
    requiring an instance of the Widget. Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py    """

    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)

    def setDefaultParameters(self, parameterNode):
        """
        Initialize parameter node with default settings.
        """
        if not parameterNode.GetParameter("Threshold"):
            parameterNode.SetParameter("Threshold", "100.0")
        if not parameterNode.GetParameter("Invert"):
            parameterNode.SetParameter("Invert", "false")

    def process(self, inputVolume, outputVolume, imageThreshold, invert=False, showResult=True):

        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param inputVolume: volume to be thresholded
        :param outputVolume: thresholding result
        :param imageThreshold: values above/below this threshold will be set to 0
        :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
        :param showResult: show output volume in slice viewers
        """

        if not inputVolume or not outputVolume:
            raise ValueError("Input or output volume is invalid")

        import time
        startTime = time.time()
        logging.info('Processing started')

        # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
        cliParams = {
            'InputVolume': inputVolume.GetID(),
            'OutputVolume': outputVolume.GetID(),
            'ThresholdValue': imageThreshold,
            'ThresholdType': 'Above' if invert else 'Below'
        }
        cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
        # We don't need the CLI module node anymore, remove it to not clutter the scene with it
        slicer.mrmlScene.RemoveNode(cliNode)

        stopTime = time.time()
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')

    def loadModelFromFile(self, modelFilePath, modelFileName, colorRGB_array, visibility_bool):
        try:
            node = slicer.util.getNode(modelFileName)
        except:
            node = slicer.util.loadModel(modelFilePath + '/' + modelFileName)
            node.GetModelDisplayNode().SetColor(colorRGB_array)
            node.GetModelDisplayNode().SetVisibility(visibility_bool)
            print (modelFileName + ' model loaded')

        return node


    def loadTransformFromFile(self, transformFilePath, transformFileName):
        try:
            node = slicer.util.getNode(transformFileName)
        except:
            node = slicer.util.loadTransform(transformFilePath +  '/' + transformFileName)
            if node == None:
                node=slicer.vtkMRMLLinearTransformNode()
                node.SetName(transformFileName)
                slicer.mrmlScene.AddNode(node)
                print ('ERROR: ' + transformFileName + ' transform not found in path. Creating node as identity...')
            
        return node


    def updateVisibility(self, modelNode, show):
        if show:
            modelNode.GetDisplayNode().SetVisibility(1) # show
        else:
            modelNode.GetDisplayNode().SetVisibility(0) # hide


    def updateModelOpacity(self, inputModel, opacityValue_norm):
        inputModel.GetDisplayNode().SetOpacity(opacityValue_norm)

    def changeColor(self, inputModel, color):
        pass    