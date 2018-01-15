# -*- coding: utf-8 -*-

"""
/***************************************************************************
 QuickOSM
                                 A QGIS plugin
 Download OpenStreetMap data
                              -------------------
        begin                : 2017-11-11
        copyright            : (C) 2017 by Etienne Trimaille
        email                : etienne dot trimaille at gmail dot com
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

__author__ = 'Etienne Trimaille'
__date__ = '2017-11-11'
__copyright__ = '(C) 2017 by Etienne Trimaille'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtGui import QIcon

from qgis.core import QgsProcessingProvider

from QuickOSM.src.quick_osm_processing.core.query_factory import (
    QueryFactoryAlgorithm)
from QuickOSM.src.utilities.utilities import resources_path


class QuickOsmProvider(QgsProcessingProvider):
    def __init__(self):
        super().__init__()
        self.alglist = [
            QueryFactoryAlgorithm(),
        ]

    def getAlgs(self):
        return self.alglist

    def id(self, *args, **kwargs):
        return 'quickosm'

    def name(self, *args, **kwargs):
        return 'QuickOSM'

    def icon(self):
        return QIcon(resources_path('QuickOSM.svg'))

    def svgIconPath(self):
        return resources_path('QuickOSM.svg')

    def loadAlgorithms(self, *args, **kwargs):
        for alg in self.alglist:
            self.addAlgorithm(alg)
