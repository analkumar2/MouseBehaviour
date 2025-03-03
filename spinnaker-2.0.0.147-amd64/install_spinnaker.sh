#!/bin/bash

set -o errexit

MY_YESNO_PROMPT='[Y/n] $ '

# Web page links
FEEDBACK_PAGE='https://www.flir.com/spinnaker/survey'

echo "This is a script to assist with installation of the Spinnaker SDK."
echo "Would you like to continue and install all the Spinnaker SDK packages?"
echo -n "$MY_YESNO_PROMPT"
read confirm
if ! ( [ "$confirm" = "y" ] || [ "$confirm" = "Y" ] || [ "$confirm" = "yes" ] || [ "$confirm" = "Yes" ] || [ "$confirm" = "" ] )
then
    exit 0
fi

echo
echo "Installing Spinnaker packages..."

sudo dpkg -i libspinnaker_*.deb
sudo dpkg -i libspinnaker-dev_*.deb
sudo dpkg -i libspinnaker-c_*.deb
sudo dpkg -i libspinnaker-c-dev_*.deb
sudo dpkg -i libspinvideo_*.deb
sudo dpkg -i libspinvideo-dev_*.deb
sudo dpkg -i libspinvideo-c_*.deb
sudo dpkg -i libspinvideo-c-dev_*.deb
sudo dpkg -i spinview-qt_*.deb
sudo dpkg -i spinview-qt-dev_*.deb
sudo dpkg -i spinupdate_*.deb
sudo dpkg -i spinupdate-dev_*.deb
sudo dpkg -i spinnaker_*.deb
sudo dpkg -i spinnaker-doc_*.deb

echo
echo "Would you like to add a udev entry to allow access to USB hardware?"
echo "  If a udev entry is not added, your cameras may only be accessible by running Spinnaker as sudo."
echo -n "$MY_YESNO_PROMPT"
read confirm
if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ] || [ "$confirm" = "yes" ] || [ "$confirm" = "Yes" ] || [ "$confirm" = "" ]
then
    echo "Launching udev configuration script..."
    sudo sh configure_spinnaker.sh
fi

echo
echo "Would you like to set USB-FS memory size to 1000 MB at startup (via /etc/rc.local)?"
echo "  By default, Linux systems only allocate 16 MB of USB-FS buffer memory for all USB devices."
echo "  This may result in image acquisition issues from high-resolution cameras or multiple-camera set ups."
echo "  NOTE: You can set this at any time by following the USB notes in the included README."
echo -n "$MY_YESNO_PROMPT"
read confirm
if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ] || [ "$confirm" = "yes" ] || [ "$confirm" = "Yes" ] || [ "$confirm" = "" ]
then
    echo "Launching USB-FS configuration script..."
    sudo sh configure_usbfs.sh
fi

echo
echo "Installation complete."

echo
echo "Would you like to make a difference by participating in the Spinnaker feedback program?"
echo -n "$MY_YESNO_PROMPT"
read confirm
if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ] || [ "$confirm" = "yes" ] || [ "$confirm" = "Yes" ] || [ "$confirm" = "" ]
then
    feedback_link_msg="Please visit \"$FEEDBACK_PAGE\" to join our feedback program!"
    if [ $(id -u) -ne 0 ]
    then
        set +o errexit
        has_display=$(xdg-open $FEEDBACK_PAGE 2> /dev/null && echo "ok")
        set -o errexit
        if [ "$has_display" != "ok" ]
        then
            echo $feedback_link_msg
        fi
    elif [ "$PPID" -ne 0 ]
    then
        # Script is run as sudo. Find the actual user name.
        gpid=$(ps --no-heading -o ppid -p $PPID)
        if [ "$gpid" -ne 0 ]
        then
            supid=$(ps --no-heading -o ppid -p $gpid)
            if [ "$supid" -ne 0 ]
            then
                user=$(ps --no-heading -o user -p $supid)
            fi
        fi

        if [ -z "$user" ] || [ "$user" = "root" ]
        then
            # Root user does not have graphical capabilities.
            echo $feedback_link_msg
        else
            set +o errexit
            has_display=$(su $user xdg-open $FEEDBACK_PAGE 2> /dev/null && echo "ok")
            set -o errexit
            if [ "$has_display" != "ok" ]
            then
                echo $feedback_link_msg
            fi
        fi
    else
        echo $feedback_link_msg
    fi
else
    echo "Join the feedback program anytime at \"$FEEDBACK_PAGE\"!"
fi

echo "Thank you for installing the Spinnaker SDK."
exit 0
