import sys
import numpy as np
import pyqtgraph as pg
import Orange.data
from PyQt5 import QtWidgets, QtCore, QtGui
from Orange.widgets import widget, gui
from Orange.widgets.utils.signals import Input, Output
from orangewidget.widget import OWBaseWidget, Input, Output
from orangewidget.settings import Setting
from orangewidget.utils.widgetpreview import WidgetPreview

class OWDensityPlot(widget.OWWidget):
    name = "Density Plot"
    description = "Create a 2D histogram"
    icon = "icons/OWDensityPlot.svg"
    priority = 10
    want_main_area = True
    resizing_enabled = True
    xbins = Setting(10)
    ybins = Setting(10)
    colormap = Setting("viridis")
    commitOnChange = Setting(0)

    class Inputs:
        data = Input("Data", Orange.data.Table)

    def __init__(self):
        super().__init__()

        # GUI
        # control area
        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(
            box, "No data on input yet, waiting to get something."
        )
        self.infob = gui.widgetLabel(box, "")
        gui.separator(self.controlArea)
        self.optionsBox = gui.widgetBox(self.controlArea, "Options")
        gui.comboBox(
            self.optionsBox,
            self,
            "colormap",
            items=pg.colormap.listMaps(),
            label="Color Map",
            sendSelectedValue=True,
            callback=[self.selection, self.checkCommit]
        )
        gui.spin(
            self.optionsBox,
            self,
            "xbins",
            minv=1,
            maxv=1000,
            step=1,
            label="X Bins",
            callback=[self.selection, self.checkCommit],
        )
        gui.spin(
            self.optionsBox,
            self,
            "ybins",
            minv=1,
            maxv=1000,
            step=1,
            label="Y Bins",
            callback=[self.selection, self.checkCommit],
        )
        gui.checkBox(
            self.optionsBox, self, "commitOnChange", "Commit data on selection change"
        )
        gui.button(self.optionsBox, self, "Commit", callback=self.commit)

        #self.optionsBox.setDisabled(True)

        # main area
        gui.widgetBox(self.mainArea, orientation="vertical")

        self.plotItem = pg.PlotItem()
        self.imv = pg.ImageView(view=self.plotItem)
        self.imv.setColorMap(pg.colormap.get(self.colormap))
        self.mainArea.layout().addWidget(self.imv)

    @Inputs.data
    def set_data(self, dataset):
        if dataset is not None:
            self.infoa.setText("%d instances in input data set" % len(dataset))
            indices = np.random.permutation(len(dataset))
            indices = indices[:int(np.ceil(len(dataset) * 0.1))]
            self.updatePlot()
        else:
            self.infoa.setText(
                "No data on input yet, waiting to get something.")
            self.infob.setText('')

    def updatePlot(self):
        xs = np.linspace(0,1,self.xbins)
        ys = np.linspace(0,1,self.ybins)
        X,Y = np.meshgrid(xs,ys)
        data = X + np.sin(Y)

        self.imv.setColorMap(pg.colormap.get(str(self.colormap), source=None))
        self.imv.setImage(data)
        self.imv.view.invertY(False)
        self.imv.getImageItem().setRect(QtCore.QRectF(0,0,1,1))
        self.plotItem.autoRange()
    
    def selection(self):
        #if self.dataset is None:
        #    return
        print('selection')

    def commit(self):
        print('commit')

    def checkCommit(self):
        self.updatePlot()
        #print('checkCommit')
        #if self.commitOnChange:
            #self.commit()

def main(argv=sys.argv):
    from AnyQt.QtWidgets import QApplication
    app = QApplication(list(argv))
    args = app.arguments()
    if len(args) > 1:
        filename = args[1]
    else:
        filename = "iris"

    ow = OWDensityPlot()
    ow.show()
    ow.raise_()

    dataset = Orange.data.Table(filename)
    ow.set_data(dataset)
    ow.handleNewSignals()
    app.exec_()
    ow.set_data(None)
    ow.handleNewSignals()
    return 0


if __name__ == "__main__":
    sys.exit(main())