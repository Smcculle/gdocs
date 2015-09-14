import sys
import json
import glob
import logging  #remove later
import mappings

try:
    from collections import OrderedDict
    #for python 2.6 install ordereddict
except ImportError:
    from ordereddict import OrderedDict
    
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
            logging.warning('KeyError, %s missing', key)
            keys.add(key)
    return log_dict
        
def to_file(flat_log, filename):
    """writes log to file in CSV format"""
    filename = filename.replace('.txt', '_out.txt')
    
    if 'logs' in filename:
        filename = filename.replace('logs','output')
    else:
        filename = 'output/' + filename
    
    with open(filename, 'w') as f:
        for line in flat_log:
            f.write( line + '\n')
    print "finished with",filename
   
def write_keys(str):
    with open('keys.txt', 'a') as f:
        f.write(str)
        
def parse_log(glog, flat_log):
    """parses changelog part of log"""
    flat_log.append('changelog')
    
    for entry in glog:
        line = []
        # ignore None in last index, add dictionary in [0] at end
        for i in range(1, len(entry) - 1):
            try:
                #line += entry[i] + ','
                line.append(entry[i])
            except TypeError:
                line += str(entry[i]) + ','

        #break up multiset into components
        if 'mts' in entry[0]:
            lineCopy = [list(line) for i in range(len(entry[0]['mts']))]
            for i,mts_action in enumerate(entry[0]['mts']):
                lineCopy[i].append(json.dumps(rename_keys(mts_action)))
                flat_log.append(','.join(str(entry) for entry in lineCopy[i]))
        else:
            try:
                line.append(json.dumps(rename_keys(entry[0])))
            except AttributeError:
                print "no keys() attribute", sys.exc_info()[0]
                raise
            flat_log.append(','.join(str(entry) for entry in line))

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
            
        except KeyError:
            logging.warning('KeyError, %s missing', key)
        
        flat_log.append(','.join(str(entry) for entry in line))
        
def main(argv):
    logging.basicConfig(filename='output/error.log', level=logging.DEBUG)
    files = []
    if argv:
        for arg in argv:
            files += glob.glob(arg)
    else:
        print 'usage: python log2csv.py <inputfiles>  \nMay use wildcards for file.',\
              ' Ex: python log2csv.py logs/254*.txt'
        sys.exit(2)
        
    if not files:
        print 'No files found.  Usage: python log2csv.py <inputfiles>  \nMay use wildcards for file.',\
              ' Ex: python log2csv.py logs/254*.txt'
        sys.exit(2)
        
    for doc in files:
        
        with open(doc, 'r') as f:
            data = f.read()
            if data[0] == ')':
                data = data[5:]

        js = json.loads(data)
        flat_log = []
        
        try:
            parse_snapshot(js['chunkedSnapshot'], flat_log)
            parse_log(js['changelog'], flat_log)
        except KeyError:
            logging.warning('Key %s missing in parse', key)
            raise
        
        to_file(flat_log, doc)
        
        
if __name__ == '__main__':
    main(sys.argv[1:])

