# How to setup and use OSC automation
This document describes how to use public and private Python libraries and Robot framework in OSC team's test automation.

## Prerequisites  
1. Install Python 3.X  
2. Pull in github OSC private Python libraries
3. Install Robot framework

### Windows Environment
Ensure that your pip is at the latest version:

`> python -m pip install --upgrade pip`

Download Visual C++ build tools from http://landinghub.visualstudio.com/visual-cpp-build-tools to avoid the following error when installing OpenStack libraries: 

`"error Microsoft Visual C++ 14.0 is required. Get it with "Microsoft Visual C++ Build Tools".`  

Install OpenStack libraries

```
> pip install python-openstackclient    
> pip install python-keystoneClient    
> pip install python-neutronclient    
> pip install robotframework    
```
The following are examples of executing Robot with Python commands on Windows:  
Go to robot directory to be able to execute automation commands

`> cd  osc-tests\functional-tests\robot`  

Execute a single test category

`> c:\Python36\Scripts\pybot.bat -d ..\results -v testbed:mytestbed.robot MC.robot`  

Execute multiple test categories

`> c:\Python36\Scripts\pybot.bat -d ..\results -v testbed:mytestbed.robot -A Multiple-Suites.robot`  

### Ubuntu Environment
In Ubuntu it is tricky, first run this with -E which helps to run as environment of current user, not the root user, in addition we have to install setuptools to be used by pip3 later:
```sh  
$ sudo –E pip3 install setuptools  
```  
Upgrade the pip3 itself to use setuptools - so it will use the updated setuptools and install correctly all the rest:
```sh  
$ sudo –E pip3 install --upgrade pip  
```  
```sh
$ sudo -E pip3 install python-openstackclient    
$ sudo -E pip3 install python-keystoneClient    
$ sudo -E pip3 install python-neutronclient    
$ sudo -E pip3 install robotframework    
```
The following are examples of executing Robot with Python commands on Ubuntu:  
Go to robot directory to be able to execute automation commands

`$ cd  osc-tests/functional-tests/robot`

Execute a single test category

`$ pybot -d ../results -v testbed:mytestbed.robot MC.robot`   

Execute multiple test categories

`$ pybot -d ../results -v testbed:mytestbed.robot -A Multiple-Suites.robot` 
