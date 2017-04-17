import logging
from collections import namedtuple

import gapiclient
from kumodocs import basedriver


class DocsDriver(basedriver.BaseDriver):
    """ 
    Functionality to retrieve and flattens Google Docs logs, and recover plain-text, suggestions, comments, 
    and images from the log.
    """

    suggestion_content = namedtuple('content', 'added, deleted')

    def __init__(self):
        self.docs_client = gapiclient.Client(service='drive', scope='https://www.googleapis.com/auth/drive')
        self.logger = logging.getLogger(__name__)

    @property
    def logger(self):
        return self.logger

    @logger.setter
    def logger(self, value):
        self.logger = value

    def choose_file(self):
        choice = self.docs_client.choose_file()
        return choice

    def get_log(self, file_id, start, end):
        pass

    def flatten_log(self, log):
        pass

    def recover_objects(self, flat_log):
        pass


if __name__ == '__main__':
    print('hi')
