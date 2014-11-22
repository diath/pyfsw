# Database URI Scheme (Refer to the SQLAlchemy documentation for variations)
DB_URI = ''

# Secret Key
SECRET_KEY = 'pyfsw'

# Network Host
NET_HOST = '127.0.0.1'

# Network Port
NET_PORT = 5000

# Debug Mode
DEBUG = False

# Debug Profiler
DEBUG_PROFILER = False

# Date Format
DATE_FORMAT = '%m/%d/%y %I:%M %p'

# Cache Time (Seconds)
CACHE_TIME = 0

# Guild Logo Upload Path
UPLOAD_PATH = ''

# Captcha Font Path (Optional)
FONT_PATH = ''

# Server Name
SERVER_NAME = ''

# Page Description
SERVER_DESCR = ''

# Post Cooldown (A cooldown between creating a new forum thread/post, seconds)
POST_COOLDOWN = 30

# Town Names
TOWNS = {
	0: 'All',
	1: 'Some Town'
}

# House Price (per SQM)
HOUSE_PRICE = 1000

# Vocation Names
VOCATIONS = {
	0: 'No Vocation',
	1: 'Sorcerer',
	2: 'Druid',
	3: 'Paladin',
	4: 'Knight',
	5: 'Master Sorcerer',
	6: 'Elder Druid',
	7: 'Royal Paladin',
	8: 'Elite Knight'
}

# Staff Positions
STAFF_POSITIONS = {
	0: 'Player',
	1: 'Player',
	2: 'Gamemaster',
	3: 'God'
}

# Gender Names
GENDERS = {
	0: 'Female',
	1: 'Male'
}

# New Character Options
NEW_CHARACTER = {
	'genders': [0, 1],
	'vocations': [5, 6, 7, 8],
	'towns': [1, 2],
	'outfit': [0, 0, 0, 0]
}

# Quests List
QUESTS = [
	{'name': 'Example Quest', 'key': 12101, 'value': 1},
]

# Achievements List
ACHIEVEMENTS = [
	{'name': 'Example Achievement', 'key': 12101, 'value': 1, 'tier': 1}
]

# Paypal Buttons
PAYPAL_BUTTONS = [
	{'id': 'id', 'amount': 'price', 'points': 0},
]
