#!/bin/bash

## Defaults
PORT=8000
PASSWORD=

## Load web2py configuration file, if exists
[ -f ~/web2py-settings ] && . ~/web2py-settings

while getopts "p:a:h" OPTION; do
    case "$OPTION" in
	p)
	    PORT="$OPTARG"
	    ;;
	a)
	    PASSWORD="$OPTARG"
	    ;;
	h)
	    echo "Usage: launch-web2py.sh [-p port] [-a password] [-h]"
	    exit
	    ;;
	*)
	    echo "Use -h to get help"
	    exit 1
	    ;;
    esac
done

## Ask for settings interactively
if [ -z "$PASSWORD" ]; then
    stty -echo 
    read -p "Password: " PASSWORD; echo
    stty echo
fi

if [ -z "$PORT" ]; then
    read -p "Port: " PORT
fi

## Save settings
cat > ~/web2py-settings <<EOF
## Autogenerated on $(date)
PORT=$PORT
PASSWORD=$PASSWORD
EOF

## Launch web2py
"$( dirname "$0" )"/../web2py/web2py.py -p "$PORT" -a "$PASSWORD"