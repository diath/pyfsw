Note
====

The website can be deployed using various methods. In this specific document we will focus on deploying using the nginx reverse proxy server and gunicorn utility. For more deployment options please see [this page](http://flask.pocoo.org/docs/0.10/deploying/).

Requirements
============

If you decided to follow the instructions in this document rather than other deployment options, it is required that your system has screen, nginx and gunicorn installed.

To install them on apt-based systems (such as Debian and Ubuntu), issue the following commands:
``$ apt-get update && apt-get install nginx screen``
``$ pip3 install gunicorn``

Due to performance and security reasons you may want to use the most recent nginx version. Please see [this page](https://www.dotdeb.org/) for more information.

Deploying
=========

First of all, create a new screen session:
``$ screen -SU website``

You can use ^-A-D key combo to detach from the session, and *screen -x website* command to attach to the session later. For a detailed tutorial about using screen please see [this page](http://www.rackaid.com/blog/linux-screen-tutorial-and-how-to/).

Once inside the screen session, navigate to pyfsw directory, that is the one that contains "run.py" file and issue the following command:
``$ gunicorn -b 127.0.0.1:5005 -w 4 run:app --log-file -``

The host and port options will override the values set in config.py file. The website should be running internally now on port 5005, you can adjust it up to your preferences. You will have to configure nginx to communicate with the website and serve it externally now, you can use [this simple configuration](misc/nginx.conf) file to get running (please make sure to edit the port in the proxy_pass option).


For more nginx config options please refer to the [nginx documentation](http://wiki.nginx.org/Configuration). 
For more gunicorn options please refer to the [gunicorn documentation](http://docs.gunicorn.org/en/latest/).
