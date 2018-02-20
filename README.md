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

## Meaning of 'trumppet'
trumppet stands for trump-puppet. Trumpet also works because, like the musical
instrument, President Trump often just makes noise and is full of hot air.
