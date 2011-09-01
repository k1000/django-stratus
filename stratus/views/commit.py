from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from _view_helpers import mix_response, message_convert
from _git_helpers import get_repo, get_commits, get_commit, get_diff

from stratus.settings import REPO_BRANCH, REPO_RESTRICT_VIEW, REPO_ITEMS_IN_PAGE, STRATUS_MEDIA_URL, GIT_RESET

def log(request, repo_name, branch=REPO_BRANCH, path=None):
    page = int(request.GET.get("page", 0))
    repo = get_repo( repo_name )
    if path:
        paths = [path]
        template = 'stratus/file_history.html'
    else:
        paths = []
        template = 'stratus/commitlog.html'
    
    commits = get_commits(repo, branch, paths, page)
    context = dict(
        REPO_ITEMS_IN_PAGE = REPO_ITEMS_IN_PAGE,
        STRATUS_MEDIA_URL = STRATUS_MEDIA_URL,
        repo_name = repo_name,
        branch_name = branch,
        commits = commits,
        next_page = page + 1,
        path = path,
        url= reverse('stratus-log', args=[repo_name, branch ])
    )
    if page > 0:
        context["previous_page"] = page-1

    return mix_response( 
        request, 
        template, 
        context)

if REPO_RESTRICT_VIEW:
    log = login_required(log)


def view(request, repo_name, branch, commit_sha=None):
    """
    view diffs of affeted files in the commit
    """
    commit = diff = None
    repo = get_repo( repo_name )
    commit_list = get_commit( repo, commit_sha)
    if commit_list:
        commit = commit_list[0]
        if len(commit_list) > 1:
            diff = get_diff( repo, commit_list[1].hexsha, commit.hexsha, )

    context = dict(
        STRATUS_MEDIA_URL = STRATUS_MEDIA_URL,
        repo_name = repo_name,
        branch_name = branch,
        diff = diff,
        commit = commit,
    )

    return mix_response( 
        request, 
        'stratus/commit.html', 
        context)

@login_required
def undo(request, repo_name, branch_name):
    """
    undo last commit
    """
    msgs = []
    json_convert = None

    repo = get_repo( repo_name )
    git = repo.git
    reset_result = git.reset( *GIT_RESET )
    msgs.append( reset_result )

    if request.is_ajax():
        json_convert = message_convert

    context = dict(
        STRATUS_MEDIA_URL = STRATUS_MEDIA_URL,
        repo_name = repo_name,
        branch_name = branch_name,
        msg=msgs, 
    )
    return mix_response( 
        request, 
        'stratus/undo.html', 
        context,
        json_convert,
        )

@login_required
def diff(request, repo_name, branch, path):
    """
    view file diffs betwin given commits
    """
    pass