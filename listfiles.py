def list_files(service, key):
  search_param = {'document':"mimeType = 'application/vnd.google-apps.document'",
                  'presentation': "mimeType = 'application/vnd.google-apps.presentation'"}
  files = service.files().list(q=search_param[key]).execute()
  files = files['items']
  print '\nChoose a file from the list below'
  for i,file in enumerate(files):
    print '%d: \t%s' %(i+1, file['title'])

  choice = int(raw_input('\nChoose a file:  '))
  
  choice = choice - 1
  fileId = files[choice]['id']
  revisions = service.revisions().list(fileId=fileId).execute()
  maxRev = revisions['items'][-1]['id']
  return fileId, maxRev
