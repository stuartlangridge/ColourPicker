#!/bin/bash

# Stuart's build script. Yes.
# Basically this is here to confirm that Stuart remembered to update __VERSION__ in __main__.py

PYV=$(grep "__VERSION__ =" pick/__main__.py | cut -d'"' -f2)
DEBV=$(dpkg-parsechangelog --show-field=Version)

if [ A$PYV != A$DEBV ]; then
    echo The versions from the Debian changelog and pick/__main__.py differ. Fix it.
    exit 1
fi

echo Building version $DEBV
debuild > /dev/null

