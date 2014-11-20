Apache Flask Configuration
====
* Source: [article](https://beagle.whoi.edu/redmine/projects/ibt/wiki/Deploying_Flask_Apps_with_Apache_and_Mod_WSGI)
* Source stackoverflow: [article](http://stackoverflow.com/questions/17386971/hello-world-flask-apache-mod-wsgi-no-response-from-apache)

Project Structure
========

using pip install (or copy and paste the folders)

* /usr/lib/python2.7/pgeo
* /usr/lib/python2.7/pgeorest
    
Apache Configuration
========
Edit file /etc/apache2/ports.conf 

ServerName it's the key parameter. This should be the DNS name or current IP. With a wrong IP or DNS ServerName apache would start but the URL would be unreachable. N.B. NO ERRORS are thrown by apache with this configuration error.

```script
#WSGIRestrictStdout Off
#WSGIRestrictSignal Off
#WSGISocketPrefix /var/run/wsgi
<VirtualHost *:80>
    ServerName 168.202.28.214
    LogLevel info	
    WSGIDaemonProcess pgeorest_main user=vortex group=vortex threads=5
    WSGIScriptAlias /pgeo /var/www/html/pgeorest_main/pgeorest_main.wsgi
    ErrorLog /var/www/html/pgeorest_main/error.log   
    CustomLog /var/www/html/pgeorest_main/access.log combined
    <Directory "/var/www/html/pgeorest_main/">
        WSGIProcessGroup pgeorest_main
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
</VirtualHost>
```

WSGI Configuration
========
Create file *pgeo.wsgi* in the */var/www/public_html/wsgi* folder
if the application is deployed as a package, write in the file:
```python
from pgeorest.pgeorest_main import app as application
```

N.B.
========
the "main.py" called by the pgeorest_main.wsgi should not contain:

```python
if __name__ == '__main__':
    app.run(host=settings['host'], port=settings['port'], debug=settings['debug'], threaded=True)
```
