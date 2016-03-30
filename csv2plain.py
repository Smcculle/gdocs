"""csv2plain.py uses the result from log2csv (flat log) to output the plain text contents.
 Usage: python csv2plain.py <inputfile>. Takes single output log from log2csv
 Ex: \tpython log2csv.py flat_logs/1_413_out.txt
"""

import sys
import os
import json
import ntpath

BASE_DIR = 'flat_logs/plaintext/'


def insert(old_string, new_string, index):
    """ inserts string new into string old at position i"""
    # in log, index starts at 1
    index -= 1
    return old_string[:index] + new_string + old_string[index:]


def delete(old_string, starting_index, ending_index):
    """ Removes portion from old_string from starting_index to ending_index"""
    # in log, index starts at 1
    starting_index -= 1
    return old_string[:starting_index] + old_string[ending_index:]


def write(s, filename):
    outfile = filename.replace('_flat', '_plain')
    outfile = '{base_dir}{outfile}'.format(base_dir=BASE_DIR, outfile=ntpath.basename(outfile))
    with open(outfile, 'w') as f:
        f.write(s)
    print "finished writing to", outfile


def get_dict(line):
    """ converts string dictionary at end of line in log to dictionary object"""
    i = line.index('{')
    try:
        log_dict = json.loads(line[i:])
    except ValueError:
        raise  # should not have a line without dictionary
    else:
        return log_dict


def parse_log(log):
    """ converts log2csv output file to plaintext"""
    plain_text = ''
    log_dict = get_dict(log[log.index('chunkedSnapshot') + 1])

    # should not contain a string if log starts at revision 1
    if 'string' in log_dict:
        chunk_string = log_dict['string']
        # chunk_string = chunk_string.decode('unicode-escape')
        plain_text += chunk_string

    # start after changelog line, which has no data
    cl_index = log.index('changelog') + 1

    for line in log[cl_index:]:
        try:
            action_dict = get_dict(line)

            if action_dict['type'] == 'is':
                i = action_dict['ins_index']
                s = action_dict['string']
                plain_text = insert(old_string=plain_text, new_string=s, index=i)

            elif action_dict['type'] == 'ds':
                si = action_dict['start_index']
                ei = action_dict['end_index']
                plain_text = delete(old_string=plain_text, starting_index=si, ending_index=ei)
        except:
            pass

    return plain_text


def main(argv):
    if not argv:
        print __doc__
        sys.exit(2)
    else:
        filename = argv[0]

    if not os.path.isfile(filename):
        print 'File named {} could not be found. '.format(filename), __doc__
        sys.exit(2)

    with open(filename, 'r') as f:
        log = f.read().split('\n')

    plain_text = parse_log(log)
    # some paragraph style elements outside 128 ascii range
    write(plain_text.encode('utf-8').strip(), filename)
    # write(plain_text.encode('mbcs').strip(), filename)


if __name__ == '__main__':
    main(sys.argv[1:])
