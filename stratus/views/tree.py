
from django.contrib.auth.decorators import login_required

from _view_helpers import mix_response, make_crumbs, message_convert
from _git_helpers import get_repo, get_commit_tree

from stratus.settings import  REPO_BRANCH, STRATUS_MEDIA_URL

@login_required
def view(request, repo_name, branch=REPO_BRANCH, path=None, commit_sha=None ):
    json_convert = None
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

        if request.is_ajax():
            json_convert = message_convert

    context = dict(
        STRATUS_MEDIA_URL = STRATUS_MEDIA_URL,
        repo_name = repo_name,
        branch_name = branch,
        commit = commit,
        tree = the_tree.list_traverse(depth = 1),
        breadcrumbs = make_crumbs(path),
        dir_path = dir_path,
        path = path,
    )

    return mix_response( 
        request, 
        template_name, 
        context,
        )