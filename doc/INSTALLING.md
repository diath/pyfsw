Requirements
============

Before you can begin the installation process, it is required that your system has Python 3.x and pip tool installed.

To install them on apt-based systems (such as Debian and Ubuntu), issue the following command:

``$ apt-get update && apt-get install python3 pip3``

Installing
==========
* ``$ git clone https://github.com/diath/pyfsw``
* ``$ cd pyfsw``
* ``$ pip3 install -r dependencies.txt``
* ``$ mv pyfsw/config.example.py pyfsw/config.py``

The website should be ready for the configuration process now. Please refer to the documentation if you are not sure what a specific config option stands for (most of them should be pretty self-explanatory though).

Development Mode
================

To run the website in development mode, please use the following command:

``$ python3 run.py``

This will run the website on the configured host and port using the Flask's built-in server. To run the website in production mode please refer to the [deploying document](doc/DEPLOYING.md).

Note
====

It is recommended that you use Virtualenv when installing pyfsw. Please refer to [this article](http://simononsoftware.com/virtualenv-tutorial/) for a Virtualenv tutorial.
