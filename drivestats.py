import os.path, sys
import time
from collections import Counter
from datetime import timedelta
import json

#todo*:  Index starting better for slide logs not beginning at 1
#todo:  map gid to account name through retrieving history with changelog.
#todo:  stats for pages that don't start at revision 1
#var historyUrl = baseUrl + docId + "/revisions/history?id=" + docId + "&start=1&end=-1&zoom_level=0&token=" + token

def get_list(line):
    ''' Returns line in a list format, discarding the style dictionary at the end'''
    stop_index = line.find('{')
    stop_index -= 1  #stops an empty element at the end of the list
    return line[:stop_index].split('|')

def temp(t):
    counter = Counter()
    session_counter = Counter()
   # data = get_data(filename)
    first_line = get_list(data[0])
    start_time = int(first_line[0])/1000
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
            
        counter[action] +=1
        prev_revision = revision

def print_stats(counter, session_counter, action_counter, revision_dict, start_time, end_time):
    counter['revisions'] += 1    
    fmt = "%Y-%m-%d %H:%M:%S"
    authors = list(set(revision_dict.values()))
    timediff = timedelta(seconds=(end_time - start_time))
    revperday = counter['revisions'] / (timediff.total_seconds() / 86400)
    longest_session, longest_session_revs = session_counter.most_common(1)[0]  

    print 'File created on %s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)))
    print 'Last revision on %s' % (time.strftime(fmt, time.localtime(end_time)))
    print 'Age of file: %s' % timediff
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
    data = data[5:]
    data = json.loads(data)
    data = data['changelog']

    data = data[1:]
   
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
