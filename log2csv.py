import sys
from collections import OrderedDict

import json
import glob
import logging  #remove later

import mappings

 

#todo:  look at reverts

CHUNKED_ORDER = ['si', 'ei', 'st']#, 'ty', 'sm']
keys = set() # temporary

def rename_keys(log_dict):
    """rename minified variables using mappings in mappings.py. preserves order"""
    log_dict = OrderedDict(log_dict)
    for key in log_dict.keys():
        try:
            new_key = mappings.remap(key)
            log_dict[new_key] = log_dict.pop(key)

            #recursively replace deep dictionaries
            if isinstance(log_dict[new_key], dict):
                log_dict[new_key] = rename_keys(log_dict[new_key])
        except KeyError:
            pass
            #logging.warning('KeyError, %s missing in renamekeys', key)
            #keys.add(key)
    return log_dict

def to_file(flat_log, filename):
    """writes log to file in CSV format"""
    filename = filename.replace('.txt', '_out.txt')

    if 'logs' in filename:
        filename = filename.replace('logs', 'output')
    else:
        filename = 'output/' + filename

    with open(filename, 'w') as outfile:
        for line in flat_log:
            outfile.write(line + '\n')
    print "finished with", filename

def write_keys(str):
    with open('keys.txt', 'a') as outfile:
        outfile.write(str)

def flat_mts(entry, line_copy, line):
    """Tail recursion to flatten multiset entry.

  Args:
    entry: an entry in changelog
    line_copy: a flattened list of each mts action appended to line
    line:  shared info for the entry( id, revision, timestamp, etc)
  Returns:
    None.  line_copy contains flattened entries to be appended to log.
  """
    if not 'mts' in entry:
        new_line = list(line)
        mts_action = mappings.remap(entry['ty'])
        new_line.append(mts_action)

        #action dictionary with descriptive keys
        new_line.append(json.dumps(rename_keys(entry)))
        line_copy.append(new_line)
    else:
        for item in entry['mts']:
            flat_mts(item, line_copy, line)

def parse_log(c_log, flat_log):
    """parses changelog part of log"""

    flat_log.append('changelog')

    for entry in c_log:
        line = []
        # ignore None in last index, add dictionary in [0] at end
        for i in range(1, len(entry) - 1):
            line.append(entry[i])

        #break up multiset into components
        if 'mts' in entry[0]:
            line_copy = []
            flat_mts(entry[0], line_copy, line)
            for item in line_copy:
                flat_log.append('|'.join(str(col) for col in item))
        else:
            try:
                action_type = mappings.remap(entry[0]['ty'])
                line.append(action_type)
                line.append(json.dumps(rename_keys(entry[0])))
            except:
                raise
            flat_log.append('|'.join(str(entry) for entry in line))

def parse_snapshot(snapshot, flat_log):
    """parses snapshot part of log"""

    flat_log.append('chunkedSnapshot')
    snapshot = snapshot[0]

    #take care of plain text paste entry
    if 's' in snapshot[0]:
        snapshot[0]['type'] = snapshot[0].pop('ty')
        snapshot[0]['string'] = snapshot[0].pop('s').replace('\n', '\\n')
        del snapshot[0]['ibi'] #this value is always 1
        flat_log.append(json.dumps(snapshot[0]))

    #parse style modifications
    for i in xrange(1, len(snapshot)):
        line = []
        try:
            for key in CHUNKED_ORDER:
                line.append(snapshot[i][key])

            action_type = mappings.remap(snapshot[i]['ty'])
            line.append(action_type)

            style_mod = json.dumps(rename_keys(snapshot[i]['sm']))
            line.append(style_mod)
            flat_log.append('|'.join(str(entry) for entry in line))

        except KeyError:
            #logging.warning('KeyError, %s missing', key)
            keys.add(key)
                
def get_flat_log(data):
    """Splits into snapshot and changelog, parses each, and returns flat log"""
    #log = json.loads(data)
    flat_log = []
    
    try:
        parse_snapshot(data['chunkedSnapshot'], flat_log)
        parse_log(data['changelog'], flat_log)
    except KeyError:
        raise

    return flat_log
    
def main(argv):
    logging.basicConfig(filename='output/error.log', level=logging.DEBUG)
    files = []

    if argv:
        for arg in argv:
            files += glob.glob(arg)
    else:
        print 'usage: python log2csv.py <inputfiles>  \nMay use wildcards for file.',\
              ' Ex: python log2csv.py logs/*.txt'
        sys.exit(2)

    if not files:
        print 'No files found.  Usage: python log2csv.py <inputfiles>  \nMay use wildcards',\
              ' for file. Ex: python log2csv.py logs/*.txt'
        sys.exit(2)

    for doc in files:
        with open(doc, 'r') as infile:
            data = infile.read()
            if data[0] == ')':
                data = data[5:]
        '''
        log = json.loads(data)
        flat_log = []

        try:
            parse_snapshot(log['chunkedSnapshot'], flat_log)
            parse_log(log['changelog'], flat_log)
        except KeyError:
            raise
        '''
        data = json.loads(data)
        flat_log = get_flat_log(data)
        to_file(flat_log, doc)

if __name__ == '__main__':
    main(sys.argv[1:])
