# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : RT QSpider
Description          : Convert a table to an event layer or a spider diagram
Date                 : Nov 14, 2012 
copyright            : (C) 2012 by Giuseppe Sucameli (Faunalia)
email                : brush.tyler@gmail.com

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from .dialogCRS import CRSDialog

from .ui.dialog_ui import Ui_RTQSpiderDlg

class RTQSpiderDlg(QDialog, Ui_RTQSpiderDlg):
    def __init__(self, vl, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.vl = vl
        self.outFn = None

        self.crsEdit.setText( "EPSG:4326" )
        self.populateCombos()

        QObject.connect(self.selectCrsBtn, SIGNAL("clicked()"), self.selectCrs)

    def selectCrs(self):
        dlg = CRSDialog( "Select the CRS", self )
        if dlg.exec_():
            self.crsEdit.setText(dlg.getProjection())

    def populateCombos(self):
        # populate the geometry type combo
        for val, name in {QGis.WKBPoint:"Point", QGis.WKBLineString:"Line"}.iteritems():
            self.geomTypeCombo.addItem(name, val)

        # populate the fields combos with numeric fields
        for index, fld in enumerate(self.vl.dataProvider().fields()):
            self.xPointCombo.addItem( fld.name(), index )
            self.yPointCombo.addItem( fld.name(), index )
 
            self.x1LineCombo.addItem( fld.name(), index )
            self.y1LineCombo.addItem( fld.name(), index )
            self.x2LineCombo.addItem( fld.name(), index )
            self.y2LineCombo.addItem( fld.name(), index )

    def accept(self):
        mode = self.geomTypeCombo.itemData( self.geomTypeCombo.currentIndex() )

        # check whether required values was filled
        if mode == QGis.WKBPoint:
            if self.xPointCombo.currentIndex() < 0 or \
                    self.yPointCombo.currentIndex() < 0:
                return
            x1 = self.xPointCombo.itemData( self.xPointCombo.currentIndex() )
            y1 = self.yPointCombo.itemData( self.yPointCombo.currentIndex() )
            if -1 in (x1, y1):
               # robusness check: this block of code should never be reached
               raise ValueError("invalid field index found...")

        elif mode == QGis.WKBLineString:
            if self.x1LineCombo.currentIndex() < 0 or \
                    self.y1LineCombo.currentIndex() < 0 or \
                    self.x2LineCombo.currentIndex() < 0 or \
                    self.y2LineCombo.currentIndex() < 0:
                return
            x1 = self.x1LineCombo.itemData( self.x1LineCombo.currentIndex() )
            y1 = self.y1LineCombo.itemData( self.y1LineCombo.currentIndex() )
            x2 = self.x2LineCombo.itemData( self.x2LineCombo.currentIndex() )
            y2 = self.y2LineCombo.itemData( self.y2LineCombo.currentIndex() )
            if -1 in (x1, y1, x2, y2):
               # robusness check: this block of code should never be reached
               raise ValueError("invalid field index found...")

        # let's ask for a output shapefile path
        settings = QSettings()
        lastDir = settings.value("/rt_qspider/lastUsedDir", "", type=str)
        filename = QFileDialog.getSaveFileName(self, 
                "Choose where to save the output shapefile", lastDir, 
                "Shapefile (*.shp)")
        if filename == "":
            return # cancel pressed
        if filename[-4:] != ".shp":
            filename += ".shp"
        settings.setValue("/rt_qspider/lastUsedDir", QFileInfo(filename).filePath())

        # create the vector file writer
        # TODO: allow user to choose encoding
        writer = QgsVectorFileWriter(filename, "System", self.vl.dataProvider().fields(), 
                mode, self.getCrs(), "ESRI Shapefile")
        if writer.hasError() != QgsVectorFileWriter.NoError:
            QMessageBox.warning(self, "RT QSpider", 
                u"Failed to create the output shapefile '%s' due to the following error:\n%s" % (filename, writer.errorMessage()))
            return

        errors = []
        count = 0
        
        # iterate through al the features
        features = self.vl.getFeatures()
        for feat in features:
            # create the new feature geometry from its coordinates
            x1d_toconv = feat[x1]
            y1d_toconv = feat[y1]
            try:
                x1d = float(x1d_toconv)
                y1d =  float(y1d_toconv)
            except:
                continue
            p1 = QgsPoint(x1d, y1d)
            if mode == QGis.WKBPoint:
                geom = QgsGeometry.fromPoint(p1)

            elif mode == QGis.WKBLineString:
                x2d_toconv = feat[x2]
                y2d_toconv = feat[y2]
                try:
                    x2d = float(x2d_toconv)
                    y2d =  float(y2d_toconv)
                except:
                    continue
                p2 = QgsPoint(x2d, y2d)
                geom = QgsGeometry.fromPolyline( [p1, p2] )

            feat.setGeometry(geom)

            # write the feature
            writer.addFeature(feat)
            if writer.hasError() != QgsVectorFileWriter.NoError:
                errors.append(writer.errorMessage())
            count += 1

        # close the writer and check for failures
        if writer.hasError() != QgsVectorFileWriter.NoError:
            QMessageBox.warning(self, "RT QSpider", 
                u"Failed to write %s features of %s due to the following errors:\n%s" % (len(errors), count, "\n".join(errors)))

            # exit if no features was added
            if len(errors) >= count:
                QFile(filename).remove()
                return

        self.outFn = filename
        QDialog.accept(self)

    def getOutputFilename(self):
        return self.outFn

    def getCrs(self):
        crs = QgsCoordinateReferenceSystem( self.crsEdit.text() )
        if not crs.isValid():
            if not crs.createFromProj4( self.crsEdit.text() ):
               # robusness check: this block of code should never be reached
               raise ValueError("invalid crs found...")
        return crs
