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

from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm
from qgis.core import (
    QgsFeatureRequest,
    QgsFileUtils,
    QgsFileDownloader,
    QgsProcessingParameterString,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterExtent,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFileDestination,
    QgsProcessingOutputString,
    QgsProcessingOutputFile,
    QgsProcessingParameterFeatureSink,
    QgsProcessingException,
    QgsProcessingAlgorithm,
    QgsCoordinateTransform,
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsFeatureSink,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QUrl, QEventLoop


from QuickOSM.src.core.definitions import ALL_LAYER_TYPES
from QuickOSM.src.core.query_factory import QueryFactory
from QuickOSM.src.core.query_preparation import QueryPreparation
from QuickOSM.src.utilities.i18n import tr


class QueryFactoryAlgorithm(QgisAlgorithm):

    """Build a query with parameters."""

    FIELD_KEY = 'FIELD_KEY'
    FIELD_VALUE = 'FIELD_VALUE'
    FIELD_QUERY_EXTENT = 'FIELD_EXTENT'
    FIELD_NOMINATIM = 'FIELD_NOMINATIM'
    FIELD_OSM_OBJECTS = 'FIELD_OSM_OBJECTS'
    FIELD_TIMEOUT = 'FIELD_TIMEOUT'
    OUTPUT_FILE = 'OUTPUT_FILE'
    SKIP_LAYERS = 'SKIP_LAYERS'

    def __init__(self):
        super(QueryFactoryAlgorithm, self).__init__()
        self.still_downloading = True
        self.feedback = None

    @staticmethod
    def name():
        return 'query_factory'

    @staticmethod
    def displayName():
        return tr('Query Factory')

    @staticmethod
    def group():
        return tr('Padawan')

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterString(
                self.FIELD_KEY, tr('Key'), optional=False))

        self.addParameter(
            QgsProcessingParameterString(
                self.FIELD_VALUE, tr('Value'), optional=True))

        self.addParameter(
            QgsProcessingParameterExtent(
                self.FIELD_QUERY_EXTENT,
                tr('Extent, might be empty, incompatible with nominatim'),
                optional=True))

        self.addParameter(
            QgsProcessingParameterString(
                self.FIELD_NOMINATIM,
                tr('Nominatim, might be empty, incompatible with an extent'),
                optional=True))

        self.addParameter(
            QgsProcessingParameterNumber(
                self.FIELD_TIMEOUT,
                tr('Timeout'),
                defaultValue=25,
                minValue=20))

        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_FILE,
                tr('Destination'),
                tr('OSM file (*.osm)')))

        self.addParameter(
            QgsProcessingParameterEnum(
                self.SKIP_LAYERS,
                tr('Skip output layers'),
                options=[f.value for f in ALL_LAYER_TYPES],
                optional=True,
                allowMultiple=True))

        for layer_type in ALL_LAYER_TYPES:
            self.addParameter(QgsProcessingParameterFeatureSink(
                layer_type.value, layer_type.value))

    def checkParameterValues(self, parameters, context):
        extent = self.parameterAsExtent(
            parameters, self.FIELD_QUERY_EXTENT, context)
        nominatim = self.parameterAsString(
            parameters, self.FIELD_NOMINATIM, context)
        if not extent.isEmpty() and nominatim:
            msg = tr(
                "Extent and Nominatim can't be together in the query factory.")
            return False, msg

        return super(QueryFactoryAlgorithm, self).checkParameterValues(
            parameters, context)

    def processAlgorithm(self, parameters, context, feedback):
        self.feedback = feedback
        key = self.parameterAsString(parameters, self.FIELD_KEY, context)
        value = self.parameterAsString(parameters, self.FIELD_VALUE, context)
        extent = self.parameterAsExtent(
            parameters, self.FIELD_QUERY_EXTENT, context)
        crs = self.parameterAsExtentCrs(
            parameters, self.FIELD_QUERY_EXTENT, context)
        nominatim = self.parameterAsString(
            parameters, self.FIELD_NOMINATIM, context)
        timeout = self.parameterAsInt(parameters, self.FIELD_TIMEOUT, context)
        output_file = self.parameterAsFileOutput(
            parameters, self.OUTPUT_FILE, context)
        index = self.parameterAsEnums(
            parameters, self.SKIP_LAYERS, context)
        skip_layers = [
            f.value for i, f in enumerate(ALL_LAYER_TYPES) if i in index]

        if extent.isEmpty():
            is_extent = False
        else:
            is_extent = True
            crs_4326 = QgsCoordinateReferenceSystem(4326)
            transform = QgsCoordinateTransform(
                crs, crs_4326, QgsProject.instance())
            extent = transform.transform(extent)

        # Missing OSMObjects
        query_factory = QueryFactory(
            key=key,
            value=value,
            nominatim_place=nominatim,
            is_extent_template=is_extent,
            timeout=timeout)
        raw_query = query_factory.make()

        query_preparation = QueryPreparation(
            raw_query,
            extent=extent if is_extent else None,
            nominatim_place=nominatim if nominatim else None,
        )
        raw_query = query_preparation.prepare_query()
        query = query_preparation.prepare_url()

        feedback.pushInfo(tr('Query generated'))
        feedback.pushInfo(raw_query)

        loop = QEventLoop()

        download = QgsFileDownloader(QUrl(query), output_file, delayStart=True)
        feedback.canceled.connect(download.cancelDownload)
        download.downloadCompleted.connect(self.is_finished)
        download.downloadExited.connect(loop.quit)
        download.downloadError.connect(self.report_errors)
        download.downloadProgress.connect(self.progress)
        feedback.pushInfo(tr('Starting the download'))
        download.startDownload()

        loop.exec_()

        result = {
            self.OUTPUT_FILE: output_file,
        }
        for layer_type in ALL_LAYER_TYPES:
            layer = QgsVectorLayer(
                output_file + '|layername=' + layer_type.value)

            (sink, dest_id) = self.parameterAsSink(
                parameters,
                layer_type.value,
                context,
                layer.fields(),
                layer.wkbType(),
                layer.crs())
            result[layer_type.value] = dest_id

            if layer_type.value in skip_layers:
                break

            self.feedback.pushInfo(
                tr('Copying layer: {vector_layer}').format(
                    vector_layer=layer_type.value))

            request = QgsFeatureRequest()
            for f in layer.getFeatures(request):
                sink.addFeature(f, QgsFeatureSink.FastInsert)

        self.feedback.pushInfo(tr('Copy is finished'))
        return result

    def is_finished(self):
        self.feedback.pushInfo(tr('Download finished'))

    def report_errors(self, errors):
        self.feedback.pushInfo(tr('Errors while downloading:'))
        raise QgsProcessingException(';'.join(errors))

    def progress(self, bytes_received, bytes_total):
        if bytes_total > 0:
            self.feedback.pushInfo(tr('Downloading progress'))

            self.feedback.pushInfo(
                tr('%s of %s') % (
                    QgsFileUtils.representFileSize(bytes_received),
                    QgsFileUtils.representFileSize(bytes_total)))
            # self.feedback.setProgress(bytes_received / bytes_total * 100)
