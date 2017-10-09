#! /bin/sh

rm sources .gitignore
set -e
spectool -S *.spec | cut -d' ' -f2 \
    | grep -E -e 'postgis-.*\.tar\.*' -e 'postgis.*\.pdf' | sort | \
while read line
do
    base=`basename "$line"`
    echo " * handling $base"
    sha512sum --tag "$base" >> sources
    echo "/$base" >> .gitignore
done
