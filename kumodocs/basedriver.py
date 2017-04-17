import os
from abc import abstractmethod, ABCMeta, abstractproperty


# noinspection PyClassHasNoInit
class BaseDriver(object):
    __metaclass__ = ABCMeta

    class KumoObj(object):
        """ A Kumo object retrieved from revision log sharing common properties:
        
        content:  content of the object
        type:  the object's type
        service:  service the object originated from
        file_name:  file name the object originated from
        start:  starting revision of the log object was recovered from
        end:  ending revision of the log object was recovered from """
        __slots__ = 'content', 'type', 'service', 'file_name', 'start', 'end',

        def __init__(self, content, type_, service, file_name, start, end):
            self.content = content
            self.type = type_
            self.service = service
            self.file_name = file_name
            self.start = start
            self.end = end

    @abstractproperty
    def logger(self):
        """
        Defines a logger property that must be provided in the derived class 
        :return: logger property
        """
        pass

    @logger.setter
    def logger(self, value):
        """
        Defines a setter for the logger property
        :return: None
        """
        pass

    @abstractmethod
    def get_log(self, file_id, start, end):
        """
        Returns the native revision log for this driver's service. 
        :param file_id: File ID 
        :param start: Starting revision
        :param end: Ending revision
        :return: unparsed revision log 
        """
        pass

    @abstractmethod
    def flatten_log(self, log):
        """
        Takes a native revision log and converts to the common log format.  
        :param log: Native revision log from some service
        :return: Flattened log in the common log format.  
        """
        pass

    @abstractmethod
    def recover_objects(self, flat_log):
        """ Recovers plain-text from the flat (common) log, as well as any associated 
        objects (images, suggestions, comments, etc ).  
        
        :param flat_log:  A native log that has been flattened using flatten_log 
        :return: None; outputs all recovered objects to the location specified by self.write_object
        """
        pass

    @abstractmethod
    def choose_file(self):
        """
        Lists drive options and prompts user for a file choice.  
        :return: Returns necessary information to retrieve the log of this file, such as any file_id, title, 
        and revisions available.  
        """
        pass

    def write_object(self, kumoobj, base_dir='../downloaded'):
        """
        Writes object to disk at location specified in directory
        :param kumoobj: An object to write, containing originating service, file_name, start and end revision, 
        as well as content and object type.  
        :param base_dir: Base directory to append file path. 
        :return: None
        """

        path_format = '{base_dir}/{service}/{file_name}/{start}-{end}/{obj_name}'
        outfile = os.path.realpath(path_format.format(base_dir, kumoobj.service, kumoobj.file_name, kumoobj.start,
                                                      kumoobj.end, kumoobj.type))

        try:
            with open(outfile, 'wb') as f:
                f.write(kumoobj.content)
        except IOError:
            self.logger.exception('Failed to write {} object'.format(kumoobj.type))
