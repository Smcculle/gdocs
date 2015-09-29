import os.path, sys
import time
from collections import Counter
from datetime import timedelta
import json

#todo*:  Index starting better for slide logs not beginning at 1, control output with flag (console vs log)
#todo:  map gid to account name through retrieving history with changelog.
#todo:  stats for pages that don't start at revision 1
#todo: refactor similar code into 1 function
#var historyUrl = baseUrl + docId + "/revisions/history?id=" + docId + "&start=1&end=-1&zoom_level=0&token=" + token

def get_list(line):
    ''' Returns line in a list format, discarding the style dictionary at the end'''
    stop_index = line.find('{')
    stop_index -= 1  #stops an empty element at the end of the list
    return line[:stop_index].split('|')

def print_stats(counter, session_counter, action_counter, revision_dict, start_time, end_time):
    '''Prints a list of stats to the console'''
    counter['revisions'] += 1    
    fmt = "%Y-%m-%d %H:%M:%S"
    authors = list(set(revision_dict.values()))
    timediff = timedelta(seconds=(time.mktime(time.localtime()) - start_time))
    if timediff.days > 0:
        revperday = counter['revisions'] / (timediff.total_seconds() / 86400)
        days = timediff.days
    else:
        revperday = counter['revisions']
        days = 0
    (hours, seconds) = divmod(timediff.seconds, 3600)
    longest_session, longest_session_revs = session_counter.most_common(1)[0]

    #modify this to write to file. 
    #sys.stdout = open(filename, 'w')
    print 'File created on %s' % (time.strftime(fmt, time.localtime(start_time)))
    print 'Last revision on %s' % (time.strftime(fmt, time.localtime(end_time)))
    print 'Age of file: %d days, %d hours, %d minutes' % (days, hours, seconds/60)
    print 'File contains %d total revisions, broken down by google id:' % (counter['revisions'])
    for author in authors:
        print '\t %s with %s revisions' % (author, counter[author])
    print 'The average number of revisions per day was %d over a total of %s sessions' % (revperday, len(revision_dict))
    print 'The average number of revisions per session was %d, with the longest session at %d revisions by %s' %(
        (counter['revisions'] / len(revision_dict) ), longest_session_revs, revision_dict[longest_session] )
    print 'Revisions by action:'
    for action in action_counter:
        print '\t', action, ':', action_counter[action]

def parse_slide(data):
    action_dict = {15: 'add_text', 4:'multiset_op', 16:'del_text', 3:'add_box',
             12:'add_slide', 13:'del_slide', 0:'del_box', 35:'revert'}
    data = json.loads(data)
    data = data['changelog']
    counter = Counter()
    session_counter = Counter()
    action_counter = Counter()
    
    start_time = data[0][1]/1000
    end_time = data[-1][1]/1000

    revision_dict = {}
    prev_revision = -1
    counter['revisions'] = -1
    
    if not data[0][5]:
        data = data[1:]

    for line in data:
        try:
            action = action_dict[line[0][0]]
        except KeyError:
            action = 'unknown'
        time = line[1]
        google_id = line[2]
        revision = line[3]
        sid = line[4]

        counter['revisions'] += 1
        counter[google_id] += 1
        session_counter[sid] += 1
        if sid not in revision_dict and sid != 'None':
            revision_dict[sid] = google_id
            
        action_counter[action] += 1
    print_stats(counter, session_counter, action_counter, revision_dict, start_time, end_time)
    
def parse_doc(data):
    
    data = data.split('\n')
    #ignore lines in snapshot
    i = data.index('changelog')
    data = data[i+1:]

    counter = Counter()
    session_counter = Counter()
    action_counter = Counter()
    
    first_line = get_list(data[0])
    start_time = int(first_line[0])/1000
    end_time = int(get_list(data[-2])[0])/1000
    counter[first_line[1]] += 1
    counter[first_line[3]] += 1
    counter[first_line[5]] += 1
    revision_dict = {}
    prev_revision = -1
    for line in data[1:-1]:
        
        line = get_list(line)
        google_id = line[1]
        revision = line[2]
        sid = line[3]
        action = line[5]

        if prev_revision != revision:
            counter['revisions'] += 1
            counter[google_id] += 1
            session_counter[sid] += 1
        if sid not in revision_dict and sid != 'None':
            revision_dict[sid] = google_id
            
        action_counter[action] += 1
        prev_revision = revision
        
    counter['revisions'] += 1
    print_stats(counter, session_counter, action_counter, revision_dict, start_time, end_time)
def main(argv):

    helpmsg = 'Usage: python log2csv.py <inputfile>. Takes output log from log2csv or changelog from slides\n'\
              'Ex: \tpython log2csv.py output/1_254_out.txt  or\n'\
              '  \tpython log2csv.py slogs/1_317.txt'
    if not argv:
        print helpmsg
        sys.exit(2)
    else:
        filename = argv[0]

    if not os.path.isfile(filename):
        print 'No file found.', helpmsg
        sys.exit(2)

    with open(filename, 'r') as infile:
        data = infile.read()

    #indicates slide log
    if data[0] == ')':
        parse_slide(data[5:])
    else:
        parse_doc(data)

if __name__ == '__main__':
    main(sys.argv[1:])
