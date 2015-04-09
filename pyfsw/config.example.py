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

# Log File
# Warnings and errors will be logged to the file when DEBUG is set to False
LOG_FILE = 'error.log'

# Debug Profiler
DEBUG_PROFILER = False

# Date Format
DATE_FORMAT = '%m/%d/%y %I:%M %p'

# Cache Time (Seconds)
CACHE_TIME = 0

# Captcha Settings (https://www.google.com/recaptcha/intro/index.html)
CAPTCHA_SITE_KEY = ''
CAPTCHA_SECRET_KEY = ''

# Guild Logo Upload Path
UPLOAD_PATH = ''

# Server Name
SERVER_NAME = ''

# Page Description
SITE_DESCR = ''

# Status host
STATUS_HOST = '127.0.0.1'

# Status port
STATUS_PORT = 7171

# Status timeout (seconds, cannot be lower than statusTimeout in config.lua)
STATUS_TIMEOUT = 5 * 60

# Admin Account Type
ADMIN_ACCOUNT_TYPE = 5

# Post Cooldown (A cooldown between creating a new forum thread/post, seconds)
POST_COOLDOWN = 30

# Forum Posting Requirements (Account age in days)
FORUM_LEVEL_REQUIREMENT = 20
FORUM_ACCOUNT_AGE_REQUIREMENT = 7

# Thread/post length limit
FORUM_CHARACTER_LIMIT = 2048

# Threads per board page
THREADS_PER_PAGE = 20

# Posts per thread page
POSTS_PER_PAGE = 10

# Town Names
TOWNS = {
	0: {'name': 'All', 'hidden': False},
	1: {'name': 'Some Town', 'hidden': False},
}

# House Price (per SQM)
HOUSE_PRICE = 1000

# Guild Level Requirement
GUILD_LEVEL = 100

# Deletion Delay (A delay before the server handles hard deleting a character in days)
DELETION_DELAY = 60

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

# PayPal Buttons
PAYPAL_BUTTONS = [
	{'id': 'id', 'amount': 'price', 'points': 0},
]

# ZayPay Options
ZAYPAY_OPTIONS = [
	{'name': 'name', 'payalogue_id': 0, 'price_id': 0, 'price_key': '', 'points': 0, 'amount': '0.00'}
]
