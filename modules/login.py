from util.utils import Region, Utils
from util.logger import Logger
from util.config import Config
from util.utils import Utils, GoTo
import time

class LoginModule(object):

    def __init__(self, config):
        """Initializes the Login module.

        Args:
            config (Config): BAAuto Config instance
        """
        self.enabled = True
        self.config = config

    def login_logic_wrapper(self):
        GoTo.home()



