# -*- coding: utf-8 -*-

"""
***************************************************************************
    dialogCRS.py
    ---------------------
    Date                 : June 2010
    Copyright            : (C) 2010 by Giuseppe Sucameli
    Email                : brush dot tyler at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
import qgis

__author__ = 'Giuseppe Sucameli'
__date__ = 'June 2010'
__copyright__ = '(C) 2010, Giuseppe Sucameli'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

class CRSDialog(QDialog):
  def __init__(self, title, parent=None):
      QDialog.__init__(self, parent)
      self.setWindowTitle( title )

      layout = QVBoxLayout()
      self.selector = QgsProjectionSelector(self)
      buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Close)

      layout.addWidget(self.selector)
      layout.addWidget(buttonBox)
      self.setLayout(layout)

      self.connect(buttonBox, SIGNAL("accepted()"), self.accept)
      self.connect(buttonBox, SIGNAL("rejected()"), self.reject)

  def authId(self):
      return str(self.selector.selectedAuthId())

  def getProjection(self):
      if self.selector.selectedAuthId() != 0:
          return self.authId()

      return str("")

