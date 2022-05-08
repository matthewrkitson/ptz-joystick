# Install necessary packages
sudo apt-get install git vim python3-venv i2c-tools

# Turn on i2c interface (note that 0 means "true" here)
sudo raspi-config nonint do_i2c 0

