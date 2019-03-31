#!/bin/bash

if [ -z "$1" ]; then
    URL="https://www.amctheatres.com/movie-theatres/san-jose/amc-mercado-20/showtimes/all/2019-04-25/amc-mercado-20/all"
else
    URL="$1"
fi

EMAIL_CONTENTS="Subject: Avengers On Sale!\n\n$URL"
EMAIL_RECIPIENT="j.belleville.richard@gmail.com"
INTERVAL=10
MOVIE_REGEX='avengers.*endgame'

while true; do
    curl -s "$URL" | egrep -i "<h2 data-reactid=.*>.*${MOVIE_REGEX}.*</h2>" && \
    printf "$EMAIL_CONTENTS" | sendmail -v $EMAIL_RECIPIENT && \
    break

    echo "Avengers not yet on sale."
    sleep $INTERVAL
done

echo "Avengers on sale! Go! Go! Go!"
