#!/bin/bash

echo "Installing dependencies..."
sudo apt-get install python-dev python-pip || { echo "Failed to install dependencies. Quiting." ; exit 1; }
sudo -H pip install -U pygame || { echo "Failed install python dependencies. Quiting." ; exit 1; }
mkdir ~/cylgameenv
cd ~/cylgameenv
clear
echo "Finished installing dependencies."
echo "Cloning Framework..."
echo "Enter your x500 (your UMD email without the @d.umn.edu) and your UMD password when prompted"
CYLGameFrameworkPath="`pwd`/CYLGameFramework"
if [ -d "$CYLGameFrameworkPath" ]
then
    cd ${CYLGameFrameworkPath}
    git pull origin master || { echo "Failed to update framework. Quiting." ; exit 1; }
    cd ..
else
    git clone https://github.umn.edu/UMDCYL/CYLGameServer.git CYLGameFramework || { echo "Failed to clone framework repo. Quiting." ; exit 1; }
fi


NewLine="export PYTHONPATH=\"$CYLGameFrameworkPath:\$PYTHONPATH\""
if grep "$NewLine" ~/.bashrc &> /dev/null
then
    echo "Good to go."
else
    echo $NewLine >> ~/.bashrc
    echo "Good to go."
    echo "Remember to run to following command to make changes apply in the currect session:"
    echo "source ~/.bashrc"
fi
