#!/bin/bash
DIR=$HOME/.local/share/rhythmbox/plugins/YoutubeSearch
mkdir -p ${DIR}
cp -ravf YoutubeSearch.* ${DIR}
