import os
import codecs
from django.core.files.uploadhandler import MemoryFileUploadHandler
import logging


#http://fairviewcomputing.com/blog/2008/10/21/ajax-upload-progress-bars-jquery-django-nginx/
class ProgressBarUploadHandler(MemoryFileUploadHandler):
    """
    Tracks progress for file uploads.
    The http post request must contain a query parameter, 'X-Progress-ID',
    which should contain a unique string to identify the upload to be tracked.
    """

    def __init__(self, request=None):
        super(ProgressBarUploadHandler, self).__init__(request)
        self.progress_id = None
        self.cache_key = None

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        logger = logging.getLogger('uploaddemo.upload_handlers.UploadProgressCachedHandler.handle_raw_input')
        self.content_length = content_length
        if 'X-Progress-ID' in self.request.GET:
            self.progress_id = self.request.GET['X-Progress-ID']
        if self.progress_id:
            self.cache_key = "%s_%s" % (self.request.META['REMOTE_ADDR'], self.progress_id )
            cache.set(self.cache_key, {
                'state': 'uploading',
                'size': self.content_length,
                'received': 0
            })
            if settings.DEBUG:
                logger.debug('Initialized cache with %s' % cache.get(self.cache_key))
        else:
            logging.getLogger('ProgressBarUploadHandler').error("No progress ID.")

    def new_file(self, field_name, file_name, content_type, content_length, charset=None):
        pass

    def receive_data_chunk(self, raw_data, start):
        logger = logging.getLogger('uploaddemo.upload_handlers.UploadProgressCachedHandler.receive_data_chunk')
        if self.cache_key:
            data = cache.get(self.cache_key)
            if data:
                data['received'] += self.chunk_size
                cache.set(self.cache_key, data)
                if settings.DEBUG:
                    logger.debug('Updated cache with %s' % data)
        return raw_data

    def file_complete(self, file_size):
        pass

    def upload_complete(self):
        logger = logging.getLogger('uploaddemo.upload_handlers.UploadProgressCachedHandler.upload_complete')
        if settings.DEBUG:
            logger.debug('Upload complete for %s' % self.cache_key)
        if self.cache_key:
            cache.delete(self.cache_key)


def file_type_from_mime(mime):
    types = {
        "text/x-python" : "python",
        "text/css" : "css",
        "text/html" : "xml",
        "aplication/javascript" : "javascript",
        "aplication/json" : "javascript",
    }
    if mime in types:
        return types[mime]
    else:
        return mime

def file_type_from_ext(ext):
    types = {
        ".py" : "python",
        ".css" : "css",
        ".html" : "xml",
        ".js" : "javascript",
    }
    if ext in types:
        return types[ext]
    else:
        return ext

def handle_uploaded_file( path, source):
    try:
        destination = open(path, 'wb+')
        for chunk in source.chunks():
            destination.write(chunk)
        destination.close()
        return True
    except:
        return False

def write_file( file_path, file_source, mode="w"):
    try:
        f = codecs.open(file_path, encoding='utf-8', mode=mode)
    except IOError:
        return False
    
    try:
        f.write(file_source)
    except IOError:
        return False
    
    f.close()
    return True