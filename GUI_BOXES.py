#GUI_BOXES
import sys
#from CAN_COM import *
from CAN_COM_DEMO import *
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



#make the window to write date to the NeNa
def WriteWidget(w2, node_list):
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



def NodeTree():
    w6 = pg.TreeWidget()
    node_list = [40, 41]
    ObjectlistNode1= [6060, 6061, 6062]

    for i in range(len(node_list)):
        
        Name = "Node " + str(node_list[i])
        item  = QtWidgets.QTreeWidgetItem([Name]) # make toplevel ITEM
        w6.addTopLevelItem(item)

        for j in range(len(ObjectlistNode1)):               #for every object in the list
            object= QtWidgets.QTreeWidgetItem([str(ObjectlistNode1[j])]) # add a Child to the Node with the name of the Node
            item.addChild(object)
    return(w6)

#Make the Connection manager window/box
def ConnectWidget(w2):
    """ Makes a widget that calls the CAN_COM library to connect to a canbus"""

    #call layoutmanager and make the window w3
    w3 = pg.LayoutWidget()
    #Make buttons and inputsfields widgets
    bustype=QLineEdit()
    channel=QLineEdit()
    bitrate=QComboBox()
    bitrate_list = [1000000, 800000, 500000, 250000, 125000, 50000, 20000, 10000]
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
    def connect(bitrate_list, bitrate):
        #bitrate_list = [1000000, 800000, 500000, 250000, 125000, 50000, 20000, 10000]
        w2.write("connecting....\n", scrollToBottom='auto')
        #run the Connect script
        #CAN_COM.__init__(bustype.text(), channel.text(), bitrate_list(bitrate.currentIndex()))
        #CAN_COM(bustype.text(), channel.text(), bitrate_list(bitrate.currentIndex()))

        #DEMO
        CAN_COM(bustype.text(), channel.text(), int(bitrate.currentText())) # Werkt wel met currentText!!
        node_list = CAN_COM.scan_bus(1)
        string_of_nums = ','.join(str(num) for num in node_list)
        w2.write("Found nodes: " + string_of_nums + "\n")
        #When connected set light to green
        Light.setStyleSheet("background-color : green")
    Connect_button.clicked.connect(lambda: connect(bitrate_list, bitrate))
    #send the finised window widget outside the function
    return w3