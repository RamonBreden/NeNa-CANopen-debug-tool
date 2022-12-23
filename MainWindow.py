"""
This example demonstrates the use of pyqtgraph's dock widget system.

The dockarea system allows the design of user interfaces which can be rearranged by
the user at runtime. Docks can be moved, resized, stacked, and torn out of the main
window. This is similar in principle to the docking system built into Qt, but 
offers a more deterministic dock placement API (in Qt it is very difficult to 
programatically generate complex dock arrangements). Additionally, Qt's docks are 
designed to be used as small panels around the outer edge of a window. Pyqtgraph's 
docks were created with the notion that the entire window (or any portion of it) 
would consist of dockable components.
"""

import sys
import CAN_COM
import numpy as np
import qdarktheme
import numpy as np
import pyqtgraph as pg

from time import perf_counter
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
    QSpinBox
)

app = QApplication(sys.argv)
qdarktheme.setup_theme() # Dark mode
win = QtWidgets.QMainWindow()
area = DockArea()
win.setCentralWidget(area)
win.resize(1000,750)
win.setWindowTitle('NeNa CANopen debugger')

menu= QMenuBar()

## Create docks, place them into the window one at a time.
## Note that size arguments are only a suggestion; docks will still have to
## fill the entire dock area and obey the limits of their internal widgets.
d1 = Dock("Menu", size=(1, 1), hideTitle=False)     ## give this dock the minimum possible size
d2 = Dock("Console", size=(500,300), closable=True, hideTitle=False)
d3 = Dock("Connection window", size=(500,400), hideTitle=False)
d4 = Dock("Plotgenerator", size=(500,200), hideTitle=False)
d5 = Dock("Write to Objects", size=(500,200), hideTitle=False)
d6 = Dock("Object List", size=(500,200), hideTitle=False)
#d7 = Dock("plot", size=(500,200), hideTitle=False)

area.addDock(d1, 'left')      ## place d1 at left edge of dock area (it will fill the whole space since there are no other docks yet)
area.addDock(d2, 'bottom', d1)     
area.addDock(d3, 'right')## place d3 at bottom edge of d1
area.addDock(d4, 'bottom', d3)     ## place d4 at right edge of dock area
area.addDock(d5, 'bottom', d4)  ## place d5 at left edge of d1
area.addDock(d6, 'right', d3)   ## place d5 at top edge of d4
#area.addDock(d7, 'right')

## Test ability to move docks programatically after they have been placed
#area.moveDock(d4, 'top', d2)     ## move d4 to top edge of d2  ## move d6 to stack on top of d4
#area.moveDock(d5, 'top', d2)     ## move d5 to top edge of d2

## Add widgets into each dock
w2 = ConsoleWidget()
d2.addWidget(w2)

#Make the Connection manager window/box
def ConnectWidget(): 
    #call layoutmanager and make the window w3
    w3 = pg.LayoutWidget()
    #Make buttons and inputsfields widgets
    bustype=QLineEdit()
    channel=QLineEdit()
    bitrate=QComboBox()
    bitrate_list = [1000, 800, 500, 250, 125, 50, 20, 10]
    bitrate.addItems(map(str, bitrate_list))
    
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
    def connect(bitrate_list):
        
        w2.write("connecting....\n", scrollToBottom='auto')
        #run the Connect script
        #CAN_COM.__init__(bustype.text(), channel.text(), bitrate_list(bitrate.currentIndex()))
        
        #When connected set light to green
        Light.setStyleSheet("background-color : green")
    Connect_button.clicked.connect(lambda: connect(bitrate_list))
    #send the finised window widget outside the function
    return w3
#generate the w3 widget and put it into the d3 box
d3.addWidget(ConnectWidget())

#dezed moet nog geimporteerd worden van de CAN_COM class
node_list= [40, 41, 10]

#make the window to write date to the NeNa
def WriteWidget(node_list):
    w5 = pg.LayoutWidget()

    #make a dropdown menu with combobox and convert all the node_list intergers to strings with map() function
    Node=QComboBox()
    Node.addItems(map(str, node_list))

    Object=QLineEdit()
    variable=QLineEdit()
    Sub_index= QLineEdit()
    UploadButton=QtWidgets.QPushButton("Upload")
    UploadButton.resize(20, 10)

    w5.addWidget(QtWidgets.QLabel("""Node:"""), row = 0, col= 0)
    w5.addWidget(Node, row=0, col=1)
    w5.addWidget(QtWidgets.QLabel("""Object:"""), row = 1, col= 0)
    w5.addWidget(Object, row=1, col=1)
    w5.addWidget(QtWidgets.QLabel("""Sub index:"""), row = 2, col= 0)
    w5.addWidget(Sub_index, row=2, col=1)
    w5.addWidget(QtWidgets.QLabel("""Variable:"""), row = 3, col= 0)
    w5.addWidget(variable, row=3, col=1)
    w5.addWidget(UploadButton, row=4, col=1)

    def upload():
        #send the folling things to the Connecting thing
        print(Node.currentText(), Object.text(), variable.text(), Sub_index.text())
        w2.write('uploaded\n' , scrollToBottom='auto')
    UploadButton.clicked.connect(upload)

    return w5 
d5.addWidget(WriteWidget(node_list))

#w4 = pg.LayoutWidget()
#GenPLotButton=QtWidgets.QPushButton("Generate new plot")
#w4.addWidget(GenPLotButton, row=0, col=0)

w4 = pg.GraphicsLayoutWidget(show=True)
w4.setWindowTitle('pyqtgraph example: Scrolling Plots')

# 1) Simplest approach -- update data in the array such that plot appears to scroll
#    In these examples, the array size is fixed.
p2 = w4.addPlot()
data1 = np.random.normal(size=300)
data2 = np.random.normal(size=300)
curve1 = p2.plot(data1, pen={'color':(0, 156, 129), 'width':3})
curve2 = p2.plot(data2, pen={'color':'w', 'width':3})
pg.setConfigOptions(antialias=True)

ptr1 = 0
lastTime = perf_counter()
fps = None

def update1():
    global data1, data2, ptr1, fps, lastTime

    data1[:-1] = data1[1:]  # shift data in the array one sample left
                            # (see also: np.roll)
    data1[-1] = np.random.normal()

    data2[:-1] = data2[1:]  # shift data in the array one sample left
                            # (see also: np.roll)
    data2[-1] = np.random.normal()
    
    ptr1 += 1
    curve1.setData(data1)
    curve1.setPos(ptr1, 0)

    curve2.setData(data2)
    curve2.setPos(ptr1, 0)

    now = perf_counter()
    dt = now - lastTime
    lastTime = now
    
    if fps is None:
        fps = 1.0 / dt
    else:
        s = np.clip(dt * 3.0, 0, 1)
        fps = fps * (1 - s) + (1.0 / dt) * s
    p2.setTitle("%0.2f fps" % fps)

# update all plots
def update():
    update1()
timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(15)

d4.addWidget(w4)

#make the list of nodes on the canbus, with dropdown list of the objects
w6 =pg.mkQApp()
w6 = pg.TreeWidget()
node_list = [41, 42, 10]
ObjectlistNode1= [46546, 6454, 4]

for i in range(len(node_list)):
    
    Name = "Node " + str(node_list[i])
    item  = QtWidgets.QTreeWidgetItem([Name]) # make toplevel ITEM
    w6.addTopLevelItem(item)

    for j in range(len(ObjectlistNode1)):               #for every object in the list
        object= QtWidgets.QTreeWidgetItem([str(ObjectlistNode1[j])]) # add a Child to the Node with the name of the Node
        item.addChild(object)

d6.addWidget(w6)

win.show()

if __name__ == '__main__':
    pg.exec()