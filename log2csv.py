import json
import csv
import mappings
from collections import OrderedDict
import logging  #remove later

#todo:  clean up comments, add arg handling, look at reverts

CHUNKED_ORDER = ['si', 'ei', 'st']#, 'ty', 'sm']
flat_log = []
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
        
def to_file():
    """writes log to file in CSV format"""
    
    with open('output\\out.txt', 'w') as f:
        for line in flat_log:
            f.write( line + '\n')

def wTest(str):
    with open('keys.txt', 'a') as f:
        f.write(str)
        
def parse_glog(glog):
    """parses changelog part of log"""
    
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
                flat_log.append(lineCopy[i])
        else:
            try:
                line.append(json.dumps(rename_keys(entry[0])))
            except AttributeError:
                print "no keys() attribute", sys.exc_info()[0]
                raise
            flat_log.append(line)
        #line += str(entry[0])
        #line.append(entry[0])
        #print line
        #flat_log.append(line)
    #more_to_file(flat_log)
    #log_conv(flat_log)
            
def parse_log(glog):
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
        #line += str(entry[0])
        #line.append(entry[0])
        #print line
        #flat_log.append(line)
    #more_to_file(flat_log)
    #log_conv(flat_log)

def parse_snapshot(snapshot):
    """parses snapshot part of log"""
    flat_log.append('chunkedSnapshot')
    snapshot = snapshot[0]
    
    #take care of plain text paste entry
    if 's' in snapshot[0]:
        snapshot[0]['type'] = snapshot[0].pop('ty')
        snapshot[0]['string'] = snapshot[0].pop('s').replace('\n', '\\n')
        del snapshot[0]['ibi'] #this value is always 1
        
        #line.append(action_type)
        #line.append(snapshot[0])
        #
        #for value in snapshot[0].values():
         #   #line += repr(value) + ','
          #  try:
           #     line += value + ','
            #except TypeError:
             #   line += str(value) + ','
        flat_log.append(json.dumps(snapshot[0]))

    #parse style modifications
    for i in xrange(1, len(snapshot)):
        #line = ''
        line = []
        try:
            for key in CHUNKED_ORDER:
                line.append(snapshot[i][key])
            t1 = mappings.remap(snapshot[i]['ty'])
            #line.append(mappings.remap(snapshot[i]['ty']))
            t2 = json.dumps(rename_keys(snapshot[i]['sm']))
            #line.append(json.dumps(rename_keys(snapshot[i]['sm'])))
            #print t1,t2
            line.append(t1)
            line.append(t2)
        except KeyError:
            logging.warning('KeyError, %s missing', key)
            raise
            '''
            try:
                line += snapshot[i][key] + ','
            except TypeError:
                line += str(snapshot[i][key]) + ','
            except KeyError:
                print "Key not found"
                raise    
        #print type(line)
        '''
        #flat_log.append(line[:-1])
        flat_log.append(','.join(str(entry) for entry in line))
        
def main():
    filename = 'logs\\' + '1_413.txt'
    logging.basicConfig(filename='logs\\error.log', level=logging.DEBUG)
        
    with open(filename, 'r') as f:
        data = f.read()
        if data[0] == ')':
            data = data[5:]

    js = json.loads(data)
    #js = fix_unicode(js)
    q0 = 'chunkedSnapshot'
    q1 = 'changelog'
    parse_snapshot(js[q0])
    parse_log(js[q1])
    to_file()
    for key in keys:
        wTest(str(key) + '\n')
    
if __name__ == '__main__':
    main()

