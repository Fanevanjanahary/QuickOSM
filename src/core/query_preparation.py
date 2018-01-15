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

from qgis.PyQt.QtCore import QUrl, QUrlQuery

# from api.nominatim import Nominatim
from QuickOSM.src.core.definitions import SERVER_LIST
from QuickOSM.src.core.exceptions import (
    QueryNotSupported, QueryFactoryException)


class QueryPreparation(object):

    """Prepare the query before sending it to Overpass."""

    def __init__(
            self, query, extent=None, nominatim_place=None,
            overpass=SERVER_LIST[0], output_format='xml'):
        """Constructor.

        :param query: The query to prepare.
        :type query: str

        :param extent: The extent to use in 4326, if needed. It can be None.
        :type extent: QgsRectangle

        :param nominatim_place: A name or a list of place names.
        :type nominatim_place: str, list(str)
        """
        self._query = query
        self._query_prepared = query
        self_url = None
        self._extent = extent
        self._nominatim_places = nominatim_place
        self._overpass = overpass
        self._output_format = output_format

        self._query_is_ready = False

    @property
    def query(self):
        """The original query.

        :return: The original query.
        :rtype: str
        """
        return self._query

    @property
    def final_query(self):
        """The generated query or None if it's not yet generated.

        :return: The final query.
        :rtype: str
        """
        if self._query_is_ready:
            return self._query_prepared
        else:
            return None

    def is_oql_query(self):
        """Return if the query is written in OQL or not.

        :return: If the it's OQL query.
        :rtype: bool
        """
        return self._query[-1] == ";"

    def is_compatible(self):
        """The plugin doesn't support all special tags like Overpass Turbo.

        :return: A tuple (bool, reason).
        :rtype: tuple
        """
        template = r'geometry="center"'
        if re.search(template, self._query):
            return False, 'center'

        template = r'out center;'
        if re.search(template, self._query):
            return False, 'center'

        template = r'{{style'
        if re.search(template, self._query):
            return False, '{{style}}'

        template = r'{{data'
        if re.search(template, self._query):
            return False, '{{data}}'

        template = r'{{date'
        if re.search(template, self._query):
            return False, '{{date}}'

        template = r'{{geocodeId:'
        if re.search(template, self._query):
            return False, '{{geocodeId:}}'

        template = r'{{geocodeBbox:'
        if re.search(template, self._query):
            return False, '{{geocodeBbox:}}'

        return True, None

    def _replace_center(self):
        """Replace {{center}} by the centroid of the extent if needed.

        The temporary query will be updated.
        """
        template = r'{{center}}'
        if not re.search(template, self._query_prepared):
            return
        else:
            if self._extent is None:
                raise QueryFactoryException('Missing extent parameter')

        y = self._extent.center().y()
        x = self._extent.center().x()
        if self.is_oql_query():
            new_string = '%s,%s' % (y, x)
        else:
            new_string = 'lat="%s" lon="%s"' % (y, x)

        self._query_prepared = (
            re.sub(template, new_string, self._query_prepared))

    def _replace_bbox(self):
        """Replace {{bbox}} by the extent BBOX if needed.

        The temporary query will be updated.
        """
        template = r'{{bbox}}'
        if not re.search(template, self._query_prepared):
            return
        else:
            if self._extent is None:
                raise QueryFactoryException('Missing extent parameter')

        y_min = self._extent.yMinimum()
        y_max = self._extent.yMaximum()
        x_min = self._extent.xMinimum()
        x_max = self._extent.xMaximum()

        if self.is_oql_query():
            new_string = '%s,%s,%s,%s' % (y_min, x_min, y_max, x_max)
        else:
            new_string = 'e="%s" n="%s" s="%s" w="%s"' % \
                         (x_max, y_max, y_min, x_min)
        self._query_prepared = (
            re.sub(template, new_string, self._query_prepared))

    # def _replace_geocode_coords(query, nominatim_name):
    #     """Replace {{geocodeCoords}} by the centroid of the extent.
    #
    #     :param query: The query.
    #     :type query: basestring
    #
    #     :param nominatim_name: The name of the area.
    #     :type nominatim_name: basestring
    #
    #     :return: The new formatted query.
    #     :rtype: basestring
    #     """
    #     def replace(catch, default_nominatim):
    #
    #         if default_nominatim:
    #             search = default_nominatim
    #         else:
    #             search = catch
    #
    #         nominatim = Nominatim()
    #         lon, lat = nominatim.get_first_point_from_query(search)
    #
    #         if _is_oql(query):
    #             new_string = '%s,%s' % (lat, lon)
    #         else:
    #             new_string = 'lat="%s" lon="%s"' % (lat, lon)
    #
    #         return new_string
    #
    #     template = r'{{(geocodeCoords):([^}]*)}}'
    #     query = re.sub(
    #         template, lambda m: replace(m.groups()[1], nominatim_name), query)
    #     return query
    #
    #
    # def _replace_geocode_area(nominatim_name, query):
    #     """Replace {{geocodeCoords}} by the centroid of the extent.
    #
    #     :param nominatim_name: The name of the area.
    #     :type nominatim_name: basestring
    #
    #     :param query: The query.
    #     :type query: basestring
    #
    #     :return: The new formatted query.
    #     :rtype: basestring
    #     """
    #     def replace(catch, default_nominatim):
    #
    #         if default_nominatim:
    #             search = default_nominatim
    #         else:
    #             search = catch
    #
    #         # if the result is already a number, it's a relation ID.
    #         # we don't perform a nominatim query
    #         if search.isdigit():
    #             osm_id = search
    #         else:
    #             # We perform a nominatim query
    #             nominatim = Nominatim()
    #             osm_id = nominatim.get_first_polygon_from_query(search)
    #
    #         area = int(osm_id) + 3600000000
    #
    #         if _is_oql(query):
    #             new_string = 'area(%s)' % area
    #         else:
    #             new_string = 'ref="%s" type="area"' % area
    #
    #         return new_string
    #
    #     template = r'{{(nominatimArea|geocodeArea):([^}]*)}}'
    #     query = re.sub(template, lambda m: replace(
    #         m.groups()[1], nominatim_name), query)
    #     return query

    def _clean_query(self):
        """Remove extra characters that might be present in the query.

        The temporary query will be updated.
        """
        query = self._query_prepared.strip()

        # Correction of ; in the OQL at the end
        self._query_prepared = re.sub(r';;$', ';', query)

    def prepare_query(self):
        """Prepare the query before sending it to Overpass.

        The temporary query will be updated.

        :return: The final query.
        :rtype: basestring
        """
        result = self.is_compatible()
        if result[0] is not True:
            raise QueryNotSupported(result[1])

        self._clean_query()
        self._replace_bbox()
        self._replace_center()
        # query = _replace_geocode_area(nominatim_name, query)
        # query = _replace_geocode_coords(nominatim_name, query)
        self._query_is_ready = True
        return self._query_prepared

    def prepare_url(self):
        """Prepare a query to be as an URL.

        :return: The URL encoded with the query.
        :rtype: basestring
        """
        if not self._query_prepared:
            return ''

        if self._output_format:
            query = re.sub(
                r'output="[a-z]*"',
                'output="%s"' % self._output_format,
                self._query_prepared)
            query = re.sub(
                r'\[out:[a-z]*',
                '[out:%s' % self._output_format,
                query)
        else:
            query = self._query_prepared

        url_query = QUrl(self._overpass)
        query_string = QUrlQuery()
        query_string.addQueryItem('data', query)
        query_string.addQueryItem('info', 'QgisQuickOSMPlugin')
        url_query.setQuery(query_string)
        return url_query.toString()
