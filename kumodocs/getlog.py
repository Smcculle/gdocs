import gdata.docs.service
import ConfigParser, urllib2, os, httplib2, sys

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError, flow_from_clientsecrets
#***requires oauth2client version 1.3.2***
from oauth2client.tools import run

#**TODO:  clean, list docs and getting file ID, integrate into kumodd?


# Create a client class which will make HTTP requests with Google Docs server.
#client = gdata.docs.service.DocsService()
fid = '1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps'
#url = 'https://docs.google.com/document/d/1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps/revisions/load?id=1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps&start=254&end=276'#&token=AC4w5ViipiO5sN96CUai4LMfK9VWsbLltw%3A1443027271527'
base_url = 'https://docs.google.com/document/d/'
url_path = '/revisions/load?id='
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

def create_URL( fileID, start, end ):
  """Constructs URL to retrieve the changelog.

  Args:
    fileID: Google file ID
    start: starting revision number
    end: ending revision number
  Returns:
    Composite URL for the request
  """
  
  url = base_url + fileID + url_path + fileID + '&start=' + str(start) + '&end=' + str(end)
  print url
  return url                                          

def list_files():
  mime_type = 'application/vnd.google-apps.folder'
  #service.files().list()
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
#*******************************************************
config = ConfigParser.ConfigParser()
config.read('config/config.cfg')
TOKENS = config.get('gdrive', 'tokenfile')
CSV_FILE = config.get('gdrive', 'csvfile')
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
  print "Creds none/invalid"
  #credentials = run(FLOW, storage) test later
http = httplib2.Http()
http = credentials.authorize(http)
service = build("drive", "v2", http=http)
user_info = get_user_info(service)
if user_info != None:
  username = user_info['user']['emailAddress']
else:
  print "Can't get username"
	
''' using service._http to place a post request:
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
try:
  url = 'https://docs.google.com/document/d/1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps/renderdata?id=1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps&token=AC4w5Vh_iTzvW2ih7wThCGejbO3J1pVpkw%3A1443374604500'
  #url = 'https://lh3.googleusercontent.com/TG-HofNaScWRUfyUuA-Ty4PzbZUW8UXHktI9apIv-DQygu7CJkjkgGY5Cm3X7FSXCiAzlQ=s1600'
  #url = 'https://lh3.googleusercontent.com/8oDqSwcKXBvy6tFS4badAWeQk7_1o3a_6d6EY9EKFsC9pTWD55qXXK3JCi8jcjTuisk01zv6ejeztTqXX3NpE91C5XxLFrT_CLUCK65bskNceclBXM4ersjGSuO0u_3dHFQ=s1600'
  #url = 'filesystem:https://docs.google.com/persistent/docs/documents/1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps/image/AE7MojedZEHNulGfoIidNJe3igHFde64_lGK2V7B6HrsqCmiBz1olI2xkcLwSNqaMsa76Xa69Z375zIli6pI1QSQKSpOsklAx4VirdmOLf0hxkCCa1HRdu8zW0JqsGD4xR-GOAq9NXLW3pvU6TcFnzO26iAphdEZLQS9c5CiznsfeRJZsCid56IS95UE_RDnip1zwZMXgTqOrP1RXUSY9frirqSPCC6YJUDiJ0h2LcaRmnolSe2r_ndW0f8ml0UOkiBTc99UHNFPYkHJ14mbIgPLVGjvOWd2QQ?zx=t2cfm4hfa0gb' 
  #url = create_URL(fid, 292, 293)
  #url = 'https://docs.google.com/document/d/1SsCaJuY51VVeCmvh80obb7kPsb6Ybau6ngKm8KIUxps/'
  resp, content = service._http.request(url)
  print resp
	    
except: 
  raise
