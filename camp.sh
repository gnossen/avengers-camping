#!/bin/bash

if [ -z "$1" ]; then
    URL="https://www.amctheatres.com/movie-theatres/san-jose/amc-mercado-20/showtimes/all/2019-04-25/amc-mercado-20/all"
else
    URL="$1"
fi

EMAIL_CONTENTS="Subject: Avengers On Sale!\n\n$URL"
EMAIL_RECIPIENT="j.belleville.richard@gmail.com"
INTERVAL=10

while true; do
    curl -s "$URL" | grep -i "endgame" && \
    printf "$EMAIL_CONTENTS" | sendmail -v $EMAIL_RECIPIENT && \
    break

    echo "Avengers not yet on sale."
    sleep $INTERVAL
done

echo "Avengers on sale! Go! Go! Go!"
