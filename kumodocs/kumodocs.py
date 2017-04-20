import logging

import gsuite.driver

LEVEL_DEFAULT = logging.INFO


def start_logger(loglevel, handler=logging.StreamHandler):
    """
    Starts the logging service with specified level and handler. 
    :param loglevel: Log all events of this severity and above.  One of DEBUG, INFO, WARNING, ERROR, CRITICAL
    :param handler: A logging handler that controls which messages are displayed to console 
    :type loglevel: str
    :return: Log object
    """
    console_handler = handler()
    console_handler.setFormatter(logging.Formatter('%(name)-25s: %(levelname)-8s %(message)s'))
    kumologger = logging.getLogger('kumodocs')
    num_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(num_level, int):
        console_handler.setLevel(LEVEL_DEFAULT)
        kumologger.warn('Invalid log level: {}.  Setting default log to {}'.format(loglevel, LEVEL_DEFAULT))
    else:
        console_handler.setLevel(num_level)
    logging.getLogger('').addHandler(console_handler)
    return kumologger


def main():
    # TODO arg handling
    logger = start_logger('debug')

    driver = gsuite.driver.GSuiteDriver()
    choice = driver.choose_file()
    start, end = driver.prompt_rev_range()
    log = driver.get_log(start=start, end=end)
    flat_log = driver.flatten_log(log)
    driver.recover_objects(log=log, flat_log=flat_log)


if __name__ == "__main__":
    main()
