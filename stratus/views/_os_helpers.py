import os
import codecs

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

def handle_uploaded_file( path, f):
    try:
        destination = open(path, 'wb+')
        for chunk in f.chunks():
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
    
    import ipdb; ipdb.set_trace()
    f.close()
    return True