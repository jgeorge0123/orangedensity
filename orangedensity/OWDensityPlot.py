import sys
import numpy as np
from scipy import stats
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
    colormap = Setting("turbo")
    xvariable = Setting("")
    yvariable = Setting("")
    squareAspectRatio = Setting(0)
    densityType = Setting("2D Histogram")
    useManualKDEBandwidth = Setting(0)
    manualKDEBandwidth = Setting(0.5)
    compare = Setting(0)

    class Inputs:
        data = Input("Data", Orange.data.Table)
        dataB = Input("Data Compare", Orange.data.Table)

    def __init__(self):
        super().__init__()

        # GUI
        # control area
        box = gui.widgetBox(self.controlArea)
        self.infob = gui.widgetLabel(box, "")
        gui.separator(self.controlArea)

        self.optionsBox = gui.widgetBox(self.controlArea, "Options")
        self.comboBoxType = gui.comboBox(
            self.optionsBox,
            self,
            "densityType",
            label="Density Type",
            items=["2D Histogram", "Gaussian KDE"],
            sendSelectedValue=True,
            callback=[self.selection, self.checkCommit]
        )
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
        gui.checkBox(
            self.optionsBox,
            self,
            "useManualKDEBandwidth",
            label="Manual KDE Bandwidth",
            callback=[self.selection, self.checkCommit]
        )
        self.manualKDEBandwidthDoubleSpin = gui.doubleSpin(
            self.optionsBox,
            self,
            "manualKDEBandwidth",
            label="KDE Bandwidth",
            step=0.001,
            minv=0,
            maxv=100000000,
            callback=[self.selection, self.checkCommit]
        )
        gui.checkBox(
            self.optionsBox,
            self,
            "compare",
            label="Compare distributions",
            callback=[self.selection, self.checkCommit]
        )

        # main area
        gui.widgetBox(self.mainArea, orientation="vertical")
        self.plotItem = pg.PlotItem()
        self.imv = pg.ImageView(view=self.plotItem)
        self.imv.setColorMap(pg.colormap.get(self.colormap))
        self.mainArea.layout().addWidget(self.imv)
        self.dataset = None
        self.datasetB = None

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
    
    @Inputs.dataB
    def set_dataB(self, dataset):
        self.datasetB = dataset
        self.updatePlot()

    def histogram(self, xVals, yVals, minX, maxX, minY, maxY):
        density = None
        if self.densityType == "2D Histogram":
            hist,xEdges,yEdges = np.histogram2d(xVals, yVals, bins=(self.xbins, self.ybins))
            density = hist
        else:
            xs = np.linspace(minX, maxX, self.xbins)
            ys = np.linspace(minY, maxY, self.ybins)
            X, Y = np.meshgrid(xs,ys)
            positions = np.vstack([X.ravel(), Y.ravel()])
            values = np.vstack([xVals, yVals])
            bw_method = None
            if self.useManualKDEBandwidth:
                bw_method = self.manualKDEBandwidth
            kernel = stats.gaussian_kde(values, bw_method=bw_method)
            Z = np.reshape(kernel(positions).T, X.shape)
            density = Z.T
        return density

    def updatePlot(self):
        if self.dataset is not None:
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
            minX = np.min(xVals)
            maxX = np.max(xVals)
            minY = np.min(yVals)
            maxY = np.max(yVals)
            density = self.histogram(xVals, yVals, minX, maxX, minY, maxY)

            if self.datasetB is not None and self.compare > 0:
                xVals = np.array(self.datasetB[:, indexXVar]).flatten()
                yVals = np.array(self.datasetB[:, indexYVar]).flatten()
                densityB = self.histogram(xVals, yVals, minX, maxX, minY, maxY)
                density = density/np.sum(density.flatten()) - densityB/np.sum(densityB.flatten())

            self.imv.setColorMap(pg.colormap.get(str(self.colormap), source=None))
            self.imv.setImage(density)
            self.imv.view.invertY(False)
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