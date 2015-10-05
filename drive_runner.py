import ConfigParser, urllib2, os, httplib2, sys, urllib, json

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError, flow_from_clientsecrets
#***requires oauth2client version 1.3.2***
from oauth2client.tools import run

import log2csv
import csv2plain
import slide2plain

#**TODO:  video slide inserts

fid = '1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps'
#url = 'https://docs.google.com/document/d/1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps/revisions/load?id=1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps&start=254&end=276'#&token=AC4w5ViipiO5sN96CUai4LMfK9VWsbLltw%3A1443027271527'
BASE_URL = 'https://docs.google.com/document/d/'
REV_PATH = '/revisions/load?id='
RENDER_PATH = '/renderdata?id='
DRAW_PATH = 'https://docs.google.com/drawings/d/{d_id}/image?w={w}&h={h}'
REV_URL = 'https://docs.google.com/{drive}/d/{file_id}/revisions/load?id={file_id}'\
          '&start={start}&end={end}'
DRIVE_TYPE = {0: 'document', 1: 'presentation'}
TITLE_PATH = 'https://www.googleapis.com/drive/v2/files/{file_id}?fields=title'

def get_user_info(service):
  """Print information about the user along with the Drive API settings.

  Args:
    service: Drive API service instance.
  """
  try:
    about = service.about().get().execute()

    return about
  except errors.HttpError, error:
    print 'An error occurred: %s' % error
    return None

def list_files(key):
  search_param = {'doc':"mimeType = 'application/vnd.google-apps.document'", 'slide': "mimeType = 'application/vnd.google-apps.presentation'"}
  files = service.files().list(q=search_param[key]).execute()
  '''
  result = []
  page_token = None
  while True:
    try:
      param = {}  #param['mimeType'] = application/vnd.google-apps.document
      if page_token:  
        param['pageToken'] = page_token 
      files = service.files().list(**param).execute()

      result.extend(files['items'])
      page_token = files.get('nextPageToken')
      if not page_token:
        break
    except errors.HttpError, error:
      print 'An error occurred: %s' % error
      break
  return result
  '''

def create_URL(choice, file_id, start, end):
  """Constructs URL to retrieve the changelog.

  Args:
    fileID: Google file ID
    start: starting revision number
    end: ending revision number
  Returns:
    Composite URL for the request
  """

  drive = DRIVE_TYPE[choice]
  url = REV_URL.format(file_id = file_id, start=start, end=end, drive=drive)
  return url

def get_title(service, file_id):
  url = TITLE_PATH.format(file_id = file_id)
  response, content = service._http.request(url)
  content = json.loads(content)
  return content['title']
  
def start_service():
  """Reads config file and initializes the gdrive service with proper authentication"""

  config = ConfigParser.ConfigParser()
  config.read('config/config.cfg')
  TOKENS = config.get('gdrive', 'tokenfile')

  # CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
  # application, including client_id and client_secret, which are found
  # on the API Access tab on the Google APIs
  # Console <http://code.google.com/apis/console>
  #CLIENT_SECRETS = 'config/client_secrets.json'
  CLIENT_SECRETS = config.get('gdrive', 'configurationfile')

  MISSING_CLIENT_SECRETS_MESSAGE = """
  WARNING: Please configure OAuth 2.0
  To make this sample run you will need to populate the config/gdrive_config.json file
  found at:
     %s
  with information from the APIs Console <https://code.google.com/apis/console>.

  """ % os.path.join(os.path.dirname(__file__), CLIENT_SECRETS)

  FLOW = flow_from_clientsecrets(CLIENT_SECRETS,
      scope='https://www.googleapis.com/auth/drive',
      message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage(TOKENS)
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run(FLOW, storage)
  http = httplib2.Http()
  http = credentials.authorize(http)
  service = build("drive", "v2", http=http)
  user_info = get_user_info(service)
  if user_info != None:
    username = user_info['user']['emailAddress']
  else:
    print "Can't get username"
    
  return service

def get_drawings(drawing_ids, service, file_id):
  drawings = []
  for drawing_id in drawing_ids:
    url = DRAW_PATH.format(d_id=drawing_id[0], w=drawing_id[1], h=drawing_id[2])
    response, content = service._http.request(url)
    extension = get_extension(response)
    drawings.append((content, extension))
    
  return drawings

def get_image_links(image_ids, service, file_id):
  image_ids = set(image_ids)
  data = {}
  for i, img_id in enumerate(image_ids):
    key = 'r' + str(i)
    #unicode image_ids are not accepted in the request, so they must be encoded as strings
    data[key] = ['image', {'cosmoId': img_id.encode(), 'container': file_id}]
  request_body = {}
  request_body['renderOps'] = data
  request_body = urllib.urlencode(request_body)
  request_body = request_body.replace('+','')
  my_headers = {}
  my_headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8'

  render_url = BASE_URL + fid + RENDER_PATH + fid
  try:
    response, content = service._http.request(render_url, method='POST', body=request_body, headers=my_headers)
    content = json.loads(content[5:])
    #keep assocation of image ids with image
    for i, img_id in enumerate(image_ids):
      key = 'r' + str(i)
      content[key] = [content.pop(key), img_id]
    return content
  except:
    print response
    print content

def get_extension(html_response):
  '''Returns extension for downloaded resource'''

  cdisp = html_response['content-disposition']
  start_index = cdisp.index('.')
  end_index = cdisp.index('"', start_index)
  extension = cdisp[start_index:end_index]
  return extension

def get_images(image_ids, service, file_id):
  images = []
  links = get_image_links(image_ids, service, file_id)
  for url, img_id in links.itervalues():
    response, content = service._http.request(url)
    extension = get_extension(response)
    images.append((content, extension, img_id))
    
  return images  
  
def get_comments(comment_anchors, service, file_id):
  url = 'https://www.googleapis.com/drive/v2/files/' + file_id + r'/comments?includeDeleted=true&fields=items(anchor%2Ccontent%2Creplies%2Fcontent)'
  response, content = service._http.request(url)
  content = json.loads(content)
  comment_anchors = set(comment_anchors)
  '''
  comments = []
  for item in content['items']:
    if item['anchor'] in comment_anchors:
      comment = item['content']
      replies = []
      if item['replies']:
        for reply in item['replies']:
          replies.append(reply['content'])
      comments.append((comment, replies))'''
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
  comment_anchors = []
  image_ids = []
  drawing_ids = []

  for line in flat_log:
    try:
      i = line.index('{')
      line_dict = json.loads(line[i:])
      if 'style_type' in line_dict:
        if line_dict['style_type'] == 'doco_anchor':
          c_id = line_dict['style_mod']['datasheet_anchor']['cv']['opValue']
          if c_id:
            comment_anchors += c_id if type(c_id) == list else [c_id]
        elif 'datasheet_anchor' in line_dict:
          c_id = line_dict['datasheet_anchor']['cv']['opValue']
          if c_id:
            comment_anchors += c_id if type(c_id) == list else [c_id]
      elif 'epm' in line_dict and 'ee_eo' in line_dict['epm']:
        if 'i_cid' in line_dict['epm']['ee_eo']:
          image_ids.append(line_dict['epm']['ee_eo']['i_cid'])
        elif 'd_id' in line_dict['epm']['ee_eo']:
          d_id = line_dict['epm']['ee_eo']['d_id']
          i_wth = line_dict['epm']['ee_eo']['i_wth']
          i_ht = line_dict['epm']['ee_eo']['i_ht']
          drawing_ids.append((d_id, int(i_wth), int(i_ht)))

    except ValueError:
        pass # either chunked or changelog header without dict, no action needed

  return comment_anchors, image_ids, drawing_ids
  
def process_doc(log, service, file_id):
  flat_log = log2csv.get_flat_log(log)
  comment_anchors, image_ids, drawing_ids = get_doc_objects(flat_log)
  plain_text = csv2plain.parse_log(flat_log)

  comments = get_comments(comment_anchors, service, file_id)
  images = get_images(image_ids, service, file_id)
  drawings = get_drawings(drawing_ids, service, file_id)
  docname = get_title(service, file_id)

  write_doc(docname, plain_text, comments, images, drawings)

def write_doc(docname, plain_text, comments, images, drawings):
  base_dir = docname + '/'
  slide2plain.makedir(base_dir)

  for i,drawing in enumerate(drawings):
    filename = base_dir + 'drawing' + str(i) + drawing[1]
    with open(filename, 'wb') as f:
      f.write(drawing[0])

  for i,img in enumerate(images):
    filename = base_dir + 'img' + str(i) + img[1]
    with open(filename, 'wb') as f:
      f.write(img[0])

  filename = base_dir + 'plain.txt'
  with open(filename, 'w') as f:
    f.write(plain_text.encode('mbcs'))

  filename = base_dir + 'comments.txt'
  comment_string = ''.join(comments)
  with open(filename, 'w') as f:
    f.write(comment_string)

def get_slide_objects(log):
  image_ids = {}
  for line in log['changelog']:
    #line[0][0] is action type, 4 is multiset, 44 is insert image action
    #for video inserts, len...[4] is 18; exclude video inserts for now
    if line[0][0] == 4 and line[0][1][1][0] == 44 and len(line[0][1][0][4]) != 18:
      #for drive,personal upload, image id in ...[9], else if url in ...[11]
      slide_id = line[0][1][0][5]
      #if not slide_id in image_ids:
       # image_ids[slide_id] = []
      #if ..[11] is a list, the image was not uploaded via url
      if type(line[0][1][0][4][11]) == list: 
        #if ..[9] is a list, not uploaded by drive
        if type(line[0][1][0][4][9]) == list:
          image_id = line[0][1][0][4][7]
        else:
          image_id = line[0][1][0][4][9]
      else:
        #if 11 is not a list, it was uploaded by url, src in ...[9]
        image_id = line[0][1][0][4][11]

      #image_ids[slide_id].append(image_id)
      image_ids[image_id] = slide_id
  return image_ids

def process_slide(log, service, file_id):

  images = get_images(image_ids.keys(), service, file_id)

  #index images by slide for printing
  slide_images = {}
  for img in images:
    slide_id = image_ids.pop(img[2])
    if slide_id in slide_images:
      slide_images[slide_id].append(img)
    else:
      slide_images[slide_id] = [img]

  path = get_title(service, file_id)
  path += '/'
  slide2plain.write_objects(log, slide_images, path)
  
def main(argv):

  helpmsg = 'Usage: python driverunner.py <file_id> <start revision> <end revision> \n'\
              'Downloads the plain-text as of end revision as well as the images and comments associated with the file \n'
  if not argv:
    print helpmsg
    #sys.exit(2)

  if len(argv) > 0:
    file_id = argv[0]
    start = argv[1]
    end = argv[2]
  else:
    choice = int(raw_input("Enter 0 for document, or 1 for presentation: "))
    file_id = raw_input("Enter file ID: ")
    start = raw_input("Start from revision: ")
    end = raw_input("End at revision: ")

#***********testing*********************only*************
  #file_id = '1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps'
  #file_id = '1O-vM_7MQgEJW06scH7k8zKHB2z2RClhPJDxI_jIKtdc'
#***************
  try:
    service = start_service()
    url = create_URL(choice, file_id, int(start), int(end))
    response, log = service._http.request(url) 
  except:
    raise

  log = json.loads(log[5:])
  if type(log['changelog'][0][0]) == dict:
    process_doc(log, service, file_id)
  elif type(log['changelog'][0][0]) == list:
    process_slide(log, service, file_id)
  else:
    raise ValueError('Unexpected type %s' % type(log['changelog'][0][0]))

if __name__ == '__main__':
    main(sys.argv[1:])
