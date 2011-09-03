import git
import stratus
from django.utils import simplejson
from django.core.context_processors import csrf
#import json
from django.template import RequestContext, TemplateDoesNotExist
#from django.template.response import TemplateResponse
from django.shortcuts import render
from django.template.loader import render_to_string, get_template
from django.http import  HttpResponse

from stratus.settings import PARTIAL_PREFIX

def git_to_dict( blob ):
    properties = ("abspath", "name", "mode",  "hexsha", "path", "size", "type",  ) #"mime_type",
    return dict([ ( prop, getattr( blob, prop ) )  for prop in properties])

# json helper
def to_json(python_object):
    if isinstance(python_object, (git.Blob, git.Tree) ):
        return git_to_dict( python_object )

    if isinstance(python_object, stratus.forms.FileUploadForm ):
        return python_object.as_p()
    return None
    #raise TypeError(repr(python_object) + ' is not JSON serializable')

def message_convert( request, template_name, context ):
    context_out ={}
    white_list =  ["msg", "success", "path", "reload_fbrowser"]
    for key in context.keys():
        if key in white_list:
            context_out[key] = context[key]

    return context_out

def partial_json_convert( request, template_name, context ):
    partial_prefix = "_"
    
    tmpl_dir = template_name.split("/")
    partial_template_path = "/".join( [ tmpl_dir[:-1][0], "%s%s" % (partial_prefix, tmpl_dir[-1:][0]) ] )

    context.update( csrf(request) )
    try:
        partial = render_to_string( partial_template_path, context )
    except TemplateDoesNotExist:
        return TemplateResponse( 
            request,
            template_name,
            context)
    
    context_out = dict(
        html = partial,
        path = context.get("path", ""),
    )
    return context_out

    
def mix_response(request, template_name, context, json_convert=None):
    if request.is_ajax():
        if json_convert:
            response_dict = json_convert( request, template_name, context )
        else:
            response_dict = partial_json_convert(request, template_name, context )

        return HttpResponse(simplejson.dumps(response_dict, default=to_json), mimetype='application/javascript')
    
    return render(
        request, 
        template_name,
        context,
        content_type="application/xhtml+xml")



def error_view(request, msg, code=None):
    return mix_response( 
            request, 
            'stratus/error.html', 
            { "msg":msg, })
            
def make_crumbs( path ):
    breadcrumbs = []
    bread = path.split("/")
    for crumb in range(0, len(bread)):
        breadcrumbs.append( (bread[crumb], "/".join(bread[:crumb+1]) ))
        
    #breadcrumbs.append( (bread[-1], "#") )
    return breadcrumbs