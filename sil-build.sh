#!/bin/bash

# Stuart's build script. Yes.
# Basically this is here to confirm that Stuart remembered to update __VERSION__ in __main__.py

PYV=$(grep "__VERSION__ =" pick/__main__.py | cut -d'"' -f2)
SNAPV=$(grep '^version:' snapcraft.yaml | cut -d'"' -f2)

if [ A$PYV != A$SNAPV ]; then
    echo The versions from snapcraft.yaml and pick/__main__.py differ. Fix it.
    exit 1
fi

echo Building version $SNAPV as snap
snapcraft --debug


