# trumppet
trumppet periodically retrieves tweets from Donald Trump 
([@realDonaldTrump](https://twitter.com/realDonaldTrump)) and stores the data in
a MongoDB database. Linguistic analysis is then performed on this data.

## Usage
This project is comprised of three components: trumppet-client, trumppet-server,
and a Flask RESTful API connecting the two.

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

API Endpoints

| HTTP Method    | URI               | Action                                 |
| -------------- | ----------------- | -------------------------------------- |
| GET            | /tweets/\<num\>   | Return the last \<num\> tweets, max 50 |
| GET            | /frequency        | Gets word frequency statistics         |
| POST           | /search           | Gets tweets matching the given phrase  |
| GET            | /freestyle        | Gets a fake Trumpian-style tweet       |

## Requirements
  * Python3 >= 3.6
  * pipenv
  * (Optional) MongoDB

## Setup
Create a virtual environment and install dependencies by running `pipenv install`
from the root of the project.

Copy and configure the following files:
```
cp trumppetclient/config/trumppetclient_config_template.json trumppetclient/config/trumppetclient_config.json
cp trumppetserver/config/trumppetserver_config_template.json trumppetserver/config/trumppetserver_config.json
```
NOTE: `trumppetserver_config.json` only needs to be configured if  MongoDB is
running locally.

Invoke the client by running `pipenv run trumppet-client ...` from within the
project, or `bin/trumppetClientWrapper.sh ...` from anywhere.  

Invoke the server by running `pipenv run trumppet-server ...` from within the
project, or `bin/trumppetServerWrapper.sh ...` from anywhere.  NOTE: If a local
MongoDB instance is being used, the Flask API needs to be started by running
`pipenv run python3 trumppetserver/api.py` from within the project.  Also, the
`trumppetserver -> base_url -> custom ` field in `truppetclient/config/trumppetclient_config.json`
needs to be set to the location of the local server (probably `http://localhost:5000`)

To configure an hourly cron job, use the following command:
```
0 * * * * export PATH="/python/user/base/directory/bin:$PATH"; export LANG="en_US.UTF-8"; echo `date` >> /path/to/log 2>&1; /path/to/trumppet/bin/trumppetServerWrapper.sh record >> /path/to/log 2>&1
```

## Meaning of 'trumppet'
trumppet stands for trump-puppet. Trumpet also works because, like the musical
instrument, President Trump often just makes noise and is full of hot air.
