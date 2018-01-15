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
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Etienne Trimaille'
__date__ = '2017-11-11'
__copyright__ = '(C) 2017 by Etienne Trimaille'


import inspect
import os
import sys

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load QuickOSM class from file QuickOSM.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .quick_osm import QuickOSMPlugin
    return QuickOSMPlugin()
