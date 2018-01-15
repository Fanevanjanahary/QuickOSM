"""
/***************************************************************************
        QuickOSM QGIS plugin
        OSM Overpass API frontend
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

from enum import Enum


class OsmType(Enum):
    Node = 'node'
    Way = 'way'
    Relation = 'relation'


class LayerType(Enum):
    Points = 'points'
    Lines = 'lines'
    Multilinesstrings = 'multilinestrings'
    MultiPolygons = 'multipolygons'


ALL_LAYER_TYPES = [
    LayerType.Points,
    LayerType.Lines,
    LayerType.Multilinesstrings,
    LayerType.MultiPolygons
]
ALL_OSM_TYPES = [OsmType.Node, OsmType.Way, OsmType.Relation]

# The order is important. The first one is the default server.
SERVER_LIST = [
    'http://www.overpass-api.de/api/interpreter',
    'http://overpass.osm.rambler.ru/cgi/interpreter',
    'http://overpass.osm.ch/api/interpreter',
]
