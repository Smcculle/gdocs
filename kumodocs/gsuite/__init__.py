from collections import namedtuple

# package-level constants defined below
REL_CONFIG_PATH = ['..', '..', 'config', 'config.cfg']
API_BASE = 'https://docs.google.com/{drive}/d/{file_id}/{params}'
REV_PARAMS = 'revisions/load?start={start}&end={end}'
RENDER_PARAMS = 'renderdata?id={id}'
MIME_TYPE = "mimeType = 'application/vnd.google-apps.{}'"
SERVICES = ['document', 'drawing', 'form', 'presentation', 'spreadsheet']
DRAW_PARAMS = 'image?w={w}&h={h}'

# package-level named tuples
FileChoice = namedtuple('FileChoice', 'file_id, title, drive, max_revs')
Drawing = namedtuple('Drawing', 'd_id width height')
