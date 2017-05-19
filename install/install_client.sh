#!/bin/bash

echo "Solving dependencies for python3..."
pip3 install -r "requirements/client_requirements.txt"

if [  "$?" -eq 0 ] ; then
    echo "OK"
else
    echo "FAILED"
    exit 2
fi

install_dir="${HOME}/machi-coro-client"
alias_str='alias mc_startgame='"'""python3 ${install_dir}/game_client.py""'"

if [ -d $install_dir ] ; then
    echo "Directory $install_dir is already exists!"
    echo "Would you like to overwrite it (yes/no)?"
    response=""
    correct_response_flag=0

    while [ $correct_response_flag -ne 1 ]
    do
        read response
        for correct_response in "yes" "no"
        do
            echo "$correct_response"
            if [[ "$correct_response" == "$response" ]] ; then
                correct_response_flag=1
                break
            fi
        done

        if [ $correct_response_flag -ne 1 ] ; then
            echo "Enter 'yes' or 'no':"
        fi
    done

    if [ "$response" == "yes" ] ; then
        rm -rf "$install_dir"
    else
        install_dir="${HOME}/machi-coro-client_reinstalled"
    fi

    sed -i "s#${alias_str}##g" "${HOME}/.bashrc"

    unset response
    unset correct_response_flag
fi

echo "Creating installing directory $install_dir"
mkdir "$install_dir"

echo "Copying files..."
cp -v "../client/game_client.py" "$install_dir"
cp -v "../client/client_IO_handler.py" "$install_dir"
cp -v "uninstall_client/uninstall.sh" "$install_dir"

echo $alias_str >> "${HOME}/.bashrc"
echo $alias_str | sh -s
. "${HOME}/.bashrc"
sed -i "s#TEMPLATE_COMMAND_ALIAS#\"${alias_str}\"#g" "${install_dir}/uninstall.sh"
sed -i "s#TEMPLATE_COMMAND_RM#\"${install_dir}\"#g" "${install_dir}/uninstall.sh"

chmod +x "${install_dir}/uninstall.sh"

echo "Successful installed"

unset alias_str
unset install_dir