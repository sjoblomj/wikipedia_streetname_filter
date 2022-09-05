#!/bin/bash

dir=$(pwd)
docker-compose up -d

cd dbserver
mvn clean install

filename=sweden-latest.osm.pbf
if [ $# -eq 1 ]; then
    filename=$1
fi
if [ ! -f "${filename}" ]; then
    echo ""
    echo ""
    echo ""
    read -p "File ${filename} not found, do you want to download it? (Roughly 600mb download) (y/N) " confirm
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        curl https://download.geofabrik.de/europe/sweden-latest.osm.pbf -o "${filename}"
    fi
fi

java -jar target/dbserver*.jar &

# Loop until server is up
server_is_up=0
for i in {1..256}; do
    if [ $(curl -s -o /dev/null -w "%{http_code}" localhost:7171/isRunning) -eq 200 ]; then
        server_is_up=1
        echo "dbserver is up"
        echo ""
        break
    else
        sleep 1
    fi
done

curl -X POST "http://localhost:7171/consume?filename=${filename}"

cd ..
./streetname_filter.py

cd "${dir}"
