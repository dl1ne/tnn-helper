# tnn-helper
Programm für den TNN-Digi mit WebUI.
Der Helper dient dazu, dass mögliche Links zu anderen Digis automatisch auf den TNN gepushed werden. 
Hierzu ist die angepasste Version vom TNN notwendig, in welcher Web-Anfragen über Localhost/127.0.0.1 direkt als Sysop behandelt werden.


`
#####################################################
#               INSTALLATION GUIDE                  #
#####################################################

# update package lists
apt-get update

# install git, python3-pip
apt-get install git python3-pip -y

# install python packages
pip3 install requests pythonping psutil

# clone tnn-helper script
cd /usr/local/src
git clone https://github.com/dl1ne/tnn-helper.git

# find python3 binary
P=`which python3`

# install tnn-helper inside crontab
echo "MAILTO=root" > /etc/cron.d/tnn-helper
echo "00 */12 * * *  root $P /usr/local/src/tnn-helper/helper.py" >> /etc/cron.d/tnn-helper

# restart crond
systemctl restart cron
`

