"""Usage: python slide2plain.py <inputfile> [output_dir]. Takes single raw changelog from slides.
Ex: \tpython slide2plain.py slogs/1_317.txt.  Outputs a directory named oslide/ by default
containing a folder for each slide page"""

import os
import sys
import json
import errno


# todo:better solution to slide/box dict, clean

BASE_DIR = 'oslide/'
box_dict = {}
slide_dict = {'p': ['i0', 'i1']}
# keep order of slides
slide_list = ['p']


def add_text(line):
    """ Adds a string to a given box at the given index """
    box_dest = line[1]
    add_string = line[4]
    index = line[3]
    old_string = box_dict[box_dest]['string']
    new_string = insert(old_string, add_string, index)
    box_dict[box_dest]['string'] = new_string


def add_box(line):
    """ Adds a new box to the collection of boxes"""
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
    """ Deletes the given range from the string at the given box """
    box_dest = line[1]
    start_i = line[3]
    end_i = line[4]
    old_string = box_dict[box_dest]['string']
    new_string = delete(old_string, start_i, end_i)
    box_dict[box_dest]['string'] = new_string


def parse_mts(data):
    """ Parse each line entry separately in the multiset """
    action_list = data[1]
    for line in action_list:
        parse_line(line)


def add_slide(line):
    """ Adds a slide and slide id to the collection """
    i = line[2]
    slide_id = line[1]
    slide_list.insert(i, slide_id)

    if slide_id not in slide_dict:
        slide_dict[slide_id] = []


def del_box(line):
    """ Deletes a box from the given slide """
    for box in line[1]:
        try:
            parent = box_dict['slide']
            del box_dict[box]
            slide_dict['slide'].remove(box)
        except:
            "key error deleting", box, 'in line = ', line


def del_slide(line):
    """ Deletes a slide given the ID and location """
    i = line[1]
    if line[4] == slide_list[i]:
        slide_list.pop(i)


def insert(old, add, i):
    """ Returns a new string with the added portion inserted at index i """
    return old[:i] + add + old[i:]


def delete(old, start, end):
    """ Returns a new string with the portion deleted from si to ei """
    return old[:start] + old[end:]


def parse(data):
    """ Takes the raw log and creates the first two boxes, and sends each line to be parsed """
    # first slide id is 'p'
    box_dict['i0'] = {'slide': 'p', 'string': ''}
    box_dict['i1'] = {'slide': 'p', 'string': ''}
    for entry in data:
        line = entry[0]
        parse_line(line)


def parse_line(line):
    """ Given a line in the log, calls a function based on the appropriate action listed in line """
    functions = {15: add_text, 4: parse_mts, 16: del_text, 3: add_box,
                 12: add_slide, 13: del_slide, 0: del_box}
    action = line[0]
    if action in functions:
        func = functions[action]
        func(line)


def makedir(path):
    """ Attempts to make a directory and raises exception if there is an issue"""
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:  # raise if the error is other than already exists
            raise


def write_output(box_dict, slide_dict, slide_list, images=None, base_dir=BASE_DIR):
    """ Write the output to the base_dir, with each slide having a folder containing all
    boxes with plaintext and images """
    makedir(base_dir)
    for i, slide in enumerate(slide_list):
        slidei = 'slide' + str(i)
        path = base_dir + slidei + '/'
        makedir(path)
        for j, box in enumerate(slide_dict[slide]):
            if box_dict[box]['string']:
                filename = path + slidei + '_' + 'box' + str(j) + '.txt'
                with open(filename, 'w') as ofile:
                    ofile.write(box_dict[box]['string'])
        if images and slide in images:
            for j, img in enumerate(images[slide]):
                extension = img[1]
                filename = path + slidei + '_' + 'image' + str(j) + extension
                with open(filename, 'wb') as ofile:
                    ofile.write(img[0])

    print 'Finished with output in directory', base_dir


def write_objects(log, images, path):
    """ Used by outside program to process a given log and set of images to output"""
    log = log['changelog']
    log = log[1:]
    parse(log)
    write_output(box_dict, slide_dict, slide_list, images=images, base_dir=path)


def main(argv):
    if not argv:
        print __doc__
        sys.exit(2)
    else:
        filename = argv[0]
        if len(argv) == 2:
            base_dir = argv[1]
            if base_dir[-1] != '/':
                base_dir += '/'
        elif len(argv) == 1:
            base_dir = BASE_DIR
        else:
            print __doc__
            sys.exit("Incorrect arguments")

    print argv
    raw_input('wait...')

    if not os.path.isfile(filename):
        print 'No file found. ', __doc__
        sys.exit(2)

    with open(filename, 'r') as f:
        data = f.read()
    if data[0] == ')':  # remove extra padding at start of file
        data = data[5:]

    data = json.loads(data)

    data = data['changelog'][1:]
    del data[0]
    parse(data)
    write_output(box_dict, slide_dict, slide_list, base_dir=base_dir)


if __name__ == '__main__':
    main(sys.argv[1:])
