import os
import json
import errno

#todo:  add main, arg handling, better solution to slide/box dict, clean

filename = 'slogs/1_317.txt'
#filename = 'slogs/deltest.txt'
with open(filename, 'r') as f:
    data = f.read()
    if data[0] == ')':
        data = data[5:]

data = json.loads(data)

data = data['changelog']
data = data[1:]
box_dict = {}

#first slide id is 'p'
box_dict['i0'] = {'slide': 'p', 'string': ''}
box_dict['i1'] = {'slide': 'p', 'string': ''}
slide_dict = {'p': ['i0', 'i1']}
#keep order of slides
slide_list = ['p']

def add_text(line):
    box_dest = line[1]
    add_string = line[4]
    index = line[3]
    old_string = box_dict[box_dest]['string']
    new_string = insert(old_string, add_string, index)
    box_dict[box_dest]['string'] = new_string

def add_box(line):
    box_attrib = {}
    slide = line[5]
    box_id = line[1]
    box_attrib['slide'] = slide
    box_attrib['string'] = ''
    box_dict[box_id] = box_attrib

    if slide in slide_dict:
        slide_dict[slide].append(box_id)
    else:
        slide_dict[slide] = [box_id]

def del_text(line):
    box_dest = line[1]
    start_i = line[3]
    end_i = line[4]
    old_string = box_dict[box_dest]['string']
    new_string = delete(old_string, start_i, end_i)
    box_dict[box_dest]['string'] = new_string

def parse_mts(data):
    action_list = data[1]
    for line in action_list:
        parse(line)
        
def add_slide(line):
    print 'add slide:', line
    i = line[2]
    slide_id = line[1]
    slide_list.insert(i, slide_id)
    
    if not slide_id in slide_dict:
        slide_dict[slide_id] = []
    
    
def del_box(line):
    for box in line[1]:
        try:
            parent = box_dict['slide']
            del box_dict[box]
            slide_dict['slide'].remove(box)
        except:
            print "key error deleting", box, 'in line = ', line
        
def del_slide(line):
    print 'del', line
    i = line[1]
    if line[4] == slide_list[i]:
        slide_list.pop(i)
    
functions = {15: add_text, 4:parse_mts, 16:del_text, 3:add_box,
             12:add_slide, 13:del_slide, 0:del_box}

def insert(old, add, i):
    return old[:i] + add + old[i:]

def delete(old, si, ei):
    si = si 
    return old[:si] + old[ei:]

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

def makedir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

based = 'oslide/'
makedir(based)
for i,slide in enumerate(slide_list):
    slidei = 'slide' + str(i) 
    path = based + slidei + '/'
    print path
    makedir(path)
    for j,box in enumerate(slide_dict[slide]):
        filename = path + slidei + '_' + 'box' + str(j) + '.txt'
        print filename
        with open(filename, 'w') as ofile:
            ofile.write(box_dict[box]['string'])
            
