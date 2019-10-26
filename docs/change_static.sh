#!/bin/bash

GITHUB_PATH="http://raw.githubusercontent.com/TiagodePAlves/mc346-python/master/docs"


function change_link {
    sed -i 's|_static|'$GITHUB_PATH'/_static|g' $1
}

function remove_type {
    sed -i 's|type="text/[a-z]*"|type="text/plain"|g' $1
}

function change_html_in_dir {
    for file in $(ls $1/*.html)
    do
        change_link $file
        remove_type $file
    done
}

change_html_in_dir $1
