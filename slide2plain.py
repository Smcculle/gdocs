import json

filename = 'slogs/1_196.txt'
with open(filename, 'r') as f:
    data = f.read()
    if data[0] == ')':
        data = data[5:]

data = json.loads(data)

data = data['changelog']
data = data[1:]
slide_dict = {}

#first slide id is 'p'
slide_dict['i0'] = {'owner': 'p', 'string': ''}
slide_dict['i1'] = {'owner': 'p', 'string': ''}

def add_text(line):
    print "add_text:", line

def add_box(line):
    print "add_box", line

def del_text(line):
    print "del_text", line

def parse_mts(data):
    print "parsing mts"
    action_list = data[1]
    for line in action_list:
        parse(line)
        
functions = {15: add_text, 4:parse_mts, 16:del_text, 3:add_box}

def parse(line):
    action = line[0]
    '''
    if action == 15:
        add_text(line)
    elif action == 4:
        parse_mts(line)
    elif action == 16:
        del_text(line)
    '''
    if action in functions:
        func = functions[action]
        func(line)

for line in data:
    parse(line[0])
