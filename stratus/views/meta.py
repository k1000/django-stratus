import codecs
from django.http import HttpResponse
from django.utils.html import escape

from stratus.settings import REPOS, REPO_BRANCH, STRATUS_MEDIA_URL
from stratus.forms import SearchForm

from _view_helpers import mix_response
from _git_helpers import get_repo

def repos(request):
    context = {
        "STRATUS_MEDIA_URL": STRATUS_MEDIA_URL,
        "repos":dict([ (repo_name, get_repo( repo_name )) for repo_name in REPOS]),
    }
    
    return mix_response( 
        request, 
        'stratus/list_repos.html', 
        context)

def branches(request, repo_name):
    pass
          
def search(request, repo_name, branch):
    """
    serch files for string
    """
    found_files = []
    query = ""
    repo = get_repo( repo_name )
    if request.method == 'GET':
        form = SearchForm( request.GET )
        query = request.GET.get("query", "")
        if query:
            git = repo.git
            #http://book.git-scm.com/4_finding_with_git_grep.html
            try:
                result = git.grep( "--name-only", query )
            except git.GitCommandError:
                pass
            else:
                found_files = result.split("\n")
    else:
        form = SearchForm( request.GET )
    
    context = dict(
        STRATUS_MEDIA_URL = STRATUS_MEDIA_URL,
        form = form,
        query = query,
        found_files = found_files,
        repo = repo,
        repo_name = repo_name,
        branch_name = branch,
    ) 

    return mix_response( 
        request, 
        'stratus/found_files.html', 
        context)

def replace(request, repo_name, branch):
    """
    serch files for string
    """
    found_files = []
    query = ""
    repo = get_repo( repo_name )
    if request.method == 'POST':
        form = SearchForm( request.POST )
        query = request.POST.get("query", "")
        replace = request.POST.get("replace", "")
        if query and replace:
            git = repo.git
            #http://book.git-scm.com/4_finding_with_git_grep.html
            try:
                result = git.grep( "--name-only", query )
            except GitCommandError:
                pass
            else:
                found_files = result.split("\n")
                for file_path in found_files:
                    f = codecs.open(file_path, encoding='utf-8', mode=mode)
                    content = f.read
                    f.write(content.replace(query, replace))
                    f.close
    else:
        form = SearchForm( request.POST )
    
    context = dict(
        STRATUS_MEDIA_URL = STRATUS_MEDIA_URL,
        form = form,
        query = query,
        found_files = found_files,
        repo = repo,
        repo_name = repo_name,
        branch_name = branch,
    ) 

    return mix_response( 
        request, 
        'stratus/found_files.html', 
        context)

def consol(request, repo_name):
    """
    serch files for string
    """
    result = query = ""
    repo = get_repo( repo_name )

    if request.method == 'POST':
        query = request.POST.get("com", "")
        if query:
            git = repo.git
            #http://book.git-scm.com/4_finding_with_git_grep.html
            com_str = query.split(" ")
            if com_str[0] != "git":
                result = "first command must be git"
            else:
                try:
                    command = getattr(git, com_str[1])
                    result = escape( command( com_str[2:] ) )
                except git.GitCommandError, e:
                    result = "GIT Command error %s" % e
                
    return HttpResponse(result, mimetype='application/javascript')