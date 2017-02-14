"""log2csv takes a google changelog and converts it into a flattened log separated by delimiter,
default '|'.  Output is saved in flat_logs folder with _flat appended to the name
Usage: python log2csv.py <inputfiles>.    May use wildcards for file.
Ex: python log2csv.py changelogs/*.txt
"""

import glob
import json
import sys
from collections import OrderedDict

import misc.mappings as mappings

CHUNKED_ORDER = ['si', 'ei', 'st']
DELIMITER = '|'


def rename_keys(log_dict):
    """rename minified variables using mappings in mappings.py. preserves order"""
    log_dict = OrderedDict(log_dict)
    for key in log_dict.keys():
        try:
            new_key = mappings.remap(key)
            log_dict[new_key] = log_dict.pop(key)

            # recursively replace deep dictionaries
            if isinstance(log_dict[new_key], dict):
                log_dict[new_key] = rename_keys(log_dict[new_key])
        except KeyError:
            # if key is not in mappings, leave old key unchanged.
            pass

    return log_dict


def to_file(flat_log, filename):
    """writes log to file in CSV format"""
    filename = filename.replace('.txt', '_flat.txt')
    # changelogs/1_413.txt

    if 'changelogs' in filename:
        filename = filename.replace('changelogs/', 'flat_logs/')
    else:
        filename = 'flat_logs/' + filename

    ensure_path(filename)

    with open(filename, 'w') as outfile:
        for line in flat_log:
            outfile.write(line + '\n')
    print "finished with", filename


def ensure_path(filename):
    path = filename[:filename.rfind('/')]
    mappings.ensure_path(path)


def flatten_mts(entry, line_copy, line):
    """ Recursively flatten multiset entry.

  Args:
    entry: an entry in changelog
    line_copy: a flattened list of each mts action appended to line
    line:  shared info for the entry( id, revision, timestamp, etc)
  Returns:
    None.  line_copy contains flattened entries to be appended to log.
  """
    if 'mts' not in entry:
        new_line = list(line)

        try:
            mts_action = mappings.remap(entry['ty'])
        except KeyError:
            mts_action = entry['ty']

        # add action, action dictionary with descriptive keys
        new_line.append(mts_action)
        new_line.append(json.dumps(rename_keys(entry)))
        line_copy.append(new_line)

    else:
        for item in entry['mts']:
            # fix missing sugid in multiset suggestion delete
            if 'dss' in item['ty']:
                sugid = (x['sugid'] for x in entry['mts'] if 'sugid' in x).next()
                item['sugid'] = sugid
            flatten_mts(item, line_copy, line)


def parse_log(c_log, flat_log):
    """parses changelog part of log"""

    flat_log.append('changelog')

    for entry in c_log:
        line = []
        # ignore None in last index, add dictionary in [0] at end
        # for i in range(1, len(entry) - 1):
        for item in entry[1:-1]:
            line.append(item)

        # break up multiset into components
        if 'mts' in entry[0]:
            line_copy = []
            flatten_mts(entry[0], line_copy, line)
            for item in line_copy:
                flat_log.append(DELIMITER.join(str(col) for col in item))
        else:
            action_type = mappings.remap(entry[0]['ty'])
            line.append(action_type)
            line.append(json.dumps(rename_keys(entry[0])))
            flat_log.append(DELIMITER.join(str(entry) for entry in line))


def parse_snapshot(snapshot, flat_log):
    """parses snapshot part of log"""

    flat_log.append('chunkedSnapshot')
    snapshot = snapshot[0]

    # take care of plain text paste entry
    if 's' in snapshot[0]:
        snapshot[0]['type'] = snapshot[0].pop('ty')
        snapshot[0]['string'] = snapshot[0].pop('s').replace('\n', '\\n')
        del snapshot[0]['ibi']  # this value is always 1 and unused
        flat_log.append(json.dumps(snapshot.pop(0)))  # pop entry to remove special case

    # parse style modifications
    for entry in snapshot:
        line = get_snapshot_line(snapshot_entry=entry)
        flat_log.append(DELIMITER.join(str(item) for item in line))


def get_snapshot_line(snapshot_entry):
    """
    Turns raw line from snapshot into a translated version for flat_log with style dictionary at end
    :param snapshot_entry: A line in the snapshot part of the log
    :return: line entry for flat_log with style dictionary at end
    """
    line = []
    for key in CHUNKED_ORDER:
        line.append(snapshot_entry[key])
    try:
        action_type = mappings.remap(snapshot_entry['ty'])
        style_mod = json.dumps(rename_keys(snapshot_entry['sm']))

    except KeyError:
        # logging.warning('KeyError, %s missing', key)
        pass
    else:
        line.append(action_type)
        line.append(style_mod)

    return line


def get_flat_log(data):
    """Splits into snapshot and changelog, parses each, and returns flat log"""
    # log = json.loads(data)
    flat_log = []

    try:
        parse_snapshot(data['chunkedSnapshot'], flat_log)
        parse_log(data['changelog'], flat_log)
    except KeyError:
        raise

    return flat_log


def main(argv):
    files = []

    if argv:
        for arg in argv:
            files += glob.glob(arg)
    else:
        print __doc__
        sys.exit(2)

    if not files:
        print 'No files found.  ', __doc__
        sys.exit(2)

    for doc in files:
        with open(doc, 'r') as infile:
            data = infile.read()
            if data[0] == ')':
                data = data[5:]
            data = json.loads(data)
            flat_log = get_flat_log(data)
            to_file(flat_log, doc)


if __name__ == '__main__':
    main(sys.argv[1:])
