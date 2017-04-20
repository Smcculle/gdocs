import Tkinter as Tk
import errno
import logging
import ntpath
import os
import re
import shutil
import tempfile
import tkFileDialog
from contextlib import contextmanager

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s: %(name)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filename='config/log.log',
                    filemode='w')

log = logging.getLogger(__name__)


def strip_invalid_characters(filename):
    """
    Very conservative stripping of extraneous characters in filename.  Characters and underscore allowed.
    :param filename: File name obtained from cloud service
    :return: 
    """
    new_filename_partial = re.sub('[^\w\-_. ]', '_', filename)
    new_filename = re.sub('__+', '_', new_filename_partial)
    log.debug('Stripped invalid characters from filename: {} -> {}'.format(filename.encode('utf-8'), new_filename))
    return new_filename


def split_title(title):
    """
    Separates filename and drive type into a tuple. 
    :param title: File title with drive extension
    :return: A tuple of title, drive 
    """
    ext_index = title.rfind('.')
    drive = title[ext_index + 1:]
    title = strip_path_extension(title[:ext_index])
    if drive in ['drawing', 'form', 'spreadsheet']:
        drive += 's'
        print('drive is now', drive)
    return title, drive


def strip_path_extension(path):
    """ Returns filename by stripping extension from basename"""
    basename = ntpath.basename(path)
    return os.path.splitext(basename)[0]


def choose_file_dialog(**options):
    """ Creates an open file dialog to choose a file, and returns a handle to that file """
    root = Tk.Tk()
    root.geometry('0x0+400+400')
    root.wait_visibility()
    root.wm_attributes('-alpha', 0.0)
    root.lift()
    root.focus_force()
    chosen_files = tkFileDialog.askopenfile(**options)
    root.destroy()
    return chosen_files


def ensure_path(path):
    """ Attempts to make a directory and raises exception if there is an issue"""
    try:
        os.makedirs(path)
    except OSError as exception:
        # if the directory exists, ignore error
        if exception.errno != errno.EEXIST:
            log.exception('I/O error creating directory at: {}'.format(path))
            raise


def remove_directory(path):
    """ Deletes all files and removes directory at path"""
    try:
        shutil.rmtree(path)
    except IOError as e:
        # if the directory does not exist, ignore error
        if e.errno != errno.ENOENT:
            log.exception('I/O error removing temp files at: {}'.format(path))
            raise


@contextmanager
def temp_directory():
    """ Creates and removes temporary directory using WITH statement """
    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        remove_directory(path)
