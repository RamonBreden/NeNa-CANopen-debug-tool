from time import perf_counter
import numpy as np
import pyqtgraph as pg

win = pg.GraphicsLayoutWidget(show=True)
win.setWindowTitle('pyqtgraph example: Scrolling Plots')

# 1) Simplest approach -- update data in the array such that plot appears to scroll
#    In these examples, the array size is fixed.
p2 = win.addPlot()
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

if __name__ == '__main__':
    pg.exec()