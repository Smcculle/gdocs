import Tkinter as Tk
import errno
import ntpath
import os
import re
import shutil
import tempfile
import tkFileDialog
from contextlib import contextmanager


def strip_invalid_characters(filename):
    """ Very conservative stripping of extraneous characters in filename """
    filename = re.sub('[^\w\-_. ]', '_', filename)
    filename = re.sub('__+', '_', filename)
    return filename


def strip_path_extension(path):
    """ Returns filename by stripping extension from basename"""
    basename = ntpath.basename(path)
    return os.path.splitext(basename)[0]


def get_download_ext(html_response):
    """Returns extension for downloaded resource"""
    cdisp = html_response['content-disposition']
    start_index = cdisp.index('.')
    end_index = cdisp.index('"', start_index)
    extension = cdisp[start_index:end_index]
    return extension


def choose_file_dialog(**options):
    """ Creates an open file dialog to choose files, and returns a handle to those file """
    root = Tk.Tk()
    root.geometry('200x200+0+0')
    root.wait_visibility()
    root.wm_attributes('-alpha', 0.0)
    root.lift()
    root.focus_force()
    chosen_files = tkFileDialog.askopenfilenames(**options)
    root.destroy()
    return chosen_files


def ensure_path(path):
    """ Attempts to make a directory and raises exception if there is an issue"""
    try:
        os.makedirs(path)
    except OSError as exception:
        #  # if the directory exists, ignore error
        if exception.errno != errno.EEXIST:
            raise


def remove_directory(path):
    """ Deletes all files and removes directory at path"""
    try:
        shutil.rmtree(path)
    except IOError as e:
        # if the directory does not exist, ignore error
        if e.errno != errno.ENOENT:
            print 'I/O error removing temp files at {}'.format(path)
            raise


@contextmanager
def temp_directory():
    """ Creates and removes temporary directory using WITH statement """
    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        remove_directory(path)
