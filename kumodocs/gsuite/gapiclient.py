"""Common methods for initializing GSuite API client and listing GSuite files. """

import ConfigParser
import argparse
import logging
import os
import sys
from collections import namedtuple, defaultdict

# noinspection PyPackageRequirements
import googleapiclient.discovery
# noinspection PyPackageRequirements
import googleapiclient.errors
import httplib2
import oauth2client.client as oa_client
import oauth2client.file as oa_file
import oauth2client.tools as oa_tools

import KIOutils
import gsuite

FileChoice = namedtuple('FileChoice', 'id, title, drive, max_rev')
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Client(object):
    """ Wraps a googleapiclient service object with functionality needed by multiple GSuite modules """

    def __init__(self, service="drive", scope='https://www.googleapis.com/auth/drive'):
        self.client = self.start(service, scope)

    @staticmethod
    def start(service_name, scope='https://www.googleapis.com/auth/drive'):
        """
        Reads config file and initializes the GSuite API client with proper authentication
        :param service_name: Name of service to start, one of gsuite.SERVICES
        :param scope: API scope to authorize.  Defaults to read/manage files in Google Drive.  
        :return: Google API client for making requests. 
        """

        logger.info('Creating the client service')
        config = ConfigParser.ConfigParser()
        file_dir = os.path.dirname(__file__)
        config_fp = os.path.realpath(os.path.join(file_dir, *gsuite.REL_CONFIG_PATH))
        config.read(config_fp)
        tokens = config.get('gdrive', 'tokenfile')
        client_secrets = config.get('gdrive', 'configurationfile')

        flow = oa_client.flow_from_clientsecrets(client_secrets,
                                                 scope=scope,
                                                 message=oa_tools.message_if_missing(client_secrets))
        storage = oa_file.Storage(tokens)
        credentials = storage.get()
        # run_flow requires a wrapped oa_tools.argparse object to handle command line arguments
        flags = argparse.ArgumentParser(parents=[oa_tools.argparser]).parse_args()
        if credentials is None:  # or credentials.invalid:
            credentials = oa_tools.run_flow(flow, storage, flags)

        # noinspection PyBroadException
        try:
            http = credentials.authorize(httplib2.Http())
            client = googleapiclient.discovery.build(serviceName=service_name, version="v2", http=http)
        except Exception as e:
            logger.error('Failed to create service', exc_info=True)
            raise sys.exit(1)
        else:
            logger.info('Created and authorized the client service')
            return client

    @staticmethod
    def create_temp_files(temp_dir, files):
        """
        Creates a directory of temporary files with file_id for virtualization of drive contents
        :param temp_dir: A temp directory that will be deleted 
        :param files: A file list resource returned from the API client list method
        :return: None
        """

        for drive_type, drive_files in files.items():
            folder_path = os.path.join(temp_dir, drive_type + '/')
            os.mkdir(folder_path)
            for file_ in drive_files:
                # replace reserved characters in title to assure valid filename
                filename = KIOutils.strip_invalid_characters(file_['title'])
                filename = '{}.{}'.format(os.path.join(temp_dir, folder_path, filename), drive_type)
                with open(filename, 'w') as f:
                    f.write(file_['id'])

    def choose_file(self):
        """
        Presents user with drive contents and prompts a choice.  
        :return: FileChoice named tuple with id, title, drive, and max revisions
        """
        files = self.list_all_files()

        with KIOutils.temp_directory() as temp_dir:
            self.create_temp_files(temp_dir, files)
            options = {'title': 'Choose a G Suite file', 'initialdir': temp_dir}
            choice = KIOutils.choose_file_dialog(**options)
            try:
                file_id = choice.read()
            except AttributeError:
                logger.error('No file chosen. Exiting.', exc_info=True)
                sys.exit(2)
            except IOError:
                logger.error('Error reading file. Exiting', exc_info=True)
                sys.exit(3)
            else:
                choice.close()
                title, drive = KIOutils.split_title(choice.name)
                logger.info('Chose file {} from service {}'.format(title, drive))

        revisions = self.client.revisions().list(fileId=file_id, fields='items(id)').execute()
        max_rev = revisions['items'][-1]['id']

        choice = FileChoice(str(file_id), title, drive, int(max_rev))
        logger.debug('Choice is {}'.format(choice))
        return choice

    def list_all_files(self):
        """
        Retrieve a list of File resources from the google API client. 
        :return: List of File resources 
        """

        result = defaultdict(list)
        page_token = None
        for drive_type in gsuite.SERVICES:
            while True:
                param = {'q': gsuite.MIME_TYPE.format(drive_type),
                         'fields': 'items(title, id)'}
                if page_token:
                    param['pageToken'] = page_token

                try:
                    files = self.client.files().list(**param).execute()
                except googleapiclient.errors.HttpError, e:
                    logger.error('Failed to retrieve list of files', exc_info=True)
                    break
                else:
                    result[drive_type].extend(files['items'])
                    page_token = files.get('nextPageToken')
                    if not page_token:
                        break
        return result

    @staticmethod
    def get_download_ext(html_response):
        """ 
        Returns extension for downloaded resource as formatted for GSuite API html response
        :param html_response:  GSuite API html response 
        :return: Extension of downloaded resource (png, pdf, doc, etc)
        """
        cdisp = html_response['content-disposition']
        start_index = cdisp.index('.')
        end_index = cdisp.index('"', start_index)
        extension = cdisp[start_index:end_index]
        return extension
