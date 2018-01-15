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

from qgis.PyQt.QtCore import QCoreApplication


def tr(text, context='@default'):
    """We define a tr function alias here since the utilities implementation
    below is not a class and does not inherit from QObject.

    .. note:: see http://tinyurl.com/pyqt-differences

    :param text: String to be translated
    :type text: str, unicode

    :param context: A context for the translation. Since a same can be
        translated to different text depends on the context.
    :type context: str

    :returns: Translated version of the given string if available, otherwise
        the original string.
    :rtype: str, unicode
    """
    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    translated_text = QCoreApplication.translate(context, text)
    return translated_text
