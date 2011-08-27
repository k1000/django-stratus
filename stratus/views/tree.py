
from django.contrib.auth.decorators import login_required

from _view_helpers import mix_response, make_crumbs
from _git_helpers import get_repo, get_commit_tree

from stratus.forms import FileUploadForm
from stratus.settings import  REPO_BRANCH, STRATUS_MEDIA_URL

@login_required
def view(request, repo_name, branch=REPO_BRANCH, path=None, commit_sha=None ):
    
    repo = get_repo( repo_name )
    commit, tree = get_commit_tree(repo, commit_sha)
    the_tree = tree
    dir_path = path.split("/")

    if commit_sha:
        template_name = 'stratus/view_commit_tree.html'
    else:
        template_name = 'stratus/view_tree.html'

    if path:
        the_tree = tree[path]

        # if its file try to get file directory 
        if the_tree.type != "tree":
            path = "/".join(dir_path[:-1])
            if len(dir_path) == 1:
                the_tree = tree
            else:
                the_tree = tree[path]
            path = "%s/" % path
    
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_path = os.path.join( repo.working_dir, path, request.FILES["file_source"].name)
            handle_uploaded_file(file_path, request.FILES['file_source'])

            msg = "file %s uploaded" % file_path
            result_msg = mk_commit(repo, msg, file_path )
            messages.success(request, result_msg )
    else:
        form = FileUploadForm( initial={ "dir_path": path } )

    context = dict(
        STRATUS_MEDIA_URL = STRATUS_MEDIA_URL,
        repo_name = repo_name,
        branch_name = branch,
        commit = commit,
        upload_form = form,
        tree = the_tree.list_traverse(depth = 1),
        breadcrumbs = make_crumbs(path),
        dir_path = dir_path,
    )

    return mix_response( 
        request, 
        template_name, 
        context)