import alembic.config
from lbrc_flask.security import init_roles, init_users

from phage_catalogue import create_app
alembicArgs = [
    '--raiseerr',
    'upgrade', 'head',
]
alembic.config.main(argv=alembicArgs)

application = create_app()
application.app_context().push()

init_roles()
init_users()
