Django project for an extension to leaguevine.com in order to handle WFDF spirit scores.

initiated in March 2013 by Christian Schaffner, huebli@gmail.com

Comments:
* This extension is set up without django-database. 
* Hopefully it will be deployed at http://spirit.leaguevine.com at some point...
* for now, it's deployed at http://spiritapp.herokuapp.com 


Goal:
Have this ready for Windmill Windup 2013, taking place 
http://www.windmillwindup.com/2013/


Instructions for deploying in a development environment:
* Goto https://www.leaguevine.com/apps/ and click on create a new app
* set Redirect URI to http://127.0.0.1:8000/code/ 
* set environmental variables CLIENT_ID and CLIENT_PWD (Client Secret Key) and REDIRECT_URI
  to the values provided for the leaguevine app. Those values are read in settings.py

if you want to use the playwithlv.com server, you have to repeat the above steps for:
* Goto http://www.playwithlv.com/apps/create/ and click on create a new app
* set Redirect URI to http://127.0.0.1:8000/code/ 
* set environmental variables CLIENT_ID_PLAYWITHLV and CLIENT_PWD_PLAYWITHLV (Client Secret Key) 
  to the values provided for the leaguevine app. Those values are read in settings.py

