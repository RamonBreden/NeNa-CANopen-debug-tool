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

from GUI_BOXES import *

import sys
from CAN_COM import *
#from CAN_COM_DEMO import *
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
d1 = Dock("Plot parameters", size=(700, ), hideTitle=True)     ## give this dock the minimum possible size
d2 = Dock("Console", size=(300,300), closable=True, hideTitle=True)
d3 = Dock("CAN BUS Connection", size=(1,200), hideTitle=False)
d4 = Dock("Plotgenerator", size=(1,200), hideTitle=True)
d5 = Dock("Write to Objects", size=(1,200), hideTitle=False)
d6 = Dock("Object List", size=(1,200), hideTitle=False)
#d7 = Dock("plot", size=(1,1),closable=True, hideTitle=False)

area.addDock(d1, 'right')     
area.addDock(d2, 'left')     
area.addDock(d3, 'bottom', d2)
area.addDock(d4, 'bottom', d1)     
area.addDock(d5, 'bottom', d3)  
area.addDock(d6, 'bottom', d5)  
#area.addDock(d7, 'bottom', d4)

## Test ability to move docks programatically after they have been placed
#area.moveDock(d4, 'top', d2)     ## move d4 to top edge of d2  ## move d6 to stack on top of d4
#area.moveDock(d5, 'top', d2)     ## move d5 to top edge of d2

## Add widgets into each dock

## first dock gets save/restore buttons


w2 = ConsoleWidget()
d2.addWidget(w2)

#generate the w3 widget and put it into the d3 box
d3.addWidget(ConnectWidget(w2))

# Gefixt op een janky manier ;)

node_list = [40, 41]

#make the window to write date to the NeNa
d5.addWidget(WriteWidget(w2, node_list))

#make the list of nodes on the canbus, with dropdown list of the objects
d6.addWidget(NodeTree())

#----------------------------------------------------------------------------------------------------
# create the ParameterTree


children = [
    dict(name='linewidth', type='float', limits=[0.1, 50], value=1, step=0.1),
    dict(name='Color', type='list', limits= ['white','blue' ],value='white' ),
    dict(name='Lines', type='int', limits= [1, 5] ),
    dict(name='Plot objects', type='bool', value= False ),
    dict(name='amount lines', type='int', limits= [1, 5] ),
    dict(name='Line 1', type='list', limits = [] ), 
]
params = pg.parametertree.Parameter.create(name='Parameters', type='group', children=children)
pt = pg.parametertree.ParameterTree(showHeader=False)
pt.setParameters(params)

d1.addWidget(pt)




#Scroll Plot ------------------------------------------------------------------------------------------------
w4 = pg.GraphicsLayoutWidget(show=True)
w4.setWindowTitle('pyqtgraph example: Scrolling Plots')
p2 = w4.addPlot()

data1 = np.random.normal(size=300)
data2 = np.random.normal(size=300)
curve1 = p2.plot(data1) #, pen={'color':(0, 156, 129), 'width':3}
curve2 = p2.plot(data2, pen={'color':(0, 156, 129), 'width':3})

pg.setConfigOptions(antialias=True)

ptr1 = 0
lastTime = perf_counter()
fps = None
#lines   = params.child('nb_lines').value()


def update_plot():
    global data1, data2, ptr1, fps, lastTime

    line_color       = params.child('Color').value()
    line_width       = params.child('linewidth').value()
    amount_of_lines =  params.child('Lines').value()
    #Object       = params.child('Line 1').value()


    

    data1[:-1] = data1[1:]  # shift data in the array one sample left
                            # (see also: np.roll)
    data1[-1] = np.random.normal()

    data2[:-1] = data2[1:]  # shift data in the array one sample left
                            # (see also: np.roll)
    data2[-1] = np.random.normal()
    
    ptr1 += 1



    curve1.setData(data1)
    curve1.setPos(ptr1, 0)
    curve1.setPen(color=line_color, width=line_width)
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

timer = pg.QtCore.QTimer()
timer.timeout.connect(update_plot)
timer.start(15)  

d4.addWidget(w4)

#--------------------------------------------------------------------------------------------------------------------------------------------
# the function that updates the parameter tree when it is i called
def updateparametertree():
    w2.write("Parameter tree changing\n", scrollToBottom='auto')
    amount_of_lines =  params.child('amount lines').value()

    for i in range(amount_of_lines):
        num = str(i+1)

        #params.addChild(dict(name= 'line '+num, type='int')  ) 
        lineparameters= [ 
            dict(name='Node', type='int', limits= [1, 5] ),
            dict(name='object', type='int', limits= [1, 5] ),
            dict(name='Color', type='list', limits= ['white','blue' ],value='white' ),
        ]
        line_params = pg.parametertree.Parameter.create(name='line'+num, type='group', children=lineparameters)
        pt.addParameters(line_params)
        


   # line_params = pg.parametertree.Parameter.create(name='Line Paramaters', type='group', children=lineparameters)
    #params.linename.Addchild(name= 'line'+i, type='int'  ) 
    #start plotting data when the it is enabled.

    if params.child('Plot objects').value() == True:
        # update all plots

        print ('done')
        timer = pg.QtCore.QTimer()
        timer.timeout.connect(update_plot)
        timer.start(15)   

params.sigTreeStateChanged.connect(updateparametertree) # looks at the parameter tree and when it changes it will run the update function.

#shows the window that is made 
win.show()
#This function keeps the GUI running 
if __name__ == '__main__':
    pg.exec()