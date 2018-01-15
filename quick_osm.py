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

from qgis.core import QgsApplication

from src.quick_osm_processing.quick_osm_provider import QuickOsmProvider


class QuickOSMPlugin:

    def __init__(self):
        self.provider = QuickOsmProvider()
        # noinspection PyArgumentList
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        pass

    def unload(self):
        # noinspection PyArgumentList
        QgsApplication.processingRegistry().removeProvider(self.provider)
