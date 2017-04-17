import logging
from collections import namedtuple

import gapiclient
from kumodocs import basedriver


class GSuiteDriver(basedriver.BaseDriver):
    """ 
    Functionality to retrieve and flattens Google Docs logs, and recover plain-text, suggestions, comments, 
    and images from the log.
    """

    suggestion_content = namedtuple('content', 'added, deleted')

    def __init__(self):
        self.client = gapiclient.Client(service='drive', scope='https://www.googleapis.com/auth/drive')
        self.logger = logging.getLogger(__name__)
        self.choice = None

    @property
    def logger(self):
        return self.logger

    @logger.setter
    def logger(self, value):
        self.logger = value

    def choose_file(self):
        """
        Presents the user with a virtualized interface of their GSuite contents to choose a file.   
        :return: A namedtuple containing file_id, title, drive, and max_revs
        """
        choice = self.client.choose_file()
        self.choice = choice

        return choice

    def prompt_rev_range(self):
        start, end = 0, 0
        if self.choice.drive not in ['document', 'presentation']:
            print('{} is not a supported service at this time')
            self.logger.debug('Unsupported service: {}'.format(self.choice.drive))
            raise SystemExit
        elif self.choice.drive != 'presentation':
            self.logger.debug('Non document drive - setting revision to 1, max_rev')
            start, end = 1, self.choice.max_revs
            print('Partial revisions for {} are not supported. Setting start=1 and end=max'.format(self.choice.drive))
        else:
            print('Please choose revision range\n')
            while start < 1 or start >= self.choice.max_revs:
                try:
                    start = int(raw_input("Start from revision(max {}): ".format(self.choice.max_revs)))
                    if start < 1 or start >= self.choice.max_revs:
                        raise ValueError
                except ValueError:
                    print("invalid start revision choice\n")

            while end == 0 or end > self.choice.max_revs:
                try:
                    end = int(raw_input("End at revision(max {}): ".format(self.choice.max_revs)))
                    if end == 0 or end > self.choice.max_revs:
                        raise ValueError
                except ValueError:
                    print("invalid end revision choice\n")

        return start, end

    def get_log(self, file_id, start, end, **kwargs):
        try:
            drive = kwargs['drive']
        except KeyError:
            self.logger.exception('No drive type found')
            raise
        pass

    def flatten_log(self, log):
        pass

    def recover_objects(self, flat_log):
        pass


if __name__ == '__main__':
    print('hi')
