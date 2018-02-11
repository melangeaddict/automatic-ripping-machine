sudo apt-get install --yes --force-yes git
sudo add-apt-repository ppa:heyarje/makemkv-beta
sudo add-apt-repository ppa:stebbins/handbrake-releases
sudo apt update
sudo apt install --yes --force-yes makemkv-bin makemkv-oss
sudo apt install --yes --force-yes handbrake-cli libavcodec-extra
sudo apt install --yes --force-yes at
sudo apt install --yes --force-yes python3 python3-pip
sudo apt-get install --yes --force-yes libdvd-pkg
sudo dpkg-reconfigure libdvd-pkg
sudo su
cd /opt
git clone https://github.com/melangeaddict/automatic-ripping-machine.git arm
cd arm
pip3 install -r requirements.txt
ln -s /opt/arm/51-automedia.rules /lib/udev/rules.d/
cp /opt/arm/arm@.service /etc/systemd/system/
cp config.sample config.py
