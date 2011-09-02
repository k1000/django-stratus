from django.conf.urls.defaults import *

# place app url patterns here
urlpatterns = patterns('stratus.views.file',
	url(r'^(?P<repo_name>[a-z0-9\-_]+)/(?P<branch>[a-z0-9\-_]+)/edit/(?P<path>[\w\(\)&\'\-\.\/ ]+)$',
		"edit", name='stratus-edit-file'),

	url(r'^(?P<repo_name>[a-z0-9\-_]+)/(?P<branch>[a-z0-9\-_]+)/new/(?P<path>[a-zA-Z0-9\-_\.\/]*)$', 
		"new", name='stratus-new-file'),

    url(r'^(?P<repo_name>[a-z0-9\-_]+)/(?P<branch>[a-z0-9\-_]+)/new-folder/(?P<path>[a-zA-Z0-9\-_\.\/]*)$', 
        "new_folder", name='stratus-new-folder'),

    url(r'^(?P<repo_name>[a-z0-9\-_]+)/(?P<branch>[a-z0-9\-_]+)/upload/$', 
        "upload", name='stratus-upload-file'),

    url(r'^(?P<repo_name>[a-z0-9\-_]+)/(?P<branch>[a-z0-9\-_]+)/delete/(?P<path>[a-zA-Z0-9\-_\.\/]+)$', 
        "delete", name='stratus-delete-file'),

    url(r'^(?P<repo_name>[a-z0-9\-_]+)/(?P<branch>[a-z0-9\-_]+)/rename/(?P<file_path>[a-zA-Z0-9\-_\.\/\\]+)$', 
        "rename", name='stratus-rename-file'),

    url(r'^(?P<repo_name>[a-z0-9\-_]+)/(?P<branch>[a-z0-9\-_]+)/get/(?P<path>[a-zA-Z0-9\-_\.\/]*)$', 
        "get_file", name='stratus-get-file'),

    url(r'^(?P<repo_name>[a-z0-9\-_]+)/(?P<branch>[a-z0-9\-_]+)/(?P<commit_sha>[a-z0-9\-_]+)/view/(?P<path>[a-zA-Z0-9\-_\.\/]*)$', 
        "view", name='stratus-view-file'),
)

urlpatterns += patterns('stratus.views.tree',
    url(r'^(?P<repo_name>[a-z0-9\-_]+)/(?P<branch>[a-z0-9\-_]+)/tree/(?P<path>[a-zA-Z0-9\-_\.\/]*)$', 
    	"view", name='stratus-tree-view'),

    url(r'^(?P<repo_name>[a-z0-9\-_]+)/(?P<branch>[a-z0-9\-_]+)/(?P<commit_sha>[a-zA-Z0-9\-_\.\/]*)/tree/(?P<path>[a-zA-Z0-9\-_\.\/]*)$', 
        "view", name='stratus-commit-tree-view'),
)

urlpatterns += patterns('stratus.views.meta', 
    url(r'^(?P<repo_name>[a-z0-9\-_]+)/consol/$', 
        "consol", name='stratus-consol'),
)

urlpatterns += patterns('stratus.views.commit',
    url(r'^(?P<repo_name>[a-z0-9\-_]+)/(?P<branch>[a-z0-9\-_]+)/view/(?P<commit_sha>[a-zA-Z0-9\-_\.\/]*)$', 
        "view", name='stratus-commit-view'),

    url(r'^(?P<repo_name>[a-z0-9\-_]+)/(?P<branch>[a-z0-9\-_]+)/history/(?P<path>[a-zA-Z0-9\-_\.\/]*)$', 
        "log", name='stratus-history-file'),

    url(r'^(?P<repo_name>[a-z0-9\-_]+)/(?P<branch>[a-z0-9\-_]+)/diff/(?P<path>[a-zA-Z0-9\-_\.\/]*)$', 
        "diff", name='stratus-diff-file'),

    url(r'^(?P<repo_name>[a-z0-9\-_]+)/(?P<branch>[a-z0-9\-_]+)/$', 
    	"log", name='stratus-log'),

    url(r'^(?P<repo_name>[a-z0-9\-_]+)/(?P<branch_name>[a-z0-9\-_]+)/undo/$', 
        "undo", name='stratus-undo'),
)

urlpatterns += patterns('stratus.views.meta',   
    url(r'^(?P<repo_name>[a-z0-9\-_]+)/(?P<branch>[a-z0-9\-_]+)/search/$', 
        "search", name='stratus-search'),

    url(r'^(?P<repo_name>[a-z0-9\-_]+)/(?P<branch>[a-z0-9\-_]+)/replace/$', 
        "replace", name='stratus-replace'),

    url(r'^(?P<repo_name>[a-z0-9\-_]+)/$', 
        "branches", name='stratus-branches'),

    url(r'^$', 
    	"repos", name='stratus-repos'),
)