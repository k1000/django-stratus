from git import *
from django.http import Http404
from stratus.views._view_helpers import error_view
from stratus.settings import REPOS, REPO_ITEMS_IN_PAGE, GIT_COMMIT, GIT_AMMEND
from stratus import signals

MSG_COMMIT_ERROR = "There were problems with making commit"
MSG_COMMIT_SUCCESS = u"Commit has been executed. %s"

def mk_commit(repo, message, path, ammend=True ):
    result_msg = ""
    git = repo.git
    cmd = GIT_COMMIT
    try:
        git.add(path)
        if ammend:
            cmd = GIT_AMMEND
        result_msg = git.commit(cmd + [u"""%s""" % message])
        ChatConnection.send_msg(dict(
            msg = result_msg
            ,room = "local"
            ,nick = "kam"
        ))
        signals.commit.send(sender=repo, message=result_msg)
        #commit_result = index.commit("""%s""" % message)
    except GitCommandError, e:
        #import ipdb; ipdb.set_trace()
        if e.stderr:
            result_msg = e.stderr
        else:
            result_msg = MSG_COMMIT_ERROR

    return result_msg

def get_commit( repo, commit_sha ):
    return list(repo.iter_commits( rev = commit_sha ))

def get_repo( repo_name ):
    return Repo(REPOS[repo_name])
    #try:
        
    #except InvalidGitRepositoryError:
    #    raise Http404 
    #except NoSuchPathError:
    #    raise Http404 #!!! FIXIT

def get_commit_tree( repo, commit_sha=None ):
    commit = None
    if commit_sha:
        commit = list(repo.iter_commits( rev=commit_sha ))[0]
        tree = commit.tree
    else:
        tree = repo.tree()
    return commit, tree

def get_diff(repo, path=None, commit_a=None, commit_b=None):
    git = repo.git
    args = []
    if commit_a: args+=[commit_a]
    if commit_b: args+=[commit_b]
    if path: args +=[ "--", path ]
    return git.diff( *args )

def get_commits(repo, branch, paths=[], page=0):
    return list(repo.iter_commits(branch, paths, max_count=REPO_ITEMS_IN_PAGE, skip=page * REPO_ITEMS_IN_PAGE ) )