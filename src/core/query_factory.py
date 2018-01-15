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

import re
from xml.dom.minidom import parseString

from QuickOSM.src.core.definitions import ALL_OSM_TYPES
from QuickOSM.src.core.exceptions import QueryFactoryException


class QueryFactory(object):

    """Build a XML or OQL query."""

    def __init__(
            self,
            key=None,
            value=None,
            is_extent_template=None,
            nominatim_place=None,
            is_around_template=None,
            around_distance=None,
            osm_objects=ALL_OSM_TYPES,
            output='xml',
            timeout=25,
            print_mode='body',
    ):
        """
        Constructor with key=value according to OpenStreetMap.

        A bbox or nominatim can be provided.

        :param key: OSM key.
        :type key: str

        :param value: OSM value.
        :type value: str

        :param is_extent_template: If we want a {{bbox}} in the query.
        :type is_extent_template: bool

        :param nominatim_place: A place name if needed.
        :type nominatim_place: str

        :param is_around_template: Around or in.
        :type is_around_template: bool

        :param around_distance: Distance to use if it's an around query.
        :type around_distance: int

        :param osm_objects: List of osm objects to query on (node/way/relation)
        :type osm_objects: list

        :param output:output of overpass : XML or JSON
        :type output: str

        :param timeout: Timeout of the query
        :type timeout: int

        :param print_mode: Print type of the overpass query (read overpass doc)
        :type print_mode: str
        """
        self._key = key
        self._value = value
        self._is_extent_template = is_extent_template
        self._nominatim_place = nominatim_place
        self._is_around_template = is_around_template
        self._distance_around = around_distance
        self._osm_objects = osm_objects
        self._timeout = timeout
        self._output = output
        self._print_mode = print_mode

    def check_parameters(self):
        """Internal function to check that the query can be built."""
        if self._nominatim_place and self._is_extent_template:
            raise QueryFactoryException('Nominatim OR bbox, not both.')

        if not self._key:
            raise QueryFactoryException('key required')

        if len(self._osm_objects) < 1:
            raise QueryFactoryException('OSM object required')

        for osmObject in self._osm_objects:
            if osmObject not in ALL_OSM_TYPES:
                raise QueryFactoryException('Wrong OSM object')

        if self._is_around_template and not self._distance_around:
            raise QueryFactoryException('No distance provided with "around".')

        if self._is_around_template and not self._nominatim_place:
            raise QueryFactoryException('No nominatim provided with "around".')

    @staticmethod
    def get_pretty_xml(query):
        """Helper to get a good indentation of the query."""
        xml = parseString(query.encode('utf-8'))
        return xml.toprettyxml()

    @staticmethod
    def replace_template(query):
        """Add some templates tags to the query {{ }}."""
        query = re.sub(
            r' area_coords="(.*?)"', r' {{geocodeCoords:\1}}', query)
        query = re.sub(
            r' area="(.*?)"', r' {{geocodeArea:\1}}', query)
        query = query.replace(' bbox="custom"', ' {{bbox}}')
        return query

    def generate_xml(self):
        """Generate the XML."""
        query = '<osm-script output="%s" timeout="%s">' % \
                (self._output, self._timeout)

        if self._nominatim_place:
            nominatim = [
                name.strip() for name in self._nominatim_place.split(';')]
        else:
            nominatim = None

        if nominatim and not self._is_around_template:

            for i, one_nominatim in enumerate(nominatim):
                query += u'<id-query area="%s" into="area_%s"/>' % \
                         (one_nominatim, i)

        query += u'<union>'

        loop = 1 if not nominatim else len(nominatim)

        for osmObject in self._osm_objects:
            for i in range(0, loop):
                query += u'<query type="%s">' % osmObject.value
                query += u'<has-kv k="%s" ' % self._key
                if self._value:
                    query += u'v="%s"' % self._value

                query += u'/>'

                if self._nominatim_place and not self._is_around_template:
                    query += u'<area-query from="area_%s" />' % i

                elif self._nominatim_place and self._is_around_template:
                    query += u'<around area_coords="%s" radius="%s" />' % \
                             (nominatim[i], self._distance_around)

                elif self._is_extent_template:
                    query = u'%s<bbox-query bbox="custom" />' % query

                query += u'</query>'

        query += u'</union>'
        query += u'<union>'
        query += u'<item />'
        query += u'<recurse type="down"/>'
        query += u'</union>'
        query += u'<print mode="%s" />' % self._print_mode
        query += u'</osm-script>'

        return query

    def make(self):
        """Make the query

        @return: query
        @rtype: str
        """
        # self.check_parameters()
        query = self.generate_xml()

        # get_pretty_xml works only with a valid XML, no template {{}}
        # So we replace fake XML after
        query = QueryFactory.get_pretty_xml(query)

        # get_pretty_xml add on XML header, let's remove the first line
        query = '\n'.join(query.split('\n')[1:])

        query = QueryFactory.replace_template(query)
        query = query.replace('	', '    ')

        return query
