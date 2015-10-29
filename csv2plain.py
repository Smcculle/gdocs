import json
import sys, os

def insert(old, new, i):
    """ inserts string new into string old at position i"""
    #in log, index starts at 1
    i = i - 1
    return old[:i] + new + old[i:]

def delete(old, si, ei):
    """ inserts string new into string old at position i"""
    #in log, index starts at 1
    si = si - 1
    return old[:si] + old[ei:]

def write(s, filename):
    of = filename.replace('_out', '_plain')
    with open(of, 'w') as f:
        f.write(s)
    print "finished writing to", of

def get_dict(line):
    """ converts string dictionary at end of line in log to dictionary object"""
    try:
        i = line.index('{')
        log_dict = json.loads(line[i:])
        return log_dict
    except:
        #should not have a line without a dictionary
        raise

def parse_log(log):
    """ converts log2csv output file to plaintext"""
    plain_text = ''
    logdict = get_dict(log[log.index('chunkedSnapshot') + 1])
    
    #should not contain a string if log starts at revision 1
    if 'string' in logdict:
        chunk_string = logdict['string']
        chunk_string = chunk_string.decode('unicode-escape')    
        plain_text += chunk_string

    #start after changelog line, which has no data
    cl_index = log.index('changelog') + 1

    for line in log[cl_index:]:    
        try:
            actiondict = get_dict(line)

            if actiondict['type'] == 'is':
                i = actiondict['ins_index']
                s = actiondict['string']
                plain_text = insert(plain_text, s, i)

            elif actiondict['type'] == 'ds':
                si = actiondict['start_index']
                ei = actiondict['end_index']
                plain_text = delete(plain_text, si, ei)
        except:
            pass #get rid of last empty line

    return plain_text
    

def main(argv):
    helpmsg = 'Usage: python csv2plain.py <inputfile>. Takes single output log from log2csv\n'\
              'Ex: \tpython log2csv.py output/1_413_out.txt'
    if not argv:
        print helpmsg
        sys.exit(2)
    else:
        filename = argv[0]

    if not os.path.isfile(filename):
        print 'No file found.', helpmsg
        sys.exit(2)

    with open(filename, 'r') as f:
        log = f.read().split('\n')

    plain_text = parse_log(log)
    #some paragraph style elements outside 128 ascii range
    write(plain_text.encode('utf-8').strip(), filename)
    #write(plain_text.encode('mbcs').strip(), filename)

if __name__ == '__main__':
    main(sys.argv[1:])
