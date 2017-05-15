#!/bin/bash

str=TEMPLATE_COMMAND_ALIAS
sed -i "s#${str}##g" "${HOME}/.bashrc"

current_dir=TEMPLATE_COMMAND_RM
echo "Removing directory $current_dir"
rm -rf "$current_dir"

unset str
unset current_dir