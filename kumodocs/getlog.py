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
	
	
try:
  url = create_URL(fid, 292, 293)
  resp, content = service._http.request(url)
  print resp
	    
except: 
  raise
