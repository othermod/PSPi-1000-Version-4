sudo tvservice -o

python /boot/PSPi/backlight.py &

cd /home/pi/PSPi/Driver
# check resolution and create config file
cat /sys/class/graphics/fb0/virtual_size | cut -d, -f1 > pspi.cfg

# start driver
sudo ./pspi &