
import sys
import os

if not __package__:
    path = os.path.join(os.path.dirname(__file__), os.pardir)
    sys.path.insert(0, path)

os.environ['moblife_config'] = 'moblife.app_config.LocalDevConfig'

import moblife

moblife.main()