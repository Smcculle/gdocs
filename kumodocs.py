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
from collections import defaultdict
from collections import namedtuple

import httplib2
from googleapiclient.discovery import build
from googleapiclient import errors
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow, _CLIENT_SECRETS_MESSAGE, argparser as oargparser


import csv2plain
import log2csv
import misc.gdoc_utils as gdoc_utils
import slide2plain

DRAW_PATH = 'https://docs.google.com/drawings/d/{d_id}/image?w={w}&h={h}'
REV_URL = 'https://docs.google.com/{drive}/d/{file_id}/revisions/load?id={file_id}' \
          '&start={start}&end={end}'
RENDER_URL = 'https://docs.google.com/{drive}/d/{file_id}/renderdata?id={file_id}'
# DRIVE_TYPE = {0: 'document', 1: 'presentation'}
TITLE_PATH = 'https://www.googleapis.com/drive/v2/files/{file_id}?fields=title'
MIME_TYPE = "mimeType = 'application/vnd.google-apps.{}'"
SERVICES = ['document', 'drawing', 'form', 'presentation', 'spreadsheet']
Suggestion = namedtuple('Suggestion', 'start, end, sug_id, content deleted')
Drawing = namedtuple('Drawing', 'd_id width height')

'https://docs.google.com/drawings/d/1D5U_nYaUrXY-kuw246hECQSc-wE0kCL2A6Xao1YVY9U/'
'https://docs.google.com/spreadsheets/d/1zzz4ZE6tIBvood5XAKgtXsg_lBFBdqoQvoZwPHLU1v8/'
'https://docs.google.com/forms/d/1NRiR4gTFL1C-opeczrshrD_o_Qv1tfBPgYDft8OQZQk/'

# TODO:  video slide inserts, refactor into generic kumodocs with gdocs driver
# TODO: add suggestion class to gdocs driver with associated functionality
# TODO: create abstract base class to inherit driver modules from
# TODO ** namedtuple for file to replace file_id containing file_id, drive type  mod strip path ext to return path, titl
# TODO *** solve forms auth issue, sheets revision=1

def list_files(service, drive_type):
    """ Lists files from the appropriate drive account"""

    # search_param = {'document': "mimeType = 'application/vnd.google-apps.document'",
    #                 'presentation': "mimeType = 'application/vnd.google-apps.presentation'"}

    files = service.files().list(q=MIME_TYPE.format(drive_type), fields='items(title, id)').execute()
    return files['items']


def list_all_files(service):
    """Retrieve a list of File resources.

     Args:
       service: Drive API service instance.
     Returns:
       List of File resources.
     """

    result = defaultdict(list)
    page_token = None
    for drive_type in SERVICES:
        while True:
            try:
                param = {'q': MIME_TYPE.format(drive_type),
                         'fields': 'items(title, id)'}
                if page_token:
                    param['pageToken'] = page_token
                files = service.files().list(**param).execute()

                result[drive_type].extend(files['items'])
                page_token = files.get('nextPageToken')
                if not page_token:
                    break
            except errors.HttpError, error:
                print 'An error occurred: %s' % error
                break
    return result


def choose_file(service, drive_type):
    files = list_all_files(service)

    with gdoc_utils.temp_directory() as temp_dir:
        _create_temp_files(temp_dir, files)
        options = {'title': 'Choose a G Suite file', 'initialdir': temp_dir}
        choice = gdoc_utils.choose_file_dialog(**options)
        try:
            file_id = choice.read()
        except AttributeError:
            print 'No file chosen. Exiting.'
            sys.exit(1)
        except IOError:
            print 'Error reading file. Exiting'
            sys.exit(2)
        else:
            choice.close()
            title = choice.name
            print 'Chose file: {}'.format(gdoc_utils.strip_path_extension(title))

    revisions = service.revisions().list(fileId=file_id, fields='items(id)').execute()
    max_rev = revisions['items'][-1]['id']

    return str(file_id), title, max_rev


def _create_temp_files(temp_dir, files):
    """ Creates a directory of empty temporary files for virtualization of drive contents """

    for drive_type, drive_files in files.items():
        folder_path = os.path.join(temp_dir, drive_type + '/')
        os.mkdir(folder_path)
        for file_ in drive_files:
            # replace reserved characters in title to assure valid filename
            filename = gdoc_utils.strip_invalid_characters(file_['title'])
            filename = '{}.{}'.format(os.path.join(temp_dir, folder_path, filename), drive_type)
            with open(filename, 'w') as f:
                f.write(file_['id'])


def create_url(file_id, drive, start, end):
    """Constructs URL to retrieve the changelog using google file ID, start/end revision number"""

    return REV_URL.format(file_id=file_id, start=start, end=end, drive=drive)


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
        os.path.dirname(os.path.realpath(__file__)), client_secrets)

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
        extension = gdoc_utils.get_download_ext(response)
        drawings.append((content, extension))

    return drawings


def get_render_request(image_ids, file_id, drive):
    """ Returns url request to retrieve images with image_ids contained in file with file_id"""
    image_ids = set(image_ids)
    data = {}
    for i, img_id in enumerate(image_ids):
        key = 'r' + str(i)
        # unicode image_ids are not accepted in the request, so they must be encoded as strings
        data[key] = ['image', {'cosmoId': img_id.encode(), 'container': file_id}]
    request_body = urllib.urlencode({'renderOps': data}).replace('+', '')
    my_headers = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'}

    render_url = RENDER_URL.format(drive=drive, file_id=file_id)

    return render_url, request_body, my_headers


def get_image_links(image_ids, service, file_id, drive):
    """ Sends url request to google API which returns a link for each image resource, returns
    dictionary of tuples containing those links along with each image_id associated with link"""
    render_url, request_body, my_headers = get_render_request(image_ids, file_id, drive)
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


def get_images(image_ids, service, file_id, drive):
    """ Gets a list of links and resolves each one, returning a list of tuples containing
    (image, extension, img_id) for each image resource"""
    images = []
    links = get_image_links(image_ids, service, file_id, drive)
    for url, img_id in links.itervalues():
        response, content = service._http.request(url)
        extension = gdoc_utils.get_download_ext(response)
        images.append((content, extension, img_id))

    return images


def get_comments(service, file_id):
    """ Gets comments and replies to those comments, and metadata for deleted comments """

    reply_fields = 'author, content, createdDate, modifiedDate, deleted'
    comment_fields = 'items(status, author, content, createdDate, modifiedDate, deleted, ' \
                     'replies({}))'.format(reply_fields)

    # output templates for comments and replies
    comment_template = '{num}. comment: {content} \nauthor: {author[displayName]}, ' \
                       'status: {status}, created: {createdDate}, modified: {modifiedDate}, ' \
                       'deleted: {deleted} \nreplies:'
    reply_template = '\n\t({num}) reply: {content} \n\tauthor: {author[displayName]}, ' \
                     'created: {createdDate}, modified: {modifiedDate}, deleted: {deleted}'

    contents = service.comments().list(fileId=file_id, includeDeleted=True,
                                       fields=comment_fields).execute()
    contents = contents['items']

    comments = []
    for i, comment in enumerate(contents):
        comment['num'] = i + 1
        comments.append(comment_template.format(**comment))
        for j, reply in enumerate(comment['replies']):
            reply['num'] = j + 1
            comments.append(reply_template.format(**reply))
        comments.append('\n\n')
    return comments


def get_doc_objects(flat_log):
    """
    Discovers objects from flat_log in a single pass.
    :param flat_log: preprocessed version of google changelog
    :return: list of comment_anchors, image_ids, drawing_ids, and a suggestions dictionary
    """
    # TODO break into one section for each object type and parallelize
    image_ids = set()
    drawing_ids = []
    suggestions = {}

    for line in flat_log:
        try:
            i = line.index('{')
            line_dict = json.loads(line[i:])
        except ValueError:
            pass  # either chunked or changelog header without dict, no action needed
        else:
            if has_element(line_dict):
                elem_dict = line_dict['epm']['ee_eo']
                if has_img(elem_dict):
                    image_ids.add(elem_dict['img_cosmoId'])
                elif has_drawing(elem_dict, drawing_ids):
                    drawing_ids.append(new_drawing(elem_dict))
            elif 'type' in line_dict:
                if is_insert_suggestion(line_dict):
                    sug_id = line_dict['sug_id']
                    if sug_id in suggestions:
                        suggestions[sug_id] = ins_sugg_text(line_dict, suggestions[sug_id])
                    else:
                        suggestions[sug_id] = new_suggestion(line_dict)
                elif is_delete_suggestion(line_dict):
                    suggestion = find_sugg_by_index(line_dict, suggestions)
                    if suggestion:
                        suggestions[suggestion.sug_id] = rm_sugg_text(line_dict, suggestion)

    return image_ids, drawing_ids, suggestions


def is_insert_suggestion(line_dict):
    return line_dict['type'] == 'iss'


def is_delete_suggestion(line_dict):
    return line_dict['type'] == 'dss'


def has_drawing(elem_dict, drawing_ids):
    """ True if elem_dict has drawing not contained in drawing_ids already """
    return 'd_id' in elem_dict and not any(d for d in drawing_ids if d.d_id == elem_dict['d_id'])


def has_element(line_dict):
    return 'epm' in line_dict and 'ee_eo' in line_dict['epm']


def has_img(elem_dict):
    return 'img_cosmoId' in elem_dict


def new_drawing(elem_dict):
    """ Returns a new Drawing namedtuple containing id, width, and height """
    drawing_keys = ('d_id', 'img_wth', 'img_ht')
    d_id, img_wth, img_ht = (elem_dict[key] for key in drawing_keys)
    return Drawing(d_id, int(img_wth), int(img_ht))


def new_drawing_old(line_dict):
    """ Returns a new Drawing namedtuple containing id, width, and height """
    d_id = line_dict['epm']['ee_eo']['d_id']
    img_wth = line_dict['epm']['ee_eo']['img_wth']
    img_ht = line_dict['epm']['ee_eo']['img_ht']
    return Drawing(d_id, int(img_wth), int(img_ht))


def new_suggestion(line_dict):
    """ Returns a new Suggestion with sug_id, content, start index, end index, deleted chars"""
    sug_id, content, start = line_dict['sug_id'], line_dict['string'], line_dict['ins_index']
    end = start + len(content) - 1
    return Suggestion(sug_id=sug_id, content=content, start=start, end=end, deleted=[])


def ins_sugg_text(line_dict, old_sugg):
    """ Returns new Suggestion with text inserted at the appropriate index """
    relative_index = line_dict['ins_index'] - old_sugg.start + 1  # index start @1 in log
    new_text = csv2plain.insert(old_string=old_sugg.content, new_string=line_dict['string'],
                                index=relative_index)
    return Suggestion(sug_id=old_sugg.sug_id, content=new_text, start=old_sugg.start,
                      end=old_sugg.end + len(line_dict['string']), deleted=old_sugg.deleted)


def rm_sugg_text(line_dict, suggestion):
    """ Returns new Suggestion with all deleted_chr appended to delete and removed from content """
    # normalize indices
    rm_start = line_dict['start_index'] - suggestion.start
    rm_end = line_dict['end_index'] - suggestion.start + 1

    deleted_chr = suggestion.content[rm_start:rm_end]
    new_content = suggestion.content[:rm_start] + suggestion.content[rm_end:]
    new_end = suggestion.end - len(deleted_chr)
    suggestion.deleted.append(deleted_chr)

    return Suggestion(sug_id=suggestion.sug_id, start=suggestion.start, end=new_end,
                      content=new_content, deleted=suggestion.deleted)


def find_sugg_by_index(line_dict, suggestions):
    """ Searches for Suggestion that contains start_index in its [start,end] range """
    suggestion = [s for s in suggestions.values() if s.start <= line_dict['start_index'] <= s.end]
    if len(suggestion) == 1:
        return suggestion[0]
    elif len(suggestion) > 1:
        print('too many suggestions')
        return suggestion[0]
    else:
        print('could not find suggestion')
        print('line dict=', line_dict)
        print('suggestions=', suggestions)
        return None


def process_doc(log, service, file_id, start, end, drive):
    """ Using google changelog, retrieves comments, suggestions, images, and drawings
    associated with that log and sends them to be outputted.  """
    flat_log = log2csv.get_flat_log(log)
    image_ids, drawing_ids, suggestions = get_doc_objects(flat_log)
    plain_text = csv2plain.parse_log(flat_log)

    comments = get_comments(service, file_id)
    images = get_images(image_ids, service, file_id, drive)
    drawings = get_drawings(drawing_ids, service, file_id)
    docname = get_title(service, file_id)

    write_doc(docname, plain_text, comments, images, drawings, start, end, suggestions, log, flat_log)


# refactor for list(**args)
def write_doc(docname, plain_text, comments, images, drawings, start, end, suggestions, log, flat_log):
    """ Writes all document objects retrieved from the log """
    base_dir = './downloaded/document/{}_{}-{}/'.format(docname, str(start), str(end))
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
        f.write('\n'.join(str(line) for line in comments))

    filename = base_dir + 'suggestions.txt'
    with open(filename, 'w') as f:
        f.write(json.dumps(suggestions, ensure_ascii=False))

    filename = base_dir + 'revision-log.txt'
    with open(filename, 'w') as f:
        f.write('chunkedSnapshot')
        for line in log['chunkedSnapshot']:
            f.write(str(line) + '\n')
        f.write('changelog')
        for line in log['changelog']:
            f.write(str(line) + '\n')

    filename = base_dir + 'flat-log.txt'
    with open(filename, 'w') as f:
        for line in flat_log:
            f.write(line + '\n')

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


def process_slide(log, service, file_id, start, end, drive):
    """ Processing for slides to retrieve all iamges and plain text from every box in each slide,
    outputs to a directory with a folder for each slide"""
    image_ids = get_slide_objects(log)
    images = get_images(image_ids.keys(), service, file_id, drive)

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


def write_other(log, drive, max_revs, title):
    base_dir = './downloaded/{}/{}_1-{}/'.format(drive, title, str(max_revs))
    gdoc_utils.ensure_path(base_dir)



def split_title(title):
    ext_index = title.rfind('.')
    drive = title[ext_index+1:]
    title = gdoc_utils.strip_path_extension(title[:ext_index])
    if drive in ['drawing', 'form', 'spreadsheet']:
        drive += 's'
        print('drive is now', drive)
    return title, drive


def main():
    print 'Downloads the plain-text as of end revision as well as the images and comments ' \
          'associated with the file, even deleted images. \n*Presentations only support starting ' \
          'from revision 1.  \n\n'

    # choice = None
    # while choice is None:
    #     try:
    #         choice = int(raw_input('Enter ' + ', '.join(
    #             '{} for {}'.format(index, service)
    #             for index, service in DRIVE_TYPE.iteritems()) + ': '))
    #         try:
    #             DRIVE = DRIVE_TYPE[choice]
    #         except KeyError:
    #             raise
    #     except (ValueError, KeyError):
    #         print('invalid choice\n')
    #         choice = None
    print('Starting the Drive service and retrieving files, please wait...')
    service = start_service()
    file_id, title, max_revs = choose_file(service, None)
    title, drive = split_title(title)
    print(file_id)
    print(title)
    print(drive)
    print(max_revs)
    start, end = 0, 0
    max_revs = int(max_revs)
    if drive != 'document':
        start, end = 1, max_revs
    elif drive == 'spreadsheet':
        print('unsupported service')
        sys.exit(2)
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

    url = create_url(file_id, drive, start, end)
    response, log = service._http.request(url)
    if response['status'] != '200':
        print 'Could not obtain log.  Check file_id, max revision number, and permission for file.'
        sys.exit(2)

    try:
        log = json.loads(log[5:])
    except ValueError:
        write_other(log=log, drive=drive, max_revs=max_revs, title=title)
    else:
        if drive == 'document':
            process_doc(log, service, file_id, start, end, drive)
        #if type(log['changelog'][0][0]) == dict:

        elif drive == 'presentation': #type(log['changelog'][0][0]) == list:
            process_slide(log, service, file_id, start, end, drive)
        else:
            write_other(log=log, drive=drive, max_revs=max_revs, title=title)
        # raise ValueError('Unexpected type %s in changelog' % type(log['changelog'][0][0]))


if __name__ == '__main__':
    main()
