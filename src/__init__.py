# -*- coding: utf-8 -*-

PLUGIN_NAME = u'discogs-genre'
PLUGIN_AUTHOR = u'Hervé Martinet'
PLUGIN_DESCRIPTION = u'Use discogs genre and/or style as genre.'
PLUGIN_VERSION = "0.1"
PLUGIN_API_VERSIONS = ["0.14"]

from PyQt4 import QtGui, QtCore
from picard import log
from picard.metadata import register_album_metadata_processor
import urllib2, gzip, cStringIO, libxml2

discogs_api_key = 'db1e3dc342'
discogs_release_url = 'http://www.discogs.com/release/'
discogs_request_url = '{0}?f=xml&api_key={1}'
discogs_request_headers = {'Accept-Encoding': 'gzip', 'User-Agent': 'discogs-genre/0.1 +http://wiki.musicbrainz.org/Picard_Plugins'}

logger = log.Log()

def get_release_url(release):
    try:
        for relation_list in release.relation_list:
            if relation_list.target_type == 'Url':
                for relation in relation_list.relation:
                    if relation.target.startswith(discogs_release_url):
                        return relation.target
    except AttributeError:
        log.info('Error retrieving release discogs url')
        pass

def process_album(tagger, metadata, release):
    release_url = get_release_url(release)
    request = urllib2.Request(discogs_request_url.format(release_url, discogs_api_key), None, discogs_request_headers)
    try:
        response = urllib2.urlopen(request)
        data = response.read()
        try:
            data = gzip.GzipFile(fileobj = cStringIO.StringIO(data)).read()
        except IOError:
            pass
    except urllib2.HTTPError, e:
        logger.info(e.read())

    genres = []
    doc = libxml2.parseMemory(data, len(data))
    for url in doc.xpathEval('/resp/release/genres/genre'):
        genres.append(url.content)
    for url in doc.xpathEval('/resp/release/styles/style'):
        genres.append(url.content)
    metadata['genre'] = genres

register_album_metadata_processor(process_album)

