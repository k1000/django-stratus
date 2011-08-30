import os

from django.http import  HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt

from _view_helpers import mix_response, make_crumbs, error_view, message_convert
from _git_helpers import get_repo, get_commit_tree, get_diff, mk_commit
from _os_helpers import file_type_from_mime, write_file, handle_uploaded_file

from stratus.settings import REPOS, REPO_BRANCH, REPO_ITEMS_IN_PAGE, REPO_RESTRICT_VIEW
from stratus.settings import FILE_BLACK_LIST, STRATUS_MEDIA_URL, EDITABLE_MIME_TYPES

from stratus.forms import TextFileEditForm, FileEditForm, FileDeleteForm, FileUploadForm, RenameForm, SearchForm

MSG_COMMIT_ERROR = "There were problems with making commit"
MSG_COMMIT_SUCCESS = u"Commit has been executed. %s"
MSG_NO_FILE = "File hasn't been found."
MSG_NO_FILE_IN_TREE = "File haven't been found under current tree."
MSG_CANT_VIEW = "Can't view file."
MSG_NOT_ALLOWED = "You are not allowed to view/edit this file."
MSG_RENAME_ERROR = u"There been an error during renaming the file %s to %s."
MSG_RENAME_SUCCESS = u"File %s has been renamed to %s"
MSG_DELETE = u"File '%s' has been deleted"
MSG_CANT_SAVE_FILE = "Error. File hasn't been saved"
MSG_UPLOAD_SUCCESS = u"File '%s' has been uploaded"
MSG_COMMIT_SUCCESS = u"File '%s' has been commited"

@login_required
def new(request, repo_name, branch=REPO_BRANCH, path=None ):
    result_msg = file_source = ""
    form_class = TextFileEditForm

    file_path = path #!!! FIX security
    #TODO check if file exist allready
    file_meta = dict(
        type = "python",
    )

    if request.method == 'POST':
        form = FileUploadForm( request.POST, request.FILES )
        if form.is_valid():
            repo = get_repo( repo_name )

            file_source = form.cleaned_data["file_source"]
            write_file(file_path, file_source )

            msg = form.cleaned_data["message"]
            result_msg = mk_commit(repo, msg, file_path )
            messages.success(request, result_msg ) 

            dir_path = "/".join( path.split("/")[:-1] )
            return redirect('stratus-tree-view', repo_name, branch, dir_path  )
        else:
            result_msg = MSG_COMMIT_ERROR
    else:
        form = form_class( initial={"message":"%s added" % path} )
    
    context = dict(
        STRATUS_MEDIA_URL = STRATUS_MEDIA_URL,
        form= form,
        breadcrumbs = make_crumbs(path),
        result_msg = result_msg,
        file_meta = file_meta,
        repo_name = repo_name,
        branch_name = branch,
        path = path,
    )
    return mix_response( 
        request, 
        'stratus/new_file.html', 
        context)



@csrf_exempt  #TODO 
@login_required
def upload(request, repo_name, branch=REPO_BRANCH ):
    file_source = path = ""
    msgs = []
    json_convert = None

    if request.method == 'POST':
        from _os_helpers import ProgressBarUploadHandler
        request.upload_handlers.insert(0, ProgressBarUploadHandler())

        repo = get_repo( repo_name )
        dir_path = request.GET.get("upload_dir") #!!! FIX security
        file_name = request.GET.get("qqfile")
        file_path = os.path.join(dir_path, unicode(filename, 'utf-8').encode('utf-8') )
        file_abs_path = os.path.join( repo.working_dir, file_path)

        print file_abs_path
        if request.META['CONTENT_TYPE'] == 'application/octet-stream':
            try:
                destination = open(file_abs_path, 'wb+')
                for chunk in request.raw_post_data:
                    destination.write(chunk)
                destination.close()
            except:
                file_writen = False
            finally:
                file_writen = True
        else:
            file_writen = handle_uploaded_file(file_abs_path, request.FILES['file_source'])

        if file_writen:
             
            msgs.append( MSG_UPLOAD_SUCCESS % file_path)
            message = MSG_COMMIT_SUCCESS % file_path
            msg = mk_commit(repo, message, file_name )
            msgs.append( msg )
            return HttpResponse('{ "success": true }', mimetype='application/javascript')
        else:
            msgs.append( MSG_CANT_SAVE_FILE )
            return HttpResponse('{ "success": false }', mimetype='application/javascript')
        
        if request.is_ajax():
            json_convert = message_convert
    else:
        form = FileUploadForm( initial={"message":"%s added" % path} )
    
    context = dict(
        STRATUS_MEDIA_URL = STRATUS_MEDIA_URL,
        form= form,
        breadcrumbs = make_crumbs(path),
        msg = msgs,
        repo_name = repo_name,
        branch_name = branch,
        path = path,
    )
    return mix_response( 
        request, 
        'stratus/upload_file.html', 
        context,
        json_convert,)


@login_required
def edit(request, repo_name, branch=REPO_BRANCH, path=None ):

    file_source = ""
    msgs = []
    json_convert = None

    if path in FILE_BLACK_LIST:
        msg = MSG_NOT_ALLOWED
        return error_view( request, result_msg)
    
    if path[-1:] == "/":
        path = path[:-1]
    file_path = path #!!! FIX security

    repo = get_repo( repo_name )
    tree = repo.tree()
    
    # edit only if exist in tree
    try:
        tree = tree[path]
    except KeyError:
        msg.append( MSG_NO_FILE_IN_TREE )
        return error_view( request, msg)
    
    # edit only if it is file
    if not tree.type  is "blob":
        msgs.append( MSG_CANT_VIEW )
        return error_view( request, msg)
    
    mime = tree.mime_type.split("/")
    file_meta = dict(
        STRATUS_MEDIA_URL = STRATUS_MEDIA_URL,
        abspath = tree.abspath,
        mime = tree.mime_type,
        size = tree.size,
        tree = tree,
        mime_type = mime[0],
        type = file_type_from_mime(tree.mime_type),
    )

    if file_meta["mime_type"] in EDITABLE_MIME_TYPES:
        form_class = TextFileEditForm
    else:
        form_class = FileEditForm
    
    if request.method == 'POST':
        form = form_class( request.POST, request.FILES )
        if form.is_valid():
            file_abs_path = os.path.join( repo.working_dir, file_path)
            if file_meta["mime_type"] == "text" or mime[1] in ["xml",]:
                file_source = form.cleaned_data["file_source"]
                file_writen = write_file(file_abs_path, file_source )
            else:
                file_writen = handle_uploaded_file(file_abs_path, request.FILES['file_source'])
            
            if file_writen:
                msgs.append( "File has been saved" )
                message = form.cleaned_data["message"]
                msg = mk_commit(repo, message, file_path )
                msgs.append( msg )
            else:
                msgs.append( MSG_CANT_SAVE_FILE )
        else:
            msgs.append( form.errors )

        if request.is_ajax():
            json_convert = message_convert
    else:
        if file_meta["mime_type"] in EDITABLE_MIME_TYPES:
            file_source = tree.data_stream[3].read
        else:
            file_source = file_meta["abspath"]

        form = form_class( initial={
            "file_source":file_source,
            "message":"modified %s" % path
        } )

    context = dict(
        STRATUS_MEDIA_URL = STRATUS_MEDIA_URL,
        form= form,
        file_source = file_source,
        breadcrumbs = make_crumbs(path),
        file_meta = file_meta,
        msg = msgs,
        repo_name = repo_name,
        branch_name = branch,
        delete_form = FileDeleteForm( initial={"message":MSG_DELETE % path }),
        path = path,
        name = path.split("/")[-1:][0],
    )
    
    if mime[0] == "image":
        import base64
        context["img_base"] = base64.b64encode( file_source )
        from getimageinfo import getImageInfo
        context["img_meta"] = getImageInfo( file_source )
    
    return mix_response( 
        request, 
        'stratus/edit.html', 
        context,
        json_convert,
        )

@login_required
def view(request, repo_name, branch, path, commit_sha=None,):
    """
    view file in the commit
    """
    file_source = diff = ""

    if path in FILE_BLACK_LIST:
        msg = MSG_NOT_ALLOWED
        return error_view( request, msg)
    
    file_path = path #!!! FIX security
    if path[-1:] == "/": path = path[:-1]
    
    repo = get_repo( repo_name )
    commit, tree = get_commit_tree( repo, commit_sha )

    if commit.parents:
        diff = get_diff( repo, path, commit.parents[0].hexsha, commit.hexsha )

    try:
        tree = tree[path]
    except KeyError:
        msg = MSG_NO_FILE_IN_TREE
        return error_view( request, msg )

    if not tree.type  is "blob":
        msg = MSG_NO_FILE_IN_TREE
        return error_view( request, msg )
    
    mime = tree.mime_type.split("/")
    
    file_source = tree.data_stream[3].read()
    
    #import ipdb; ipdb.set_trace()
    file_meta = dict(
        STRATUS_MEDIA_URL = STRATUS_MEDIA_URL,
        abspath = tree.abspath,
        mime = tree.mime_type,
        size = tree.size,
        tree = tree,
        path = tree.abspath,
        mime_type = mime[0],
        type = file_type_from_mime(tree.mime_type),
    )
    context = dict(
        STRATUS_MEDIA_URL = STRATUS_MEDIA_URL,
        file_source = file_source,
        breadcrumbs = make_crumbs(path),
        commit = commit,
        diff = diff,
        file_meta = file_meta,
        repo_name = repo_name,
        branch_name = branch,
        path = path,
        name = path.split("/")[-1:][0],
    )
    if mime[0] == "image":
        import base64
        context["img_base"] = base64.b64encode( file_source )
        from getimageinfo import getImageInfo
        context["img_meta"] = getImageInfo( file_source )

    return mix_response( 
        request, 
        'stratus/view_file.html', 
        context)

@login_required
def delete(request, repo_name, branch, path ):
    repo = get_repo( repo_name )
    tree = repo.tree()
    try:
        ftree = tree[path] #check if exixs under the tree
    except KeyError:
        pass

    if request.method == "POST":
        form = FileDeleteForm(request.POST)
        if form.is_valid():
            if os.path.isfile(path):
                os.remove(path)
            git = repo.git
            del_message = git.rm(path)

            msg = form.cleaned_data["message"]
            commit_result = git.commit("-m", """%s""" % msg)
            messages.success(request, commit_result ) 

            dir_path = "/".join( path.split("/")[:-1] )
            return redirect('stratus-tree-view', repo_name, branch, dir_path  )
    else:
        form = FileDeleteForm(initial={
            "message": "file %s deleted" % path,
            "path": path,
        })
    
    context = dict(
        STRATUS_MEDIA_URL = STRATUS_MEDIA_URL,
        breadcrumbs = make_crumbs(path),
        form = form,
        repo_name = repo_name,
        branch_name = branch,
        path = path,
    )
    return mix_response( 
        request, 
        'stratus/delete_file.html', 
        context)

@login_required
def get_file(request, repo_name, branch, path, commit_sha="" ):
    """
    get file from git tree
    """

    if path in FILE_BLACK_LIST:
        raise Http404
    
    repo = get_repo( repo_name )
    commit, tree = get_commit_tree( repo, commit_sha )

    try:
        tree = tree[path]
    except KeyError:
        raise Http404

    if not tree.type  is "blob":
        raise Http404

    return HttpResponse(tree.data_stream.read(), mimetype=tree.mime_type)

@login_required
def rename(request, repo_name, branch, file_path):

    if request.method == 'POST':
        repo = get_repo( repo_name )
        tree = repo.tree()
        try:
            tree = tree[file_path]
        except KeyError:
            msg = MSG_NO_FILE_IN_TREE
            return error_view( request, msg)

        form = RenameForm( request.POST )
        
        if form.is_valid():

            git = repo.git
            new_name = form.cleaned_data["new_name"]
            try:
                os.rename(file_path, new_name)
            except IOError:
                msg = MSG_RENAME_ERROR % (file_path, new_name)
                return error_view( request, msg)
            else:
                
                git.mv( path, new_name )
                msg = MSG_RENAME_SUCCESS % (path, new_name)
                commit_result = git.commit("-m", """%s""" % msg)
                messages.success(request, commit_result ) 
                dir_path = "/".join( path.split("/")[:-1] )
                return redirect('stratus-tree-view', repo_name, branch, dir_path  )
        else:
            messages.error(request, MSG_RENAME_ERROR ) 
    else:
        form = RenameForm( )

    context = dict(
        STRATUS_MEDIA_URL = STRATUS_MEDIA_URL,
        breadcrumbs = make_crumbs(file_path),
        form = form,
        repo_name = repo_name,
        branch_name = branch,
        path = file_path,
    ) 
    return mix_response( 
        request, 
        'stratus/rename_file.html', 
        context)