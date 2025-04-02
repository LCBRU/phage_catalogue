import alembic.config

from phage_catalogue import create_app
from phage_catalogue.security import init_authorization
alembicArgs = [
    '--raiseerr',
    'upgrade', 'head',
]
alembic.config.main(argv=alembicArgs)

application = create_app()
application.app_context().push()

init_authorization()
