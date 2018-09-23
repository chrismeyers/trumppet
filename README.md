# trumppet
trumppet periodically retrieves tweets from Donald Trump 
([@realDonaldTrump](https://twitter.com/realDonaldTrump)) and stores the data in
a MongoDB database. Linguistic analysis is then performed on this data.

## Usage
This project is comprised of four components: trumppet-client, trumppet-server,
a Flask REST API connecting the two, and a website.

```
Usage: trumppet-client [OPTIONS] COMMAND [ARGS]...

  Client component of a Donald Trump tweet analyzer. This application
  displays data retrieved from the server component through HTTP requests.

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  freestyle  generates a Trumpian-style tweet: Sentance. Sentance.
             Exclamation! (NOTE: these tweets are not real)
  frequency  get unique word counts
  playback   prints previous tweets
  search     searches tweets for usage of a word or phrase
```

```
Usage: trumppet-server [OPTIONS] COMMAND [ARGS]...

  Server component of a Donald Trump tweet analyzer. This application
  manages the insertion of data into a MongoDB database from data received
  through the Twitter API.

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  catalog  fetch and store all possible tweets
  record   fetch and store latest tweets
```

**API Endpoints**

| HTTP Method    | URI               | Action                                 |
| -------------- | ----------------- | -------------------------------------- |
| GET            | /tweets/\<num\>   | Return the last \<num\> tweets, max 50 |
| GET            | /frequency        | Gets word frequency statistics         |
| POST           | /search           | Gets tweets matching the given phrase  |
| GET            | /freestyle        | Gets a fake Trumpian-style tweet       |

**Endpoint examples**
  * https://api.trumppetapp.com/tweets/10
  * https://api.trumppetapp.com/freestyle

## Requirements
  * Python3 >= 3.6
  * pipenv
  * (Optional) MongoDB

## Setup
Create a virtual environment and install dependencies by running `pipenv install`
from the root of the project.

### Client Setup
Copy and configure the following files:
```
cp trumppetclient/config/trumppetclient_config_template.json trumppetclient/config/trumppetclient_config.json
```

Invoke the client by running `pipenv run trumppet-client ...` from within the
project, or `bin/trumppetClientWrapper.sh ...` from anywhere.  

### (Optional) Server Configuration
Copy and configure the following files:
```
cp trumppetserver/config/trumppetserver_config_template.json trumppetserver/config/trumppetserver_config.json
```

Invoke the server by running `pipenv run trumppet-server ...` from within the
project, or `bin/trumppetServerWrapper.sh ...` from anywhere.  

Now, the Flask API server needs to be configured:
* For development, a local Flask server can be used by running `pipenv run python3 trumppetserver/api.py`
  from within the project.  Make sure the `trumppetserver -> base_url -> custom `
  field in `truppetclient/config/trumppetclient_config.json` is set to the
  location of the custom Flask server (probably `http://localhost:5000`)
+ For production, the Flask server can be tied to Apache through mod_wsgi.  Make
  sure the version of mod_wsgi is configured for Python 3.  For Ubuntu, it's
  easier to build and install Python and mod_wsgi from source.  These directions
  are based on Ubuntu server 16.04.
  * First, [build and install Python](https://solarianprogrammer.com/2017/06/30/building-python-ubuntu-wsl-debian/)<sup>1</sup>
    (replace Python versions with latest) using `./configure --enable-shared --enable-optimizations`.
  + Then, [build and install mod_wsgi](http://modwsgi.readthedocs.io/en/develop/user-guides/quick-installation-guide.html)<sup>2</sup>
    using `./configure --with-python=/path/to/python3`.
    * More information about configuring mod_wsgi with virtual environments
      can be found [here](http://modwsgi.readthedocs.io/en/develop/user-guides/virtual-environments.html).
  + Enable mod_wsgi:
    * Run: `sudo echo LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so > /etc/apache2/mods-available/mod_wsgi.load`
    * Run: `sudo a2enmod mod_wsgi`
  * Add a virtual host entry in the file `/etc/apache2/sites-available/VHOST_NAME.conf`:
```
<VirtualHost *:80>
  ...

  ServerName api.website.com

  WSGIDaemonProcess WSGI_HANDLE python-home=/path/to/virtualenvs/trumppet-XXXXXXX
  WSGIScriptAlias / /path/to/trumppet/trumppetserver/wsgi.py

  <Directory /path/to/trumppet/trumppetserver>
      WSGIProcessGroup WSGI_HANDLE
      WSGIApplicationGroup %{GLOBAL}
      Require all granted
  </Directory>

  ...
</VirtualHost>
```
  * Enable the new virtual host by running `sudo a2ensite VHOST_NAME.conf`
  + Finally, test the Apache config (`sudo apachectl -t`), then restart Apache (`sudo apachectl restart`).
    * NOTE: Whenever there are changes to the server code, Apache needs to be restarted.

### Cron Setup
To configure a cron job that runs every 15 minutes, use the following command:
```
*/15 * * * * export PATH="/python/user/base/directory/bin:$PATH"; export LANG="en_US.UTF-8"; echo `date` >> /path/to/log 2>&1; /path/to/trumppet/bin/trumppetServerWrapper.sh record >> /path/to/log 2>&1
```
NOTE: The python user base directory can be located by running `python3 -m site --user-base`.

### MongoDB Authentication
Authentication can be enabled by adding the following to the mongodb.conf:
```
security:
  authorization: enabled
```
User creation instructions can be found [here](https://docs.mongodb.com/manual/tutorial/enable-authentication/).

Make sure `trumppetserver/config/trumppetserver_config.json` is configured.

## Additional Information
<sup>1</sup> Python build instructions:
```
sudo apt-get update
sudo apt-get upgrade

sudo apt-get install build-essential
sudo apt-get install libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev 
sudo apt-get install libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev tk-dev libffi-dev

sudo wget https://www.python.org/ftp/python/X.Y.Z/Python-X.Y.Z.tar.xz
sudo tar xf Python-X.Y.Z.tar.xz
cd Python-X.Y.Z
sudo ./configure --enable-shared --enable-optimizations
sudo make -j 8
sudo make altinstall

# If there are errors running 'pythonX.Y --version' run:
sudo ln -s /usr/local/lib/libpythonX.Ym.so.1.0 /usr/lib/libpythonX.Ym.so.1.0
```

<sup>2</sup> mod_wsgi build instructions:
```
sudo wget https://github.com/GrahamDumpleton/mod_wsgi/archive/X.Y.Z.tar.gz
sudo mv X.Y.Z.tar.gz mod_wsgi-X.Y.Z.tar.gz
sudo tar xvfz mod_wsgi-X.Y.Z.tar.gz

cd mod_wsgi-X.Y.Z
sudo ./configure --with-python=/path/to/python3
sudo make
sudo make install

# If there are build errors, try installing:
sudo apt-get install apache2-dev
```
