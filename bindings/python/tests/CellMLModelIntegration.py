#!/usr/bin/env python

#DOC-START imports
import sys, os, math
#from scipy.special.basic import euler


# Intialise OpenCMISS
from opencmiss.opencmiss import opencmiss
#DOC-END imports

usageString = "Usage: " + sys.argv[0] + " <Noble 98 model file> [euler | bdf] [ode time step]"

# Set problem parameters
#DOC-START parameters

# get the model file
if len(sys.argv) > 1:
    modelFile = sys.argv[1]
else:
    print "You need to provide the location of the Noble 98 CellML model file"
    print usageString
    sys.exit(-2)
    
# check if we have an integrator specified
integrationMethodName = "euler"
if len(sys.argv) > 2:
    integrationMethodName = sys.argv[2]

# and setup the actual integrator type
integrationMethod = opencmiss.DAESolverTypes.EULER # no NONE type to default to?
if integrationMethodName == "euler":
    print "Using EULER integrator"
    integrationMethod = opencmiss.DAESolverTypes.EULER
elif integrationMethodName == "bdf":
    print "Using BDF (CVODE) integrator"
    integrationMethod = opencmiss.DAESolverTypes.BDF
else:
    print "Invalid integrator specified"
    print usageString
    sys.exit(-1)

# and setup the (maximal) time step for the ODE integrator
# this is used in the integration of the CellML model
odeTimeStep = 0.01
if len(sys.argv) > 3:
    odeTimeStep = float(sys.argv[3])
    
# 1D domain size
width = 1.0
numberOfXElements = 2

# Materials parameters
Am = 193.6
Cm = 0.014651
conductivity = 0.0

# Simulation parameters
stimValue = 2.5
stimStop = 1.5
timeStop = 500 # [ms?]
# this is used in the dummy monodomain problem/solver
pdeTimeStep = 0.01 # [ms]
# this is the step at which we grab output from the solver
outputTimeStep = 1.0
# set this to 1 to get exfiles written out during solve
outputFrequency = 0
#DOC-END parameters

#Setup field number handles
coordinateSystemUserNumber = 1
regionUserNumber = 1
basisUserNumber = 1
pressureBasisUserNumber = 2
generatedMeshUserNumber = 1
meshUserNumber = 1
cellMLUserNumber = 1
decompositionUserNumber = 1
equationsSetUserNumber = 1
problemUserNumber = 1
#Mesh component numbers
linearMeshComponentNumber = 1
#Fields
geometricFieldUserNumber = 1
fibreFieldUserNumber = 2
dependentFieldUserNumber = 3
materialsFieldUserNumber = 4
equationsSetFieldUserNumber = 5
cellMLModelsFieldUserNumber = 6
cellMLStateFieldUserNumber = 7
cellMLParametersFieldUserNumber = 8
cellMLIntermediateFieldUserNumber = 9

#DOC-START parallel information
# Get the number of computational nodes and this computational node number
numberOfComputationalNodes = opencmiss.ComputationalNumberOfNodesGet()
computationalNodeNumber = opencmiss.ComputationalNodeNumberGet()
#DOC-END parallel information

#DOC-START initialisation
# Create a 2D rectangular cartesian coordinate system
coordinateSystem = opencmiss.CoordinateSystem()
coordinateSystem.CreateStart(coordinateSystemUserNumber)
coordinateSystem.DimensionSet(1)
coordinateSystem.CreateFinish()

# Create a region and assign the coordinate system to the region
region = opencmiss.Region()
region.CreateStart(regionUserNumber,opencmiss.WorldRegion)
region.LabelSet("Region")
region.coordinateSystem = coordinateSystem
region.CreateFinish()
#DOC-END initialisation

#DOC-START basis
# Define a bilinear Lagrange basis
basis = opencmiss.Basis()
basis.CreateStart(basisUserNumber)
basis.type = opencmiss.BasisTypes.LAGRANGE_HERMITE_TP
basis.numberOfXi = 1
basis.interpolationXi = [opencmiss.BasisInterpolationSpecifications.LINEAR_LAGRANGE]
basis.CreateFinish()
#DOC-END basis

#DOC-START generated mesh
# Create a generated mesh
generatedMesh = opencmiss.GeneratedMesh()
generatedMesh.CreateStart(generatedMeshUserNumber,region)
generatedMesh.type = opencmiss.GeneratedMeshTypes.REGULAR
generatedMesh.basis = [basis]
generatedMesh.extent = [width]
generatedMesh.numberOfElements = [numberOfXElements]

mesh = opencmiss.Mesh()
generatedMesh.CreateFinish(meshUserNumber,mesh)
#DOC-END generated mesh

#DOC-START decomposition
# Create a decomposition for the mesh
decomposition = opencmiss.Decomposition()
decomposition.CreateStart(decompositionUserNumber,mesh)
decomposition.type = opencmiss.DecompositionTypes.CALCULATED
decomposition.numberOfDomains = numberOfComputationalNodes
decomposition.CreateFinish()
#DOC-END decomposition

#DOC-START geometry
# Create a field for the geometry
geometricField = opencmiss.Field()
geometricField.CreateStart(geometricFieldUserNumber, region)
geometricField.decomposition = decomposition
geometricField.TypeSet(opencmiss.FieldTypes.GEOMETRIC)
geometricField.VariableLabelSet(opencmiss.FieldVariableTypes.U, "coordinates")
geometricField.ComponentMeshComponentSet(opencmiss.FieldVariableTypes.U, 1, linearMeshComponentNumber)
geometricField.CreateFinish()

# Set geometry from the generated mesh
generatedMesh.GeometricParametersCalculate(geometricField)
#DOC-END geometry

#DOC-START equations set
# Create the equations_set
equationsSetField = opencmiss.Field()
equationsSet = opencmiss.EquationsSet()
equationsSetSpecification = [opencmiss.EquationsSetClasses.BIOELECTRICS,
        opencmiss.EquationsSetTypes.MONODOMAIN_EQUATION,
        opencmiss.EquationsSetSubtypes.NONE]
equationsSet.CreateStart(equationsSetUserNumber, region, geometricField,
        equationsSetSpecification, equationsSetFieldUserNumber, equationsSetField)
equationsSet.CreateFinish()
#DOC-END equations set

#DOC-START equations set fields
# Create the dependent Field
dependentField = opencmiss.Field()
equationsSet.DependentCreateStart(dependentFieldUserNumber, dependentField)
equationsSet.DependentCreateFinish()

# Create the materials Field
materialsField = opencmiss.Field()
equationsSet.MaterialsCreateStart(materialsFieldUserNumber, materialsField)
equationsSet.MaterialsCreateFinish()

# Set the materials values
# Set Am
materialsField.ComponentValuesInitialise(opencmiss.FieldVariableTypes.U,opencmiss.FieldParameterSetTypes.VALUES,1,Am)
# Set Cm
materialsField.ComponentValuesInitialise(opencmiss.FieldVariableTypes.U,opencmiss.FieldParameterSetTypes.VALUES,2,Cm)
# Set conductivity
materialsField.ComponentValuesInitialise(opencmiss.FieldVariableTypes.U,opencmiss.FieldParameterSetTypes.VALUES,3,conductivity)
#DOC-END equations set fields

#DOC-START create cellml envopencmissment
# Create the CellML envopencmissment
cellML = opencmiss.CellML()
cellML.CreateStart(cellMLUserNumber, region)
# Import a Nobel 98 cell model from a file
noble98Model = cellML.ModelImport(modelFile)
#DOC-END create cellml envopencmissment

#DOC-START flag variables
# Now we have imported the model we are able to specify which variables from the model we want to set from openCMISS
cellML.VariableSetAsKnown(noble98Model, "fast_sodium_current/g_Na")
cellML.VariableSetAsKnown(noble98Model, "membrane/IStim")
# and variables to get from the CellML 
cellML.VariableSetAsWanted(noble98Model, "membrane/i_K1")
cellML.VariableSetAsWanted(noble98Model, "membrane/i_to")
cellML.VariableSetAsWanted(noble98Model, "membrane/i_K")
cellML.VariableSetAsWanted(noble98Model, "membrane/i_K_ATP")
cellML.VariableSetAsWanted(noble98Model, "membrane/i_Ca_L_K")
cellML.VariableSetAsWanted(noble98Model, "membrane/i_b_K")
cellML.VariableSetAsWanted(noble98Model, "membrane/i_NaK")
cellML.VariableSetAsWanted(noble98Model, "membrane/i_Na")
cellML.VariableSetAsWanted(noble98Model, "membrane/i_b_Na")
cellML.VariableSetAsWanted(noble98Model, "membrane/i_Ca_L_Na")
cellML.VariableSetAsWanted(noble98Model, "membrane/i_NaCa")
#DOC-END flag variables

#DOC-START create cellml finish
cellML.CreateFinish()
#DOC-END create cellml finish

#DOC-START map Vm components
# Start the creation of CellML <--> OpenCMISS field maps
cellML.FieldMapsCreateStart()
#Now we can set up the field variable component <--> CellML model variable mappings.
#Map Vm
cellML.CreateFieldToCellMLMap(dependentField,opencmiss.FieldVariableTypes.U,1, opencmiss.FieldParameterSetTypes.VALUES,noble98Model,"membrane/V", opencmiss.FieldParameterSetTypes.VALUES)
cellML.CreateCellMLToFieldMap(noble98Model,"membrane/V", opencmiss.FieldParameterSetTypes.VALUES,dependentField,opencmiss.FieldVariableTypes.U,1,opencmiss.FieldParameterSetTypes.VALUES)

#Finish the creation of CellML <--> OpenCMISS field maps
cellML.FieldMapsCreateFinish()

# Set the initial Vm values
dependentField.ComponentValuesInitialise(opencmiss.FieldVariableTypes.U, opencmiss.FieldParameterSetTypes.VALUES, 1,-92.5)
#DOC-END map Vm components

#DOC-START define CellML models field
#Create the CellML models field
cellMLModelsField = opencmiss.Field()
cellML.ModelsFieldCreateStart(cellMLModelsFieldUserNumber, cellMLModelsField)
cellML.ModelsFieldCreateFinish()
#DOC-END define CellML models field

#DOC-START define CellML state field
#Create the CellML state field 
cellMLStateField = opencmiss.Field()
cellML.StateFieldCreateStart(cellMLStateFieldUserNumber, cellMLStateField)
cellML.StateFieldCreateFinish()
#DOC-END define CellML state field

#DOC-START define CellML parameters and intermediate fields
#Create the CellML parameters field 
cellMLParametersField = opencmiss.Field()
cellML.ParametersFieldCreateStart(cellMLParametersFieldUserNumber, cellMLParametersField)
cellML.ParametersFieldCreateFinish()

#  Create the CellML intermediate field 
cellMLIntermediateField = opencmiss.Field()
cellML.IntermediateFieldCreateStart(cellMLIntermediateFieldUserNumber, cellMLIntermediateField)
cellML.IntermediateFieldCreateFinish()
#DOC-END define CellML parameters and intermediate fields

# Create equations
equations = opencmiss.Equations()
equationsSet.EquationsCreateStart(equations)
equations.sparsityType = opencmiss.EquationsSparsityTypes.SPARSE
equations.outputType = opencmiss.EquationsOutputTypes.NONE
equationsSet.EquationsCreateFinish()

# Find the domains of the first and last nodes
firstNodeNumber = 1
lastNodeNumber = (numberOfXElements+1)
firstNodeDomain = decomposition.NodeDomainGet(firstNodeNumber, 1)
lastNodeDomain = decomposition.NodeDomainGet(lastNodeNumber, 1)

# set up the indices of the fields we want to grab
potentialComponent = cellML.FieldComponentGet(noble98Model, opencmiss.CellMLFieldTypes.STATE, "membrane/V")
stimulusCurrentComponent = cellML.FieldComponentGet(noble98Model, opencmiss.CellMLFieldTypes.PARAMETERS, "membrane/IStim")
I_CaL_K_Component = cellML.FieldComponentGet(noble98Model, opencmiss.CellMLFieldTypes.INTERMEDIATE, "membrane/i_Ca_L_K")
I_CaL_Na_Component = cellML.FieldComponentGet(noble98Model, opencmiss.CellMLFieldTypes.INTERMEDIATE, "membrane/i_Ca_L_Na")
# and the arrays to store them in
Vm = []
IStim = []
ICaLK = []
ICaLNa = []
ICaL = []

# We are using node 1 as the point in our dummy monodomain problem to integrate the CellML model
cellmlNode = 2
cellmlNodeDomain = decomposition.NodeDomainGet(cellmlNode, 1)
cellmlNodeThisComputationalNode = False
if cellmlNodeDomain == computationalNodeNumber:
    cellmlNodeThisComputationalNode = True
    
# set the stimulus current on
stimulusIsOn = False
if cellmlNodeThisComputationalNode:
    cellMLParametersField.ParameterSetUpdateNode(opencmiss.FieldVariableTypes.U, opencmiss.FieldParameterSetTypes.VALUES, 1, 1, cellmlNode, stimulusCurrentComponent, 0.0)

# # Set up the gNa gradient
# gNaComponent = cellML.FieldComponentGet(noble98Model, opencmiss.CellMLFieldTypes.PARAMETERS, "fast_sodium_current/g_Na")
# for node in range(1,lastNodeNumber):
#     nodeDomain = decomposition.NodeDomainGet(node,1)
#     if nodeDomain == computationalNodeNumber:
#         x = geometricField.ParameterSetGetNode(opencmiss.FieldVariableTypes.U, opencmiss.FieldParameterSetTypes.VALUES, 1, 1, node, 1)
#         y = geometricField.ParameterSetGetNode(opencmiss.FieldVariableTypes.U, opencmiss.FieldParameterSetTypes.VALUES, 1, 1, node, 2)
#         distance = math.sqrt(x*x + y*y)/math.sqrt(width*width + height*height)
#         gNaValue = 2*(distance + 0.5)*0.3855
#         cellMLParametersField.ParameterSetUpdateNode(opencmiss.FieldVariableTypes.U, opencmiss.FieldParameterSetTypes.VALUES, 1, 1, node, gNaComponent, gNaValue)

#DOC-START define monodomain problem
#Define the problem
problem = opencmiss.Problem()
problemSpecification=[opencmiss.ProblemClasses.BIOELECTRICS,
    opencmiss.ProblemTypes.MONODOMAIN_EQUATION,
    opencmiss.ProblemSubtypes.MONODOMAIN_GUDUNOV_SPLIT]
problem.CreateStart(problemUserNumber,problemSpecification)
problem.CreateFinish()
#DOC-END define monodomain problem

#Create the problem control loop
problem.ControlLoopCreateStart()
controlLoop = opencmiss.ControlLoop()
problem.ControlLoopGet([opencmiss.ControlLoopIdentifiers.NODE],controlLoop)
controlLoop.TimesSet(0.0,stimStop,pdeTimeStep)

# controlLoop.OutputTypeSet(opencmiss.ControlLoopOutputTypes.TIMING)
controlLoop.OutputTypeSet(opencmiss.ControlLoopOutputTypes.NONE)

controlLoop.TimeOutputSet(outputFrequency)
problem.ControlLoopCreateFinish()

#Create the problem solvers
daeSolver = opencmiss.Solver()
dynamicSolver = opencmiss.Solver()
problem.SolversCreateStart()
# Get the first DAE solver
problem.SolverGet([opencmiss.ControlLoopIdentifiers.NODE],1,daeSolver)
daeSolver.DAESolverTypeSet(integrationMethod)
daeSolver.DAETimeStepSet(odeTimeStep)
daeSolver.OutputTypeSet(opencmiss.SolverOutputTypes.NONE)
# Get the second dynamic solver for the parabolic problem
problem.SolverGet([opencmiss.ControlLoopIdentifiers.NODE],2,dynamicSolver)
dynamicSolver.OutputTypeSet(opencmiss.SolverOutputTypes.NONE)
problem.SolversCreateFinish()

#DOC-START define CellML solver
#Create the problem solver CellML equations
cellMLEquations = opencmiss.CellMLEquations()
problem.CellMLEquationsCreateStart()
daeSolver.CellMLEquationsGet(cellMLEquations)
cellmlIndex = cellMLEquations.CellMLAdd(cellML)
problem.CellMLEquationsCreateFinish()
#DOC-END define CellML solver

#Create the problem solver PDE equations
solverEquations = opencmiss.SolverEquations()
problem.SolverEquationsCreateStart()
dynamicSolver.SolverEquationsGet(solverEquations)
solverEquations.sparsityType = opencmiss.SolverEquationsSparsityTypes.SPARSE
equationsSetIndex = solverEquations.EquationsSetAdd(equationsSet)
problem.SolverEquationsCreateFinish()

# Prescribe any boundary conditions 
boundaryConditions = opencmiss.BoundaryConditions()
solverEquations.BoundaryConditionsCreateStart(boundaryConditions)
solverEquations.BoundaryConditionsCreateFinish()

# Main time loop
# Here we are really doing something that Opencmiss is not designed to handle, so this is not optimal
# but does allow up to test model integration in Opencmiss.
currentTime = 0.0
# grab initial results
#print "Time: " + str(currentTime)
time = []
value = 0.0
if cellmlNodeThisComputationalNode:
    time.append(currentTime)
    Vm.append(cellMLStateField.ParameterSetGetNode(opencmiss.FieldVariableTypes.U, opencmiss.FieldParameterSetTypes.VALUES, 1, 1, cellmlNode, potentialComponent))
    ICaLK.append(cellMLIntermediateField.ParameterSetGetNode(opencmiss.FieldVariableTypes.U, opencmiss.FieldParameterSetTypes.VALUES, 1, 1, cellmlNode, I_CaL_K_Component))
    ICaLNa.append(cellMLIntermediateField.ParameterSetGetNode(opencmiss.FieldVariableTypes.U, opencmiss.FieldParameterSetTypes.VALUES, 1, 1, cellmlNode, I_CaL_Na_Component))
    ICaL.append(ICaLK[-1] + ICaLNa[-1])
    IStim.append(cellMLParametersField.ParameterSetGetNode(opencmiss.FieldVariableTypes.U, opencmiss.FieldParameterSetTypes.VALUES, 1, 1, cellmlNode, stimulusCurrentComponent))

while currentTime < timeStop:
    # check if we need to turn off the stimulus current
    if stimulusIsOn and (currentTime > stimStop):
        stimulusIsOn = False
        if cellmlNodeThisComputationalNode:
            cellMLParametersField.ParameterSetUpdateNode(opencmiss.FieldVariableTypes.U, opencmiss.FieldParameterSetTypes.VALUES, 1, 1, cellmlNode, stimulusCurrentComponent, 0.0)

    # set the next solution interval
    nextTime = currentTime + outputTimeStep
    controlLoop.TimesSet(currentTime, nextTime, outputTimeStep)
    
    # integrate the model
    problem.Solve()
    
    # check if we need to turn stimulus on (to match behaviour of OpenCOR (https://github.com/opencor/opencor/issues/675))
    if not stimulusIsOn and (currentTime < stimStop):
        stimulusIsOn = True
        if cellmlNodeThisComputationalNode:
            cellMLParametersField.ParameterSetUpdateNode(opencmiss.FieldVariableTypes.U, opencmiss.FieldParameterSetTypes.VALUES, 1, 1, cellmlNode, stimulusCurrentComponent, stimValue)

    currentTime = nextTime
    
    # grab results
    #print "Time: " + str(currentTime)
    if cellmlNodeThisComputationalNode:
        time.append(currentTime)
        Vm.append(cellMLStateField.ParameterSetGetNode(opencmiss.FieldVariableTypes.U, opencmiss.FieldParameterSetTypes.VALUES, 1, 1, cellmlNode, potentialComponent))
        ICaLK.append(cellMLIntermediateField.ParameterSetGetNode(opencmiss.FieldVariableTypes.U, opencmiss.FieldParameterSetTypes.VALUES, 1, 1, cellmlNode, I_CaL_K_Component))
        ICaLNa.append(cellMLIntermediateField.ParameterSetGetNode(opencmiss.FieldVariableTypes.U, opencmiss.FieldParameterSetTypes.VALUES, 1, 1, cellmlNode, I_CaL_Na_Component))
        ICaL.append(ICaLK[-1] + ICaLNa[-1])
        IStim.append(cellMLParametersField.ParameterSetGetNode(opencmiss.FieldVariableTypes.U, opencmiss.FieldParameterSetTypes.VALUES, 1, 1, cellmlNode, stimulusCurrentComponent))
    
# save the results
with open('results.txt', "w") as outputFile:
    print >> outputFile, "#time Vm ICaL ICaLK ICaLNa IStim"
    for i in range(0, len(time)):
        print >> outputFile, time[i], Vm[i], ICaL[i], ICaLK[i], ICaLNa[i], IStim[i]
         
# Export the results, here we export them as standard exnode, exelem files
if outputFrequency != 0:
    fields = opencmiss.Fields()
    fields.CreateRegion(region)
    fields.NodesExport("Monodomain","FORTRAN")
    fields.ElementsExport("Monodomain","FORTRAN")
    fields.Finalise()

