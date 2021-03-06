
from django.conf import settings

REPOS = getattr(settings, "REPOS", {
	"local": settings.PROJECT_PATH,
})

REPO_BRANCH = getattr(settings, "REPO_BRANCH", "master")
REPO_RESTRICT_VIEW = getattr(settings, "REPO_RESTRICT_VIEW", True)
REPO_ITEMS_IN_PAGE = getattr(settings, "REPO_VIEW_IN_PAGE", 10)

FILE_BLACK_LIST = getattr(settings,"FILE_BLACK_LIST", 
	("settings.py",) 
)
#STRATUS_MEDIA_URL =  "%sstratus/" %  getattr(settings,"STRATUS_MEDIA_URL", settings.STATIC_URL )
STRATUS_MEDIA_URL  = "/static/stratus/"
# limit editor height for large documets
LIMIT_EDITOR_HEIGHT = getattr(settings,"LIMIT_EDITOR_HEIGHT", "300" ) 
EDITABLE_MIME_TYPES = getattr(settings,"EDITABLE_MIME_TYPES", ["text", "application"] )
PARTIAL_PREFIX = getattr(settings,"PARTIAL_PREFIX", "_")

#GIT Commands
GIT_RESET = ["--soft", "HEAD^"]
GIT_COMMIT = ["-m",]
GIT_AMMEND = ["--amend", "-m",]
