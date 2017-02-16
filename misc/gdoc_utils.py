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


def choose_file_dialog(**options):
    """ Creates an open file dialog to choose a file, and returns a handle to that file """
    root = Tk.Tk()
    root.geometry('200x200+200+200')
    root.attributes('-alpha', 0.0)
    root.lift()
    root.focus_force()
    chosen_file = tkFileDialog.askopenfile(**options)
    root.destroy()
    return chosen_file


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
