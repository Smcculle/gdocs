import gdata.docs.service
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


# Create a client class which will make HTTP requests with Google Docs server.
#client = gdata.docs.service.DocsService()
fid = '1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps'
#url = 'https://docs.google.com/document/d/1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps/revisions/load?id=1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps&start=254&end=276'#&token=AC4w5ViipiO5sN96CUai4LMfK9VWsbLltw%3A1443027271527'
BASE_URL = 'https://docs.google.com/document/d/'
REV_PATH = '/revisions/load?id='
RENDER_PATH = '/renderdata?id='
DRAW_PATH = 'https://docs.google.com/drawings/d/{d_id}/image?w={w}&h={h}'
REV_URL = 'https://docs.google.com/{drive}/d/{file_id}/revisions/load?id={file_id}'\
          '&start={start}&end={end}'
DRIVE_TYPE = {0: 'document', 1: 'presentation'}

'''
# Query the server for an Atom feed containing a list of your documents.
documents_feed = client.GetDocumentListFeed()
# Loop through the feed and extract each document entry.
for document_entry in documents_feed.entry:
  # Display the title of the document on the command line.
  print document_entry.title.text '''
#response = urllib2.urlopen('http://python.org/')
#response2 = urllib2.urlopen('https://docs.google.com/document/d/1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps/revisions/load?id=1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps&start=356&end=413&token=AC4w5VhT-LQdJPSQF5_vs6me2J2jm5n9tQ%3A1443022633364')
#response3 = urllib2.urlopen('https://docs.google.com/document/d/1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps/revisions/load?id=1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps&start=356&end=413')

#start below here                            
def get_user_info(service):
  """Print information about the user along with the Drive API settings.

  Args:
    service: Drive API service instance.
  """
  try:
    about = service.about().get().execute()

		#print 'Current user name: %s' % about['name']
		#print 'Root folder ID: %s' % about['rootFolderId']
		#print 'Total quota (bytes): %s' % about['quotaBytesTotal']
		#print 'Used quota (bytes): %s' % about['quotaBytesUsed']
    return about
  except errors.HttpError, error:
    print 'An error occurred: %s' % error
    return None

def write(msg):
  with open('out.txt', 'w') as f:
    f.write(msg)

def create_URL(choice, file_id, start, end):
  """Constructs URL to retrieve the changelog.

  Args:
    fileID: Google file ID
    start: starting revision number
    end: ending revision number
  Returns:
    Composite URL for the request
  """
  
  #url = BASE_URL + fileID + REV_PATH + fileID + '&start=' + str(start) + '&end=' + str(end)
  drive = DRIVE_TYPE[choice]
  url = REV_URL.format(file_id = file_id, start=start, end=end, drive=drive)
  return url                                          

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
def code():
  #*******************************************************
  

  '''firefox_headers = Host: docs.google.com
  User-Agent: Mozilla/5.0 (Windows NT 6.0; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0
  Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
  Accept-Language: en-US,en;q=0.5
  Accept-Encoding: gzip, deflate
  X-Same-Domain: 1
  X-Build: kix_2015.39-Tue_c
  X-Rel-Id: f4.3c139c9a.s
  Content-Type: application/x-www-form-urlencoded;charset=utf-8
  Referer: https://docs.google.com/document/d/1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps/edit
  Content-Length: 185
  Cookie: S=documents=ppqauTAY-3fd0JQbccmuLg; PREF=ID=1111111111111111:FF=0:LD=en:TM=1430849915:LM=1434946035:GM=1:S=DvnVckHxB-q8f3uM; NID=72=SN-h7bU5ixF7JXVToenbW0A8Hx29fx9ok685PuJ3tL4NQJG3IH_0Vxs4pb5yYhzbRJQVIWfkMeH86qxNinQxRO640EVjrl7Gxx5T16oZE6WygOUo1PNvFo-CerLb-eZAiA4TAawyioMYbu-gnBdIydUV2ReMXNPo7c787dtdBADCLOt9Q90b2umTdE_xm3B42w0167Eh8Is07c42jZAnS61KZ6_kN6ICbc2CruSEqd_207xGHEKbJZivYZQ_QHuUKn1bQRzCDeXKshJEJOkxYrOYflTBuDsm_4oZWHE; SID=DQAAAAUBAAB0RJLyqQ8N3ctjEOV27goo-GxsLlWD_eZT80GRWp7HGVVhWBUQRKfrKUZIiBoZ6K-cIETf6RZI-bMSA5F35KZxJnXMSJyR9hvqlnicb_4_3-0XeU7TdMrtGn-OIzUuKIc1-qfIBXPGnJl1R8jvx0dJYnJPNkh4i4hpwT8c3t_aMeMeKZ5HoovdeOnzr3iKZYOcX1-6aTDvDITPF-lMDnrwZguB5zitFvBfwE6kEPnwrxnIILqJiku44fxKucwUsg8ikdP0jdq7V_H95G0lVrU7gSKQi-GMPx5Ye1UEZkMak_2lwv5lz6UT2rjuZOFT9tGOrwmgiu5HG2RUYQiey4UAIwwDVLoqQfYdEc1Jcv0k6A; HSID=AYmQls4T18mDaCbr2; SSID=AmXPoDc67aYDoNmzl; APISID=iKZE9vv7HT70tHOf/ADLlc-pDqQppsjzXn; SAPISID=f1uyG_q5zERmOJZG/At2H1U7DnWgRErkCH; OGP=-5061451:; WRITELY_SID=DQAAAAsBAACvdY0F8RM5A6LtQizf9xNQ66vw6JhGiSWJ6TXfFTIgH3QIUQzW5XV6VhqBSbidSQ-WUdJIdXPkxCtfiLc8ybwhgByfQs5jxQiQhuqfpfX-tJ35wCFEGzkv84Bsw1KYL0QR5Wo-sr0c8rQUOnOVYFCs8F5cWUsGqQrOOgUQ8rUcqBV-hypdymQyEks5mL6bqaOu3-ZH19sNCd4vkQMsUbADa5ZfDtyERBe-JEOtLOYq-w6V3_Hys9L7qqZE1Ld0sKsqECzb0GOrCJ5scmaT_NLCy8UC7a3mQFb-Tmp23STPU5QFMc1FRkRWSj0MPVyCw2jGWeX84ppYdEgZQoAYlyFYhFt3J1oDK3MOv__WBguhaw; GMAIL_RTT=79; llbcs=0; lbcs=1
  Connection: keep-alive
  Pragma: no-cache
  Cache-Control: no-cache'''

  '''using service._http to place a post request:
  headers = {'Content-Length': ' *len(data)*', 'Accept-Language': ' en-US,en;q=0.5',
             'Accept-Encoding': ' gzip, deflate', 'X-Rel-Id': ' f3.3c139c9a.s', 'Connection': ' keep-alive',
             'Accept': ' text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
             'User-Agent': ' Mozilla/5.0 (Windows NT 6.0; WOW64; rv', 'X-Build': ' kix_2015.38-Tue_b',
             'Host': ' docs.google.com', 'Referer': ' https', 'X-Same-Domain': ' 1', 'Pragma': ' no-cache',
             'Cache-Control': ' no-cache',
             'Cookie': ' S=documents=_gEM09sxq_vGAys5OjO15Q; PREF=ID=1111111111111111',
             'Content-Type': ' application/x-www-form-urlencoded;charset=utf-8'}
  request body has the form of data, where           
  data = {"r0":["image",{"cosmoId":"AE7MojedZEHNulGfoIidNJe3igHFde64_lGK2V7B6HrsqCmiBz1olI2xkcLwSNqaMsa76Xa69Z375zIli6pI1QSQKSpOsklAx4VirdmOLf0hxkCCa1HRdu8zW0JqsGD4xR-GOAq9NXLW3pvU6TcFnzO26iAphdEZLQS9c5CiznsfeRJZsCid56IS95UE_RDnip1zwZMXgTqOrP1RXUSY9frirqSPCC6YJUDiJ0h2LcaRmnolSe2r_ndW0f8ml0UOkiBTc99UHNFPYkHJ14mbIgPLVGjvOWd2QQ",
                         "container":"1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps"}],
          "r1":["image",{"cosmoId":"AE7MojcVJFxz6C3l7_zsJTerLC3O5Brhi7JJzDW-6B1fADHe11ARrISozlbtx-q69Xv7PL5_eta7zxryOWmcgWjYZ_XbV5BwlEbx6NSK8iKXVxNXxjVwsVa4gHiahiN_ViPztRFaxHDz0EGBRHJwQPFhsogoJWChMnpu8_dpMnU18-ibrYjKpc7_tldrCLGiYJQ2NppkQNR1Ra_BVLqojugBpnsuIDuIYkPiDZkdjcGIECxHMZHYFx0ptvFFHSeQqVIFBEy0EO-8V0qminR9O8QIS-PukaJvotzltYej0x4sfVMj5fdakOEvBa8lZDY4a5vmXoGDqH9nxo1M7_dSmrYp4M7gBQicm6rXLwtwNO34hWp1rKQynhHJJZOpdlT_0iJgX1ivYm5KRzyxUhD2arp7W6VA4b4UPg",
                         "container":"1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps"}]}
  where cosmoId are obtained from the changelog, container is doc_id.
  data is then urlencoded such as urllib.encode(data)
  resp, cont = service._http.request(
      url, method='POST', body=data, headers=my_headers)
      '''
  content_type = 'application/x-www-form-urlencoded;charset=UTF-8'
  Origin = 'https://docs.google.com'
  Referer = 'https://docs.google.com/document/d/1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps/edit'
  user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'
  x_build = 'kix_2015.39-Tue_c'
  x_rel_id = 'f4.1222e5f4.s'
  x_same_domain = 1
  #i_cid_0 = '1dvj9ynBuUWMi9NyMdlS3GgD37_HZVGKxBy5cRQ'
  i_cid_0 = '1-1lmZiUX7N0wdSobr8v0-Wzo2PHezCXQyjEEeg'
  fid = '1bR8kOZ7MB1-RO3ENrPau7k1JrdjbALq38D6TlgXWqAo'
  data = {}
  data['r0'] = ['image',{'cosmoId':i_cid_0, 'container':fid}]
  req_body = {}
  req_body['renderOps'] = data
  req_body = urllib.urlencode(req_body)
  req_body.replace('+', '')
  render_url = base_url + fid + '/renderdata?id=' + fid
  my_headers = {}
  #my_headers['Content-Length'] = len(req_body)
  my_headers['Content-Type'] = content_type
  #my_headers['Referer'] = Referer

  try:
    #resp, cont = service._http.request(render_url, method='POST', body=req_body, headers=my_headers)
    myComments = service._http.request('https://www.googleapis.com/drive/v2/files/1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps/comments?includeDeleted=true')
    
    #url = 'https://docs.google.com/document/d/1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps/renderdata?id=1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps&token=AC4w5Vh_iTzvW2ih7wThCGejbO3J1pVpkw%3A1443374604500'
    #url = 'https://lh3.googleusercontent.com/TG-HofNaScWRUfyUuA-Ty4PzbZUW8UXHktI9apIv-DQygu7CJkjkgGY5Cm3X7FSXCiAzlQ=s1600'
    #url = 'https://lh3.googleusercontent.com/8oDqSwcKXBvy6tFS4badAWeQk7_1o3a_6d6EY9EKFsC9pTWD55qXXK3JCi8jcjTuisk01zv6ejeztTqXX3NpE91C5XxLFrT_CLUCK65bskNceclBXM4ersjGSuO0u_3dHFQ=s1600'
    #url = 'filesystem:https://docs.google.com/persistent/docs/documents/1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps/image/AE7MojedZEHNulGfoIidNJe3igHFde64_lGK2V7B6HrsqCmiBz1olI2xkcLwSNqaMsa76Xa69Z375zIli6pI1QSQKSpOsklAx4VirdmOLf0hxkCCa1HRdu8zW0JqsGD4xR-GOAq9NXLW3pvU6TcFnzO26iAphdEZLQS9c5CiznsfeRJZsCid56IS95UE_RDnip1zwZMXgTqOrP1RXUSY9frirqSPCC6YJUDiJ0h2LcaRmnolSe2r_ndW0f8ml0UOkiBTc99UHNFPYkHJ14mbIgPLVGjvOWd2QQ?zx=t2cfm4hfa0gb' 
    #url = create_URL(fid, 292, 293)
    #url = 'https://docs.google.com/document/d/1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps/'
    #resp, content = service._http.request(url)
    #print resp
              
  except: 
    raise

  #To catch a comment#
  '''
  comments = service.comments().list(fileId=fid, includeDeleted=True).execute()
  for i in comments['items']:
          print i['htmlContent']
          for j in i['replies']:
                  print j['content']
                  '''
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
    url = DRAW_PATH.format(id=drawing_id[0], w=drawing_id[1], h=drawing_id[2])
    print url
    response, content = service._http.request(url)
    extension = get_extension(response)
    drawings.append((content, extension))

  return drawings

def get_image_links(image_ids, service, file_id):
  image_ids = set(image_ids)
  data = {}
  for i, imid in enumerate(image_ids):
    key = 'r' + str(i)
    #unicode image_ids are not accepted in the request, so they must be encoded as strings
    data[key] = ['image', {'cosmoId': imid.encode(), 'container': file_id}]
  request_body = {}
  request_body['renderOps'] = data
  request_body = urllib.urlencode(request_body)
  request_body = request_body.replace('+','')
  my_headers = {}
  my_headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8'

  render_url = BASE_URL + fid + RENDER_PATH + fid
  try:
    response, content = service._http.request(render_url, method='POST', body=request_body, headers=my_headers)
    return json.loads(content[5:])
  except:
    raise

def get_extension(html_response):
  '''Returns extension for downloaded resource'''
  
  cdisp = html_response['content-disposition']
  return cdisp[cdisp.index('.'):-1]

def get_images(image_ids, service, file_id):
  images = []
  links = get_image_links(image_ids, service, file_id)
  for url in links.itervalues():
    response, content = service._http.request(url)
    extension = get_extension(response)
    images.append((content, extension))

  return images  
  
def get_comments(comment_anchors, service, file_id):
  url = 'https://www.googleapis.com/drive/v2/files/' + file_id + r'/comments?includeDeleted=true&fields=items(anchor%2Ccontent%2Creplies%2Fcontent)'
  response, content = service._http.request(url)
  content = json.loads(content)
  comment_anchors = set(comment_anchors)
  comments = []
  for item in content['items']:
    if item['anchor'] in comment_anchors:
      comment = item['content']
      replies = []
      if item['replies']:
        for reply in item['replies']:
          replies.append(reply['content'])
      comments.append((comment, replies))

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

  for i,drawing in enumerate(drawings):
    with open('imtest/draw' + str(i) + drawing[1], 'wb') as f:
      f.write(drawing[0])

def get_slide_objects(log):
  image_ids = {}
  for line in log['changelog']:
    #line[0][0] is action type, 4 is multiset, 44 is insert image action
    #for video inserts, len...[4] is 18; exclude video inserts for now
    if line[0][0] == 4 and line[0][1][1][0] == 44 and len(line[0][1][0][4]) != 18:
      #for drive,personal upload, image id in ...[9], else if url in ...[11]
      slide_id = line[0][1][0][5]
      if not slide_id in image_ids:
        image_ids[slide_id] = []
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
      
      image_ids[slide_id].append(image_id)
  return image_ids

def process_slide(log, service, file_id):
  #plain_text = slide2plain
  image_ids = get_slide_objects(log)
  '''
  id_list = []
  for image_id in image_ids.itervalues():
    id_list.append(image_id)    '''
  images = get_images([img for img_list in image_ids.values() for img in img_list],
                       service, file_id)

  for i,img in enumerate(images):
    with open('imtest/img' + str(i) + img[1], 'wb') as f:
      f.write(img[0])
  
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
  file_id = '1O-vM_7MQgEJW06scH7k8zKHB2z2RClhPJDxI_jIKtdc'
  try:
    service = start_service()
    url = create_URL(choice, file_id, int(start), int(end))
    print url
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

'''
#####getting comments from log:, and some will not be comments :(
    for ind,line in enumerate(data):
	try:
		i = line.index('{')
		x = json.loads(line[i:])
		if 'style_type' in x:
			if x['style_type'] == 'doco_anchor':
				print 'at',ind,x['style_mod']['datasheet_anchor']['cv']['opValue']
		else:
			if 'datasheet_anchor' in x:
				print '2ndat',ind,x['datasheet_anchor']['cv']['opValue']
	except ValueError:
		pass
'''

