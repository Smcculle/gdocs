import logging
from collections import namedtuple

import basedriver
import gapiclient


class GSuiteDriver(basedriver.BaseDriver):
    """ 
    Functionality to retrieve and flattens Google Docs logs, and recover plain-text, suggestions, comments, 
    and images from the log.
    """

    suggestion_content = namedtuple('content', 'added, deleted')

    def __init__(self, base_dir='../downloaded'):
        self.client = gapiclient.Client(service='drive', scope='https://www.googleapis.com/auth/drive')
        self._logger = logging.getLogger(__name__)
        self._base_dir = base_dir
        self.choice = None

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, value):
        self._logger = value

    @property
    def base_dir(self):
        return self._base_dir

    @base_dir.setter
    def base_dir(self, value):
        self._base_dir = value

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
        elif self.choice.drive == 'presentation':
            self.logger.debug('Non document drive - setting revision to 1, max_revs')
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

    def get_log(self, start, end, **kwargs):
        """
        Gets log from the google api client using self.choice data along with starting and ending revision 
        :param start: Starting revision
        :param end: Ending revision
        :param kwargs: Unused here.  
        :return: Native revision log
        """

        log_url = self.client.create_log_url(start=start, end=end, choice=self.choice)
        response, log = self.client.request(url=log_url)
        return log

    def flatten_log(self, log):
        print("flattening log")
        pass

    def recover_objects(self, flat_log):
        print("recovering objects")
        pass


if __name__ == '__main__':
    print('hi')
