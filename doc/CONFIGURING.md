Configuring
===========

This document serves as a reference manual for the config options.

DB_URI
------

This option tells the website how to connect to the database server. In most cases the following example should get you going:

``mysql+pymysql://user:password@host/Database?unix_socket=/socket/path``

For a more detailed description and more options please see the [SQLAlchemy documentation](http://docs.sqlalchemy.org/en/latest/dialects/mysql.html#module-sqlalchemy.dialects.mysql.pymysql).

SECRET_KEY
----------

This options is used to sign the cookies cryptographically. You should set it to a random string of at least a moderate length. You can use the following command to generate one:

``$ < /dev/urandom tr -dc 'a-zA-Z0-9-_!@#$%^&*()_+{}|:<>?=' | head -c${1:-32}; echo;``

You can also invoke a Python shell and use the following code:

``import os``

``os.urandom(32)``

NET_HOST
--------

The host to listen on when running the server. You most likely want to leave it at 127.0.0.1 in development mode. In production mode this variable will be overridden by the deployment tool.

NET_PORT
--------

The port to listen on when running the server. Pick any unused port number higher than 1024 in development mode. In production mode this variable will be overridden by the deployment tool.

DEBUG
-----

determines whether to enable the debugger. This should **never** be set to True in **production** mode as it exposes a system shell to the client. You probably want to set it to True in development mode as it provides an easy way to find the problems within your code (make sure that the server doesn't listen on a public host interface when in development mode though).

LOG_FILE
--------

A path to a log file that will contain any stack traces and errors when DEBUG is set to False.

DEBUG_PROFILER
--------------

determines whether to enable a debug profiler that contains information about rendering time, queries, query times and such. This option will only work when DEBUG is set to True.

DATE_FORMAT
-----------

The date format used throughout various pages. Please see [this page](https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior) for a list of available format options.

CACHE_TIME
----------

Some pages are cached to improve the performance. This option determines how long should a page get cached for. The value is represented in seconds. Set it to 0 to disable the caching mechanism.

CAPTCHA_SITE_KEY
CAPTCHA_SECRET_KEY
------------------

Captcha site and secret keys used to display Google's NoCaptcha Recaptcha. Please see [their website](https://www.google.com/recaptcha/intro/index.html) for more details.

UPLOAD_PATH
-----------

A path to a directory where the uploaded guild logos should be stored. It is recommended that the directory is not executable (just in case).

SERVER_NAME
-----------

This option is used to display the server name in the website's title and footer.

SITE_DESCR
----------

This option is passed to the description tag in the website's header section.

STATUS_HOST
-----------

The host of the status server used to fetch the server information.

STATUS_PORT
-----------

The port of the status server used to fetch the server information.

STATUS_TIMEOUT
--------------

The status socket timeout in seconds. This option should not be lower than statusTimeout in config.lua.

ADMIN_ACCOUNT_TYPE
------------------

The account type of administrators on your server. You probably want to leave it at 5.

POST_COOLDOWN
-------------

The cooldown between creating a new forum thread/post in seconds.

FORUM_LEVEL_REQUIREMENT
-----------------------

The minimum level required to make a thread/post on the forum.

FORUM_ACCOUNT_AGE_REQUIREMENT
-----------------------------

The minimum account age required to make a thread/post on the forum in days.

FORUM_CHARACTER_LIMIT
---------------------

The maximum length of a forum thread/post.

THREADS_PER_PAGE
----------------

determines how many threads should be displayed per a board page.

POSTS_PER_PAGE
--------------

determines how many posts should be displayed per a thread page.

TOWNS
-----

A Python dictionary where the town IDs are used as the dict keys and the values are dictionaries containing the following keys: **name** and **hidden**. The hidden key is a boolean that determines whether a town should be displayed on the houses page.

HOUSE_PRICE
-----------

The house price per SQM used to calculate the total house price on the houses page.

GUILD_LEVEL
-----------

The minimum character level to create a new guild.

DELETION_DELAY
--------------

The delay before the server handles hard-deleting a character in days.

VOCATIONS
---------

A Python dictionary where the vocation IDs are used as the dict key and the values are vocation names.

STAFF_POSITIONS
---------------

A Python dictionary where the group IDs are used as the dict key and the values are group names.

GENDERS
-------

A Python dictionary where the gender IDs are used as the dict key and the values are gender names.

NEW_CHARACTER
-------------

QUESTS
------

A Python list of dictionaries containing the following keys: **name**, **key** and **value**. The key is a storage key and the value is a quest value that determines the final quest value to display the quest as completed. See the reference config file for an example entry.

ACHIEVEMENTS
------------

A Python list of dictionaries containing the following keys: **name**, **key** and **value**. The key field is a storage key, the value field is the final storage value that determines the final achievement value to display the achievement and the tier field is used to display a corresponding amount of "star" icons next to the achievement. See the reference config file for an example entry.

PAYPAL_BUTTONS
--------------

A Python list of dictionaries containing the following keys: **id**, **amount**, **points**. The id field is PayPal button ID that you can generate when signed into your PayPal account, the amount field is the decimal price value and the points field is the amount of premium points that an account should receive upon completing a donation. See the reference config file for an example entry.

ZAYPAY_OPTIONS
--------------

A Python list of dictionaries containing the following keys: **name**, **payalogue_id**, **price_id**, **price_key**, **points** and **amount**. The name field is used to title the payment container, the point field is the amount of premium points that an account should receive upon completing a payment. The other fields are corresponding payalogue settings that you can obtain once configuring payalogues when signed into your ZayPay account. See the reference config file for an example entry.
