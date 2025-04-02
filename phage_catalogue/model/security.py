from lbrc_flask.security.model import User as BaseUser

from phage_catalogue.security import ROLENAME_EDITOR, ROLENAME_UPLOADER

class User(BaseUser):
    @property
    def is_editor(self):
        return self.has_role(ROLENAME_EDITOR)

    @property
    def is_uploader(self):
        return self.has_role(ROLENAME_UPLOADER)
