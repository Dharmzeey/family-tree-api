import os
# THIS WILL TRY TO GET THE OS ENV VARIABLE OR SET TO NONE IF IT DOES NOT EXISTS
get_os = os.environ.get("SITE_STATUS", None)
# THIS WILL LOAD THE DEVELOPMENT SETTINGS IF THE VALUE IS NONE
if get_os is None:
  from .development import * 
# THIS WILL LOAD THE DEVELOPMENT SETTINGS IF THE SITE_STATUS KEY RETURNS A VALUE [(PROD) THAT IN SET ON THE WEB SERVER OS]
# elif get_os == "production":
#   from .production import *
#   import pymysql
#   pymysql.install_as_MySQLdb()