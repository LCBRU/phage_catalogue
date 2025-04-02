from lbrc_flask.security import init_roles, init_users

ROLENAME_EDITOR='editor'
ROLENAME_UPLOADER='uploader'

def init_authorization():
    init_roles([ROLENAME_EDITOR, ROLENAME_UPLOADER])
    init_users()
