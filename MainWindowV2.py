#----------------------------------------------------------------------------------#
# A debug application for nodes attached to a CAN bus using the CANopen protocol   #
#----------------------------------------------------------------------------------#
# Authors: Ramon Breden - Willem van Rossum                                        #
# Date: 14 January 2023                                                            #
# Version: 0.1 (IN DEVELOPMENT)                                                    #
#----------------------------------------------------------------------------------#
# Language: Python                                                                 #
# Required libraries: canopen, time, sys, qdarktheme, numpy, pyqtgraph, pyqt6      #
#----------------------------------------------------------------------------------#

# IMPORTS
from CAN_COM import *
from time import perf_counter
import sys
import qdarktheme
import numpy as np
import pyqtgraph as pg
from pyqtgraph.console import ConsoleWidget
from pyqtgraph.dockarea.Dock import Dock
from pyqtgraph.dockarea.DockArea import DockArea
from pyqtgraph.Qt import QtWidgets
from PyQt6.QtGui import *
from PyQt6.QtWidgets import (
    QLineEdit,
    QComboBox,
    QMenuBar,
    QApplication)

# Initialize application
app = QApplication(sys.argv)
qdarktheme.setup_theme() # Dark mode
win = QtWidgets.QMainWindow()
area = DockArea()
win.setCentralWidget(area)
win.resize(1200,750)
win.setWindowTitle('NeNa CANopen debugger')
menu= QMenuBar()
errordialog = QtWidgets.QErrorMessage()

# Create docks and define their pixel sizes
d1 = Dock("Plot parameters", size=(250, ), hideTitle=True)    
d2 = Dock("Console", size=(250,300), closable=True, hideTitle=True)
d3 = Dock("CAN BUS Connection", size=(1,200), hideTitle=True)
d4 = Dock("Graph", size=(700,200), hideTitle=True)
d5 = Dock("Write to Objects", size=(1,200), hideTitle=True)
d6 = Dock("Object List", size=(1,200), hideTitle=True)

# Assign each dock to a spot within the application window
area.addDock(d1, 'right')     
area.addDock(d2, 'left')     
area.addDock(d3, 'bottom', d2)
area.addDock(d4, 'right', d1)     
area.addDock(d5, 'bottom', d3)  
area.addDock(d6, 'bottom', d5)  

# Define the console widget and add it to dock 2
w2 = ConsoleWidget()
d2.addWidget(w2)

# Define the connect widget
w3 = pg.LayoutWidget()

# Buttons and input fields for connect widget
bustype=QComboBox()
bustype_list = ['pcan', 'none'] # List of possible bus types
bustype.addItems(bustype_list)
channel=QComboBox()
channel_list = ['PCAN_USBBUS1','none'] # List of possible channels
channel.addItems(channel_list)
bitrate=QComboBox() # Combobox with possible bitrates
bitrate_list = [1000000, 800000, 500000, 250000, 125000, 50000, 20000, 10000]
bitrate.addItems(map(str, bitrate_list))

# Make connect button
Connect_button=QtWidgets.QPushButton("Connect")
# Make the light to communicate connect status
Light=QtWidgets.QPushButton("")
Light.setStyleSheet("background-color : red")

# Add the widgets to the w3 window
w3.addWidget(QtWidgets.QLabel("""Bustype:"""), row = 0, col= 0)
w3.addWidget(bustype, row=0, col=1)
w3.addWidget(QtWidgets.QLabel("""Channel:"""), row = 1, col= 0)
w3.addWidget(channel, row=1, col=1)
w3.addWidget(QtWidgets.QLabel("""Bitrate:"""), row = 2, col= 0)
w3.addWidget(bitrate, row=2, col=1)
w3.addWidget(Connect_button, row=3, col=1) 
w3.addWidget(Light, row= 3, col=0)

# Define the action of the connect button
node_list = ['Not connected']
CAN_ID= ['not connected',0,0]

def connect():
    
    global connectpcan, node_list, CAN_ID, node_added_list

    # Set light and write status to console
    CAN_ID= ['not connected']
    Light.setStyleSheet("background-color : red")
    w2.write("connecting....\n", scrollToBottom='auto')

    # Pull entered data from input fields
    bus=                bustype.currentText()
    channelname =       channel.currentText()
    bit =               int(bitrate.currentText())

    # Run the __init__ of the CAN_COM class
    connectpcan = CAN_COM(bus, channelname, bit)
    
    # Get all nodes connected to the CAN bus
    node_list, node_added_list = connectpcan.scan_bus()

    # Write connected nodes to the console
    string_of_nums = ','.join(str(num) for num in node_list)
    w2.write("Connected \n Found nodes: " + string_of_nums + "\n")   

    # Set light to green
    Light.setStyleSheet("background-color : green")

    CAN_ID = [bus, channelname, bit]
    print(CAN_ID) # debugging

    return node_list, CAN_ID, connectpcan, node_added_list

Connect_button.clicked.connect(connect)
d3.addWidget(w3)

# Define write widget
w5 = pg.LayoutWidget()

# Make a dropdown menu with combobox and convert all the node_list integers
# to strings with the map() function
Node=QComboBox()
Node.addItems(map(str, node_list))

# Make the rest of the inputfields
Object=QLineEdit()
variable=QLineEdit()
Sub_index= QLineEdit()

# Add upload and update buttons
UploadButton=QtWidgets.QPushButton("Upload")
UploadButton.resize(20, 10)
UpdateButton=QtWidgets.QPushButton("Update")
UpdateButton.resize(10, 10)

# Make labels and add them to the input fields and buttons
w5.addWidget(QtWidgets.QLabel("Node:"), row = 0, col= 0)
w5.addWidget(Node, row=0, col=1)
w5.addWidget(QtWidgets.QLabel("Object:"), row = 1, col= 0)
w5.addWidget(Object, row=1, col=1)
w5.addWidget(QtWidgets.QLabel("Sub index:"), row = 2, col= 0)
w5.addWidget(Sub_index, row=2, col=1)
w5.addWidget(QtWidgets.QLabel("Variable:"), row = 3, col= 0)
w5.addWidget(variable, row=3, col=1)
w5.addWidget(UploadButton, row=4, col=1)
w5.addWidget(UpdateButton, row=4, col=0)

# Function to update the list inside the dropdown list
def UpdateLists():
    QComboBox.clear(Node)
    Node.addItems(map(str, node_list))
    pg.TreeWidget.clear(w6)
    populatelist()

UpdateButton.clicked.connect(UpdateLists)

# Function to write a variable to a selected node, object and subindex
def upload():
    connectpcan.upload(int(Node.currentText()), int(Object.text(), 16), int(Sub_index.text()), int(variable.text()), node_added_list)
    w2.write('Uploading...\n' , scrollToBottom='auto')
    receive = connectpcan.download(int(Node.currentText()), int(Object.text(), 16), int(Sub_index.text()), node_added_list)
    w2.write('Succesfully uploaded ' + str(receive) + ' to node ' + Node.currentText() + ' to object ' + Object.text() + ' at sub index ' + Sub_index.text() + '\n' , scrollToBottom='auto')

# Run the upload function when the button is pressed
UploadButton.clicked.connect(upload)
d5.addWidget(w5)

# Define node tree widget
w6 = pg.TreeWidget()
w6.setHeaderHidden(True)

# Placeholder list
ObjectlistNode1= ['Example object list!',6060, 6061, 6062]

# This function populates the tree based on the connected nodes
def populatelist():
    
    for i in range(len(node_list)):
        
        Name = "Node " + str(node_list[i])
        item  = QtWidgets.QTreeWidgetItem([Name]) # Make toplevel item
        w6.addTopLevelItem(item)

        for j in range(len(ObjectlistNode1)): # For every object in the list
            object= QtWidgets.QTreeWidgetItem([str(ObjectlistNode1[j])]) # Add a child to the node with the name of the node
            item.addChild(object)

populatelist()
d6.addWidget(w6)

# Define contents of the parameter tree
children = [
    # Basic plot parameters
    dict(name='Plot speed', type='int', limits= [1, 500], value= 15 ),
    dict(name='Plot width', type='int', limits= [1, 500], value= 100 ),
    dict(name='Plot objects', type='bool', value= False ),
    # Parameters line 1
    dict(name='Line 1', type='bool', value= False ),
    dict(name='Line name', type='str'),
    dict(name='Width line 1', type='float', limits=[0.1, 50], value=1, step=0.1),
    dict(name='Color line 1', type='list', limits= ['white', 'red', 'green', 'magenta', 'blue' ],value='white' ),
    dict(name='Node ID line 1', type='int', limits= [0, 100000]),
    dict(name='Object ID line 1', type='str', limits= [1, 100000]),
    dict(name='Sub index line 1', type='int', limits= [0, 20]), 
    # Parameters line 2
    dict(name='Line 2', type='bool', value= False ),
    dict(name='Width line 2', type='float', limits=[0.1, 50], value=1, step=0.1),
    dict(name='Color line 2', type='list', limits= ['white', 'red', 'green', 'magenta', 'blue' ],value='white' ),
    dict(name='Node ID line 2', type='int', limits= [0, 100000] ),
    dict(name='Object ID line 2', type='str', limits= [1, 100000] ),
    dict(name='Sub index line 2', type='int', limits= [0, 20] ),
    # Parameters line 3
    dict(name='Line 3', type='bool', value= False ),
    dict(name='Width line 3', type='float', limits=[0.1, 50], value=1, step=0.1),
    dict(name='Color line 3', type='list', limits= ['white', 'red', 'green', 'magenta', 'blue' ],value='white' ),
    dict(name='Node ID line 3', type='int', limits= [0, 100000] ),
    dict(name='Object ID line 3', type='str', limits= [1, 100000] ),
    dict(name='Sub index line 3', type='int', limits= [0, 20] ), 
]

# Create the parameter tree
params = pg.parametertree.Parameter.create(name='Parameters', type='group', children=children)
pt = pg.parametertree.ParameterTree(showHeader=False)
pt.setParameters(params)
d1.addWidget(pt)

# This function updates the parameter tree
def updateparametertree():
    w2.write("Parameter tree changing\n", scrollToBottom='auto')

    # Start plotting the graph when the tickbox is ticked
    plot_object = params.child('Plot objects').value()
    plot_length= params.child('Plot speed').value()
    try:
        if plot_object == True:
            timer.start(plot_length)  
        else:
            timer.stop()
    except:
        w2.write("NOT CONNECTED \n")

# Looks at the parameter tree and when it changes it will run the update function
params.sigTreeStateChanged.connect(updateparametertree)

# Define the scrolling plot
w4 = pg.GraphicsLayoutWidget(show=True)
w4.setWindowTitle('Scrolling Plot')
p2 = w4.addPlot()

pg.setConfigOptions(antialias=False) # Set to true for improved curve rendering at the cost of performance
windowWidth = 500
ptr1 = -windowWidth

# Initialize the fps counter
lastTime = perf_counter()
fps = None

# Define the curves
curve1 = p2.plot()
curve2 = p2.plot()
curve3 = p2.plot()

# Axis spacing
Xm1 = np.linspace(0,0,windowWidth)
Xm2 = np.linspace(0,0,windowWidth)            
Xm3 = np.linspace(0,0,windowWidth)            
Xm4 = np.linspace(0,0,windowWidth)

# This function updates the fps counter and the scrolling plot
def update_plot():
    global Xm2, ptr1, fps, lastTime

    # Check if the line is ready to be displayed
    line1ON = params.child('Line 1').value()
    line2ON = params.child('Line 2').value()
    line3ON = params.child('Line 3').value()

    # Plot line 1
    if line1ON == True:
        line_color1       = params.child('Color line 1').value()
        line_width1      = params.child('Width line 1').value()
        node_id1= params.child('Node ID line 1').value()
        ob_id1=int( params.child('Object ID line 1').value(), 16)
        sub_idx1=int(params.child('Sub index line 1').value())

        Xm1[:-1] = Xm1[1:]
        read_int_1 = connectpcan.download(node_id1, ob_id1, sub_idx1, node_added_list)
        Xm1[-1] = float(read_int_1)

        curve1.setData(Xm1)
        curve1.setPos(ptr1, 0)
        curve1.setPen(color=line_color1, width=line_width1)
    else: 
            curve1.clear() #reset graph

    # Plot line 2
    if line2ON == True:
        line_color2       = params.child('Color line 2').value()
        line_width2      = params.child('Width line 2').value()
        node_id2= params.child('Node ID line 2').value()
        ob_id2=int( params.child('Object ID line 2').value(), 16)
        sub_idx2=int(params.child('Sub index line 2').value())

        Xm2[:-1] = Xm2[1:]
        read_int_2 = connectpcan.download(node_id2, ob_id2, sub_idx2, node_added_list)
        Xm2[-1] = float(read_int_2)

        curve2.setData(Xm2)
        curve2.setPos(ptr1, 0)
        curve2.setPen(color=line_color2, width=line_width2)
    else: 
        curve2.clear() #reset graph

    # Plot line 3
    if line3ON == True:
        line_color3       = params.child('Color line 3').value()
        line_width3      = params.child('Width line 3').value()
        node_id3= params.child('Node ID line 3').value()
        ob_id3=int( params.child('Object ID line 3').value(), 16)
        sub_idx3=int(params.child('Sub index line 3').value())

        Xm3[:-1] = Xm3[1:]
        read_int_3 = connectpcan.download(node_id3, ob_id3, sub_idx3, node_added_list)
        Xm3[-1] = float(read_int_3)

        curve3.setData(Xm3)
        curve3.setPos(ptr1, 0)
        curve3.setPen(color=line_color3, width=line_width3)
    else: 
        curve3.clear() #reset graph

    ptr1 += 1 
    
    # Calculations for the fps counter
    now = perf_counter()
    dt = now - lastTime
    lastTime = now
    
    if fps is None:
        fps = 1.0 / dt
    else:
        s = np.clip(dt * 3.0, 0, 1)
        fps = fps * (1 - s) + (1.0 / dt) * s
    p2.setTitle("%0.2f fps" % fps)

timer = pg.QtCore.QTimer()
timer.timeout.connect(update_plot)  
d4.addWidget(w4)

# Display the application window
win.show()
# This function keeps the GUI running 
if __name__ == '__main__':
    pg.exec()