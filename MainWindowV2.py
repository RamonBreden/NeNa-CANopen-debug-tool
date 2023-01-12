"""

"""

from GUI_BOXES import *
from CAN_COM import *

from time import perf_counter
import sys
import numpy as np
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
    QPushButton,
    QComboBox,
    QStatusBar,
    QMenuBar,
    QToolBar,
    QMessageBox,
    QApplication,
    QSpinBox,
    QErrorMessage
    
)

app = QApplication(sys.argv)
qdarktheme.setup_theme() # Dark mode
win = QtWidgets.QMainWindow()
area = DockArea()
win.setCentralWidget(area)
win.resize(1000,750)
win.setWindowTitle('NeNa CANopen debugger')

menu= QMenuBar()
errordialog = QtWidgets.QErrorMessage()
## Create docks, place them into the window one at a time.

d1 = Dock("Plot parameters", size=(700, ), hideTitle=True)    
d2 = Dock("Console", size=(300,300), closable=True, hideTitle=True)
d3 = Dock("CAN BUS Connection", size=(1,200), hideTitle=False)
d4 = Dock("Plotgenerator", size=(1,200), hideTitle=True)
d5 = Dock("Write to Objects", size=(1,200), hideTitle=True)
d6 = Dock("Object List", size=(1,200), hideTitle=True)
#d7 = Dock("plot", size=(1,1),closable=True, hideTitle=False)

area.addDock(d1, 'right')     
area.addDock(d2, 'left')     
area.addDock(d3, 'bottom', d2)
area.addDock(d4, 'bottom', d1)     
area.addDock(d5, 'bottom', d3)  
area.addDock(d6, 'bottom', d5)  
#area.addDock(d7, 'bottom', d4)


#CONSELWIDGET -------------------------------------------------------------------------------------------------------------------------
w2 = ConsoleWidget()
d2.addWidget(w2)


#CONNECT WIDGET---------------------------------------------------------------------------------------------------------------------
w3 = pg.LayoutWidget()

#Make buttons and inputsfields widgets
bustype=QComboBox()
bustype_list = ['pcan', 'none'] #list of bustypes possible
bustype.addItems(bustype_list)
channel=QComboBox()
channel_list = ['PCAN_USBBUS1','none'] #list of bustypes possible
channel.addItems(channel_list)
bitrate=QComboBox()
bitrate_list = [1000000, 800000, 500000, 250000, 125000, 50000, 20000, 10000]
bitrate.addItems(map(str, bitrate_list))

#Make button
Connect_button=QtWidgets.QPushButton("Connect")
#Make the light to communicate the state
Light=QtWidgets.QPushButton("")
Light.setStyleSheet("background-color : red")

#add the widgets to the w3 window
w3.addWidget(QtWidgets.QLabel("""Bustype:"""), row = 0, col= 0)
w3.addWidget(bustype, row=0, col=1)

w3.addWidget(QtWidgets.QLabel("""Channel:"""), row = 1, col= 0)
w3.addWidget(channel, row=1, col=1)

w3.addWidget(QtWidgets.QLabel("""Bitrate:"""), row = 2, col= 0)
w3.addWidget(bitrate, row=2, col=1)

w3.addWidget(Connect_button, row=3, col=1) 
w3.addWidget(Light, row= 3, col=0)

#define the action of the button
node_list = ['Not connected']

def connect():
    #ISSUE: THere is no way to see if the connection has failed
    global connectpcan, node_list
    CAN_ID= ['not connected']
    Light.setStyleSheet("background-color : red")
    w2.write("connecting....\n", scrollToBottom='auto')


    bus=                bustype.currentText()
    channelname =       channel.currentText()
    bit =               int(bitrate.currentText())

    connectpcan = CAN_COM(bus, channelname, bit) # Werkt wel met currentText!!     
    
    #Get all nodes connected to the canbus
    node_list = connectpcan.scan_bus()

    #write the node list to the consel
    string_of_nums = ','.join(str(num) for num in node_list)
    w2.write("Connected \n Found nodes: " + string_of_nums + "\n")   

    #When connected set light to green
    Light.setStyleSheet("background-color : green")

    CAN_ID = [bus, channelname, bit]
    print(CAN_ID)


    #Stop connection with the CANBUS 
    #this is only because we couldnot get the CAN_COM things to work
    connectpcan.disconnect()
    return node_list, CAN_ID, connectpcan
Connect_button.clicked.connect(connect)

d3.addWidget(w3)


# WRITE WIDGET---------------------------------------------------------------------------------------------------
w5 = pg.LayoutWidget()

#make a dropdown menu with combobox and convert all the node_list intergers to strings with map() function
Node=QComboBox()
Node.addItems(map(str, node_list))
#make the rest of the inputfields
Object=QLineEdit()
variable=QLineEdit()
Sub_index= QLineEdit()
UploadButton=QtWidgets.QPushButton("Upload")
UploadButton.resize(20, 10)

UpdateButton=QtWidgets.QPushButton("Update")
UpdateButton.resize(10, 10)
#Make Lables and add the labels and inputfields to the widget
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

#function to update the list in the dropdown list
def UpdateLists():
    QComboBox.clear(Node)
    Node.addItems(map(str, node_list))
    pg.TreeWidget.clear(w6)
    populatelist()
    


UpdateButton.clicked.connect(UpdateLists)

def upload():
    #send the folling things to the Connecting thing
    connectpcan.upload(int(Node.currentText()), int(Object.text(), 16), int(Sub_index.text()), int(variable.text()))
    w2.write('Uploading...\n' , scrollToBottom='auto')
    receive = connectpcan.download(int(Node.currentText()), int(Object.text(), 16), int(Sub_index.text()))
    w2.write('Succesfully uploaded ' + str(receive) + ' to node ' + Node.currentText() + ' to object ' + Object.text() + ' at sub index ' + Sub_index.text() + '\n' , scrollToBottom='auto')

UploadButton.clicked.connect(upload)


d5.addWidget(w5)
#NODE TREE WIDGET------------------------------------------------------------------------------------------------------------------------
w6 = pg.TreeWidget()
w6.setHeaderHidden(True)

ObjectlistNode1= ['Example object list!',6060, 6061, 6062]
def populatelist():
    
    for i in range(len(node_list)):
        
        Name = "Node " + str(node_list[i])
        item  = QtWidgets.QTreeWidgetItem([Name]) # make toplevel ITEM
        w6.addTopLevelItem(item)

        for j in range(len(ObjectlistNode1)):               #for every object in the list
            object= QtWidgets.QTreeWidgetItem([str(ObjectlistNode1[j])]) # add a Child to the Node with the name of the Node
            item.addChild(object)
    
populatelist()

d6.addWidget(w6)        
#PARAMETER TREE----------------------------------------------------------------------------------------------------


children = [
    #basic plot parameters
    dict(name='Lines', type='int', limits= [1, 5] ),
    dict(name='Plot length', type='int', limits= [1, 500], value= 15 ),
    dict(name='Plot objects', type='bool', value= False ),
    #Parameters per line
    dict(name='Line 1'),
    dict(name='Line name', type='str'),
    dict(name='Width line 1', type='float', limits=[0.1, 50], value=1, step=0.1),
    dict(name='Color line 1', type='list', limits= ['white', 'red', 'green', 'magenta', 'blue' ],value='white' ),
    dict(name='Node ID line 1', type='int', limits= [1, 100000] ),
    dict(name='Object ID line 1', type='str', limits= [1, 100000] ),
    dict(name='Sub index line 1', type='int', limits= [1, 20] ), 
    dict(name='Line 2'),
    dict(name='Color line 2', type='list', limits= ['white', 'red', 'green', 'magenta', 'blue' ],value='white' ),
    dict(name='Node ID line 2', type='int', limits= [1, 100000] ),
    dict(name='Object ID line 2', type='str', limits= [1, 100000] ),
    dict(name='Sub index line 2', type='int', limits= [1, 20] ), 
    dict(name='Line 3'),
    dict(name='Color line 3', type='list', limits= ['white', 'red', 'green', 'magenta', 'blue' ],value='white' ),
    dict(name='Node ID line 3', type='int', limits= [1, 100000] ),
    dict(name='Object ID line 3', type='str', limits= [1, 100000] ),
    dict(name='Sub index line 3', type='int', limits= [1, 20] ), 

]
params = pg.parametertree.Parameter.create(name='Parameters', type='group', children=children)
pt = pg.parametertree.ParameterTree(showHeader=False)
pt.setParameters(params)

d1.addWidget(pt)


#SCROLL PLOT ------------------------------------------------------------------------------------------------
w4 = pg.GraphicsLayoutWidget(show=True)
w4.setWindowTitle('pyqtgraph example: Scrolling Plots')
p2 = w4.addPlot()

pg.setConfigOptions(antialias=True)
windowWidth = 500
ptr1 = -windowWidth
lastTime = perf_counter()
fps = None


#curve1 = p2.plot(pen={'color':(0, 156, 129), 'width':3})
curve2 = p2.plot()

#Xm1 = np.linspace(0,0,windowWidth)
Xm2 = np.linspace(0,0,windowWidth)            



#lines   = params.child('nb_lines').value()


def update_plot():
    global Xm2, node, ptr1, fps, lastTime

    
    line_color1       = params.child('Color line 1').value()
    line_width1      = params.child('Width line 1').value()
    
 
    node_id1= params.child('Node ID line 1').value()
    obj_id1= params.child('Object ID line 1').value()
    subindx1= params.child('Sub index line 1').value()

    
    




    Xm2[:-1] = Xm2[1:]

    read_byte_2 =connectpcan.download(node_id1, obj_id1, subindx1)
    read_int_2 = int.from_bytes(read_byte_2, "little")

    Xm2[-1] = float(read_int_2)
    
    ptr1 += 1

    curve2.setData(Xm2)
    curve2.setPos(ptr1, 0)
    curve2.setPen(color=line_color1, width=line_width1)

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


#--------------------------------------------------------------------------------------------------------------------------------------------
# the function that updates the parameter tree when it is i called
def updateparametertree():
    w2.write("Parameter tree changing\n", scrollToBottom='auto')

    # start plotting the graph when the tickbox is ticked
    plot_object = params.child('Plot objects').value()
    plot_length= params.child('Plot length').value()
    
    if plot_object == True:
        timer.start(plot_length)
    else:
        timer.stop()
params.sigTreeStateChanged.connect(updateparametertree) # looks at the parameter tree and when it changes it will run the update function.





#--------------------------------------------------------------------------------------------------------------------------------------------
#shows the window that is made 
win.show()
#This function keeps the GUI running 
if __name__ == '__main__':
    pg.exec()