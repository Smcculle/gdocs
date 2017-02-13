#! /usr/bin/python2.7

# comments API
# https://www.googleapis.com/drive/v3/files/1-x74jkh4s5LEJLWqKUNcV_9EMQjQ4Gm4sV4YVJy9FJo
#                                             /comments?fields=comments(anchor, content)
# &includeDeleted=true for metadata on deleted comments

import ConfigParser
import argparse
import json
import os
import sys
import urllib
from collections import namedtuple

import httplib2
from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow, _CLIENT_SECRETS_MESSAGE, argparser as oargparser

import csv2plain
import log2csv
import slide2plain

# TODO:  video slide inserts

DRAW_PATH = 'https://docs.google.com/drawings/d/{d_id}/image?w={w}&h={h}'
REV_URL = 'https://docs.google.com/{drive}/d/{file_id}/revisions/load?id={file_id}' \
          '&start={start}&end={end}'
RENDER_URL = 'https://docs.google.com/{drive}/d/{file_id}/renderdata?id={file_id}'
DRIVE_TYPE = {0: 'document', 1: 'presentation'}
TITLE_PATH = 'https://www.googleapis.com/drive/v2/files/{file_id}?fields=title'
DRIVE = ''


def list_files(service, drive_type):
    """ Lists files from the appropriate drive account"""

    search_param = {'document': "mimeType = 'application/vnd.google-apps.document'",
                    'presentation': "mimeType = 'application/vnd.google-apps.presentation'"}
    files = service.files().list(q=search_param[drive_type]).execute()
    return files['items']


def choose_file(service, drive_type):
    files = list_files(service, drive_type)
    print '\nChoose a file from the list below'
    for i, file_ in enumerate(files):
        print '{}: \t{}'.format(i, file_['title'])

    choice, file_id = None, None
    while choice is None:
        try:
            choice = int(raw_input('\nChoose a file:  '))
            file_id = files[choice]['id']
        except KeyError:
            print('invalid choice')
            choice = None

    print 'Chose file {}'.format(files[choice]['title'])

    revisions = service.revisions().list(fileId=file_id).execute()
    max_rev = revisions['items'][-1]['id']
    return str(file_id), max_rev


def create_url(file_id, start, end):
    """Constructs URL to retrieve the changelog using google file ID, start/end revision number"""

    return REV_URL.format(file_id=file_id, start=start, end=end, drive=DRIVE)


def get_title(service, file_id):
    """Gets the title associated with supplied google file_id"""
    url = TITLE_PATH.format(file_id=file_id)
    response, content = service._http.request(url)
    return json.loads(content)['title']


def start_service():
    """Reads config file and initializes the gdrive service with proper authentication"""

    config = ConfigParser.ConfigParser()
    config.read('config/config.cfg')
    tokens = config.get('gdrive', 'tokenfile')

    # CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
    # application, including client_id and client_secret, which are found
    # on the API Access tab on the Google APIs
    # Console <http://code.google.com/apis/console>
    client_secrets = config.get('gdrive', 'configurationfile')

    missing_client_secrets_message = _CLIENT_SECRETS_MESSAGE % os.path.join(
        os.path.dirname(__file__), client_secrets)

    flow = flow_from_clientsecrets(client_secrets,
                                   scope='https://www.googleapis.com/auth/drive',
                                   message=missing_client_secrets_message)

    storage = Storage(tokens)
    credentials = storage.get()
    # run_flow requires a wrapped tools.argparse object to handle command line arguments
    flags = argparse.ArgumentParser(parents=[oargparser]).parse_args()
    if credentials is None:  # or credentials.invalid:
        credentials = run_flow(flow, storage, flags)
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = build("drive", "v2", http=http)
    return service


def get_drawings(drawing_ids, service, file_id):
    drawings = []
    for drawing_id in drawing_ids:
        # url = DRAW_PATH.format(d_id=drawing_id[0], w=drawing_id[1], h=drawing_id[2])
        url = DRAW_PATH.format(d_id=drawing_id.d_id, w=drawing_id.width, h=drawing_id.height)
        response, content = service._http.request(url)
        extension = get_extension(response)
        drawings.append((content, extension))

    return drawings


def get_render_request(image_ids, file_id):
    """ Returns url request to retrieve images with image_ids contained in file with file_id"""
    image_ids = set(image_ids)
    data = {}
    for i, img_id in enumerate(image_ids):
        key = 'r' + str(i)
        # unicode image_ids are not accepted in the request, so they must be encoded as strings
        data[key] = ['image', {'cosmoId': img_id.encode(), 'container': file_id}]
    request_body = urllib.urlencode({'renderOps': data}).replace('+', '')
    my_headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}

    render_url = RENDER_URL.format(drive=DRIVE, file_id=file_id)

    return render_url, request_body, my_headers


def get_image_links(image_ids, service, file_id):
    """ Sends url request to google API which returns a link for each image resource, returns
    dictionary of tuples containing those links along with each image_id associated with link"""
    render_url, request_body, my_headers = get_render_request(image_ids, file_id)
    try:
        response, content = service._http.request(render_url, method='POST',
                                                  body=request_body, headers=my_headers)
        content = json.loads(content[5:])
        # keep assocation of image ids with image
        for i, img_id in enumerate(image_ids):
            key = 'r' + str(i)
            content[key] = (content.pop(key), img_id)
        return content
    except:
        print 'Unable to retrieve image resources'


def get_extension(html_response):
    """Returns extension for downloaded resource"""

    cdisp = html_response['content-disposition']
    start_index = cdisp.index('.')
    end_index = cdisp.index('"', start_index)
    extension = cdisp[start_index:end_index]
    return extension


def get_images(image_ids, service, file_id):
    """ Gets a list of links and resolves each one, returning a list of tuples containing
    (image, extension, img_id) for each image resource"""
    images = []
    links = get_image_links(image_ids, service, file_id)
    for url, img_id in links.itervalues():
        response, content = service._http.request(url)
        extension = get_extension(response)
        images.append((content, extension, img_id))

    return images


def get_comments(comment_anchors, service, file_id):
    """ Gets comments and replies to those comments.  Deleted comments show up as blank"""
    url = ''.join(('https://www.googleapis.com/drive/v2/files/',
                   file_id,
                   r'/comments?includeDeleted=true'
                   r'&fields=items(anchor%2Ccontent%2Creplies%2Fcontent)'))
    response, content = service._http.request(url)
    content = json.loads(content)
    comment_anchors = set(comment_anchors)

    comments = []
    for item in content['items']:
        if item['anchor'] in comment_anchors:
            comment = 'Comment: %s\n' % item['content']
            comments.append(comment)
            if item['replies']:
                for reply in item['replies']:
                    reply = '\t%s\n' % reply['content']
                    comments.append(reply)

    return comments


def get_doc_objects(flat_log):
    """
    Discovers objects from flat_log in a single pass.
    :param flat_log: preprocessed version of google changelog
    :return: list of comment_anchors, image_ids, drawing_ids, and a suggestions dictionary
    """
    # TODO break into one section for each object type and parallelize
    comment_anchors = []
    image_ids = set()
    drawing_ids = []
    drawing = namedtuple('drawing', 'd_id width height')
    suggestions = {}

    for line in flat_log:
        try:
            i = line.index('{')
            line_dict = json.loads(line[i:])
            if 'style_type' in line_dict:
                if line_dict['style_type'] == 'doco_anchor':  # comment anchor
                    c_id = line_dict['style_mod']['datasheet_anchor']['cv']['opValue']
                    if c_id:
                        comment_anchors += c_id if type(c_id) == list else [c_id]
                elif 'datasheet_anchor' in line_dict:  # data anchor for comment
                    c_id = line_dict['datasheet_anchor']['cv']['opValue']
                    if c_id:
                        comment_anchors += c_id if type(c_id) == list else [c_id]
            elif 'epm' in line_dict and 'ee_eo' in line_dict['epm']:
                if 'img_cosmoId' in line_dict['epm']['ee_eo']:  # image located
                    image_ids.add(line_dict['epm']['ee_eo']['img_cosmoId'])
                elif 'd_id' in line_dict['epm']['ee_eo']:  # drawing located
                    mod_add_drawing(drawing, drawing_ids, line_dict)
            elif 'type' in line_dict:
                if line_dict['type'] == 'iss':  # suggestions located
                    mod_insert_suggestion(line_dict, suggestions)
                elif line_dict['type'] == 'dss' and 'sug_id' in line_dict:
                    mod_delete_suggestion(line_dict, suggestions)

        except ValueError:
            pass  # either chunked or changelog header without dict, no action needed

    return comment_anchors, image_ids, drawing_ids, suggestions


def mod_add_drawing(drawing, drawing_ids, line_dict):
    """ Modifies drawing_ids to add a drawing namedtuple containing id, width, and height """
    d_id = line_dict['epm']['ee_eo']['d_id']
    img_wth = line_dict['epm']['ee_eo']['img_wth']
    img_ht = line_dict['epm']['ee_eo']['img_ht']
    drawing_ids.append(drawing(d_id, int(img_wth), int(img_ht)))


def mod_delete_suggestion(line_dict, suggestions):
    """ Modifies suggestions to delete text from the given suggestion from start to end index"""
    start_index = line_dict['start_index']
    end_index = line_dict['end_index']
    try:
        sug_id = line_dict['sug_id']
    except KeyError:
        print "key error in sugid"
        print line_dict
        sys.exit(2)

    # remove later#
    if sug_id not in suggestions:
        print 'Trying to delete suggestion that does not exist'
        raise
    suggestions[sug_id] = csv2plain.delete(suggestions[sug_id],
                                           start_index, end_index)


def mod_insert_suggestion(line_dict, suggestions):
    """ Modifies suggestions to add text to a given suggestion at index"""
    sug_id = line_dict['sug_id']
    ins_index = line_dict['ins_index']
    string = line_dict['string']

    # check if suggestion exists, create otherwise
    if sug_id in suggestions:
        suggestions[sug_id] = csv2plain.insert(suggestions[sug_id],
                                               string, ins_index)
    else:
        suggestions[sug_id] = string


def process_doc(log, service, file_id, start, end):
    """ Using google changelog, retrieves comments, suggestions, images, and drawings
    associated with that log and sends them to be outputted.  """
    flat_log = log2csv.get_flat_log(log)
    comment_anchors, image_ids, drawing_ids, suggestions = get_doc_objects(flat_log)
    plain_text = csv2plain.parse_log(flat_log)

    comments = get_comments(comment_anchors, service, file_id)
    images = get_images(image_ids, service, file_id)
    drawings = get_drawings(drawing_ids, service, file_id)
    docname = get_title(service, file_id)

    write_doc(docname, plain_text, comments, images, drawings, start, end, suggestions)


# refactor for list(**args)
def write_doc(docname, plain_text, comments, images, drawings, start, end, suggestions):
    """ Writes all document objects retrieved from the log """
    base_dir = './downloaded/gdocs/{}_{}-{}/'.format(docname, str(start), str(end))
    slide2plain.makedir(base_dir)

    for i, drawing in enumerate(drawings):
        filename = base_dir + 'drawing' + str(i) + drawing[1]
        with open(filename, 'wb') as f:
            f.write(drawing[0])

    for i, img in enumerate(images):
        filename = base_dir + 'img' + str(i) + img[1]
        with open(filename, 'wb') as f:
            f.write(img[0])

    filename = base_dir + 'plain.txt'
    with open(filename, 'w') as f:
        f.write(plain_text.encode('utf-8'))

    filename = base_dir + 'comments.txt'
    with open(filename, 'w') as f:
        f.write(''.join(comments))

    filename = base_dir + 'suggestions.txt'
    with open(filename, 'w') as f:
        f.write(json.dumps(suggestions))

    print 'Finished with output in directory', base_dir


def get_slide_objects(log):
    """ Gets objects(only images for now) associated with slide from the log"""
    image_ids = {}
    for line in log['changelog']:
        # line[0][0] is action type, 4 is multiset, 44 is insert image action
        # for video inserts, len...[4] is 18; exclude video inserts for now
        if line[0][0] == 4 and line[0][1][1][0] == 44 and len(line[0][1][0][4]) != 18:
            # for drive,personal upload, image id in ...[9], else if url in ...[11]
            slide_id = line[0][1][0][5]
            # if ..[11] is a list, the image was not uploaded via url
            if type(line[0][1][0][4][11]) == list:
                # if ..[9] is a list, not uploaded by drive
                if type(line[0][1][0][4][9]) == list:
                    image_id = line[0][1][0][4][7]
                else:
                    image_id = line[0][1][0][4][9]
            else:
                # if 11 is not a list, it was uploaded by url, src in ...[9]
                image_id = line[0][1][0][4][11]

            # image_ids[slide_id].append(image_id)
            image_ids[image_id] = slide_id
    return image_ids


def process_slide(log, service, file_id, start, end):
    """ Processing for slides to retrieve all iamges and plain text from every box in each slide,
    outputs to a directory with a folder for each slide"""
    image_ids = get_slide_objects(log)
    images = get_images(image_ids.keys(), service, file_id)

    # index images by slide for printing
    slide_images = {}
    for img in images:
        slide_id = image_ids.pop(img[2])
        if slide_id in slide_images:
            slide_images[slide_id].append(img)
        else:
            slide_images[slide_id] = [img]

    path = './downloaded/gslide/{}_{}-{}/'.format(get_title(service, file_id), str(start), str(end))
    slide2plain.write_objects(log, slide_images, path)


def main():
    print 'Downloads the plain-text as of end revision as well as the images and comments ' \
          'associated with the file, even deleted images. \n*Presentations only support starting ' \
          'from revision 1.  \n\n'
    global DRIVE

    choice = None
    while choice is None:
        try:
            choice = int(raw_input('Enter ' + ', '.join(
                '{} for {}'.format(index, service)
                for index, service in DRIVE_TYPE.iteritems()) + ': '))
            try:
                DRIVE = DRIVE_TYPE[choice]
            except KeyError:
                raise
        except (ValueError, KeyError):
            print('invalid choice\n')
            choice = None

    service = start_service()
    file_id, max_revs = choose_file(service, drive_type=DRIVE)
    start, end = 0, 0
    max_revs = int(max_revs)
    while start < 1 or start >= max_revs:
        try:
            start = int(raw_input("Start from revision(max {}): ".format(max_revs)))
            if start < 1 or start >= max_revs:
                raise ValueError
        except ValueError:
            print("invalid revision choice\n")

    while end == 0 or end > max_revs:
        try:
            end = int(raw_input("End at revision(max {}): ".format(max_revs)))
            if end == 0 or end > max_revs:
                raise ValueError
        except ValueError:
            print("invalid revision choice\n")

    url = create_url(file_id, start, end)
    response, log = service._http.request(url)
    if response['status'] != '200':
        print 'Could not obtain log.  Check file_id, max revision number, and permission for file.'
        sys.exit(2)

    log = json.loads(log[5:])
    if type(log['changelog'][0][0]) == dict:
        process_doc(log, service, file_id, start, end)
    elif type(log['changelog'][0][0]) == list:
        process_slide(log, service, file_id, start, end)
    else:
        raise ValueError('Unexpected type %s in changelog' % type(log['changelog'][0][0]))


if __name__ == '__main__':
    main()
