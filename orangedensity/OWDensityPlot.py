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
    xvariable = Setting("")
    yvariable = Setting("")
    squareAspectRatio = Setting(0)

    class Inputs:
        data = Input("Data", Orange.data.Table)

    def __init__(self):
        super().__init__()

        # GUI
        # control area
        box = gui.widgetBox(self.controlArea)
        self.infob = gui.widgetLabel(box, "")
        gui.separator(self.controlArea)

        self.optionsBox = gui.widgetBox(self.controlArea, "Options")
        self.comboBoxXVariable = gui.comboBox(
            self.optionsBox,
            self,
            "xvariable",
            label="X Variable",
            sendSelectedValue=True,
            callback=[self.selection, self.checkCommit]
        )
        self.comboBoxYVariable = gui.comboBox(
            self.optionsBox,
            self,
            "yvariable",
            label="Y Variable",
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
        gui.comboBox(
            self.optionsBox,
            self,
            "colormap",
            items=pg.colormap.listMaps(),
            label="Color Map",
            sendSelectedValue=True,
            callback=[self.selection, self.checkCommit]
        )
        gui.checkBox(
            self.optionsBox,
            self,
            "squareAspectRatio",
            label="Square Aspect Ratio",
            callback=[self.selection, self.checkCommit]
        )

        # main area
        gui.widgetBox(self.mainArea, orientation="vertical")
        self.plotItem = pg.PlotItem()
        self.imv = pg.ImageView(view=self.plotItem)
        self.imv.setColorMap(pg.colormap.get(self.colormap))
        self.mainArea.layout().addWidget(self.imv)
        self.dataset =  None

    @Inputs.data
    def set_data(self, dataset):
        if dataset is not None:

            varnames = []
            for vardomain in dataset.domain:
                varnames.append(str(vardomain))
            self.comboBoxXVariable.clear()
            self.comboBoxXVariable.addItems(varnames)
            self.comboBoxXVariable.setCurrentText(self.xvariable)
            self.comboBoxYVariable.clear()
            self.comboBoxYVariable.addItems(varnames)
            self.comboBoxYVariable.setCurrentText(self.yvariable)
            self.dataset = dataset
            if self.xvariable == "":
                self.xvariable = self.comboBoxXVariable.currentText()
            if self.yvariable == "":
                self.yvariable = self.comboBoxYVariable.currentText()
            self.updatePlot()

    def updatePlot(self):
        indexXVar = 0
        try:
            indexXVar = self.dataset.domain.index(self.xvariable)
        except:
            print(f'XVariable {self.xvariable} not found.')
        
        indexYVar = 0
        try:
            indexYVar = self.dataset.domain.index(self.yvariable)
        except:
            print(f'YVariable {self.yvariable} not found.')

        xVals = np.array(self.dataset[:, indexXVar]).flatten()
        yVals = np.array(self.dataset[:, indexYVar]).flatten()
        hist,xEdges,yEdges = np.histogram2d(xVals, yVals, bins=(self.xbins, self.ybins))
        self.imv.setColorMap(pg.colormap.get(str(self.colormap), source=None))
        self.imv.setImage(hist)
        self.imv.view.invertY(False)
        minX = np.min(xVals)
        maxX = np.max(xVals)
        minY = np.min(yVals)
        maxY = np.max(yVals)
        histBounds = QtCore.QRectF(minX, minY, maxX-minX, maxY-minY)
        self.imv.getImageItem().setRect(histBounds)
        if self.squareAspectRatio > 0:
            self.plotItem.getViewBox().setAspectLocked(True)
        else:
            self.plotItem.getViewBox().setAspectLocked(False)
        self.plotItem.getViewBox().setRange(histBounds, disableAutoRange=True)
        
    def selection(self):
        print('selection')

    def commit(self):
        print('commit')

    def checkCommit(self):
        self.updatePlot()

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