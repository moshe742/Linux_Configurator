import os
import subprocess
import sys
import time
from pathlib import Path
from PyQt5.QtWidgets import *
from helper import *
from functools import partial

def main():
    if not is_sudo():
        print("This script must be run as root") # replace with a QMessageBox
        sys.exit()

    HOME = str(Path.home())

    """Determine the Distro and Desktop Enviroment"""
    distro = os.popen("cat /etc/*release").read()
    OS = ""
    DE = ""
    if "fedora" in distro:
        OS = "Fedora"
        if "KDE" in distro:
            DE = "KDE"
        else:
            DE = "GNOME"
    elif "ubuntu" in distro:
        OS = "Ubuntu"
        if "KDE" in distro:
            DE = "KDE"
        else:
            DE = "GNOME"



    """Determine which GPU is in the PC"""
    gpu = os.popen("lspci | grep VGA").read().lower()
    if "intel" in gpu:
        GPU = "Intel"
    elif "amd" in gpu:
        GPU = "AMD"
    elif "nvidia" in gpu:
        GPU = "Nvidia"
    else:
        GPU = "Unknown"

    """Determine if the computer is PC or a Laptop"""
    if not os.path.exists("/proc/acpi/button/lid"):
        PC = "Desktop"
    else:
        PC = "Laptop"    

    system = f"You are runnig a {PC} PC \nYour system is {OS} {DE} with {GPU} GPU."

        ### APP ###

    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle('Installer')
    window.setGeometry(400, 400, 400, 400)
    layout = QVBoxLayout()
    label = QLabel(f'{system}\n\nChoose what to install')
    cb_drivers = QCheckBox(f"Install System configs and Drivers   (Recommended)")
    cb_gpu = QCheckBox(f"Install {GPU} drivers")
    cb_dropbox = QCheckBox('Install Dropbox')
    cb_nextcloud = QCheckBox('Install NextCloud')
    cb_google = QCheckBox('Install Google Cloud')
    cb_skype = QCheckBox('Install Skype')
    cb_zoom = QCheckBox('Install Zoom')
    cb_chrome = QCheckBox('Install Chrome')
    cb_chromium = QCheckBox('Install Chromium')
        
    cb_drivers.setChecked(True)

    btn = QPushButton('Start Install')
    install_func = partial(install, cb_drivers, cb_gpu, cb_dropbox, cb_nextcloud, cb_google, cb_zoom, cb_skype, cb_chrome, cb_chromium)
    btn.clicked.connect(install_func)

    layout.addWidget(label)

    layout.addWidget(cb_drivers)
    layout.addWidget(cb_gpu)
    layout.addWidget(cb_dropbox)
    layout.addWidget(cb_nextcloud)
    layout.addWidget(cb_google)
    layout.addWidget(cb_zoom)
    layout.addWidget(cb_skype)
    layout.addWidget(cb_chrome)
    layout.addWidget(cb_chromium)


    layout.addWidget(btn)
    window.setLayout(layout)
    window.show()
    sys.exit(app.exec_())


def install(drivers, gpu, dropbox, nextcloud, google, zoom, skype, chrome, chromium): # all booleans to indicate if installation needed
    print("We need to install:")
    if drivers.checkState():
        print("Drivers") # replace with install_drivers()
    if gpu.checkState():
        print("GPU drivers") # replace with install_gpu()
    if dropbox.checkState():
        print("dropbox") # replace with install_dropbox()
    if nextcloud.checkState():
        print("nextcloud") # replace with install_nextcloud()
    if google.checkState():
        print("google") # replace with install_google()
    if zoom.checkState():
        print("zoom") # replace with install_zoom()
    if skype.checkState():
        print("skype") # replace with install_skype()
    if chrome.checkState():
        print("chrome") # replace with install_chrome()
    if chromium.checkState():
        print("chromium") # replace with install_chromium()


def install_drivers():
    if OS == "Fedora":
        run_cmd("dnf -y upgrade --refresh")
        run_cmd("dnf check")
        run_cmd("hostnamectl set-hostname fedora") # By default my machine is called localhost; hence, I rename it for better accessability on the network.

        
        # Enable RPM Fusion
        run_cmd("rpm -Uvh http://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm")
        run_cmd("rpm -Uvh http://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm")
        # Enable the RPM Fusion free and nonfree repositories.
        run_cmd("dnf groupupdate core")
        run_cmd("dnf install -y rpmfusion-free-release-tainted")
        run_cmd("dnf install -y dnf-plugins-core")

        # Enable Fastest Mirror Plugin.
        print("Enable Fastest Mirror")
        run_cmd("echo 'fastestmirror=true' | tee -a /etc/dnf/dnf.conf")
        run_cmd("echo 'max_parallel_downloads=20' | tee -a /etc/dnf/dnf.conf")
        run_cmd("echo 'deltarpm=true' | tee -a /etc/dnf/dnf.conf")

        # Install Flatpak, Snap and Fedy
        print("Install Flatpak, Snap and Fedy")
        run_cmd("flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo")
        run_cmd("flatpak update")
        run_cmd("dnf install -y snapd")
        run_cmd("ln -s /var/lib/snapd/snap /snap") # "sudo snap refresh" AFTER REBOOT # for classic snap support
        run_cmd("dnf copr enable kwizart/fedy")
        run_cmd("dnf install -y fedy")
        run_cmd("flatpak install -y flatseal")
        
        # Install Codecs and VLC.
        print("Install Codecs and VLC")
        run_cmd("dnf install -y vlc")
        run_cmd("dnf groupupdate sound-and-video")
        run_cmd("dnf install -y libdvdcss")
        run_cmd("dnf install -y lame\* --exclude=lame-devel")
        run_cmd("dnf group upgrade --with-optional Multimedia")
        run_cmd("dnf config-manager --set-enabled fedora-cisco-openh264")
        run_cmd("dnf install -y gstreamer1-plugin-openh264 mozilla-openh264")  
        
        # Update disk drivers.
        run_cmd("fwupdmgr refresh --force")
        if "WARNING:" in subprocess.getoutput('fwupdmgr get-updates'):
            print("true")
            run_cmd("echo 'DisabledPlugins=test;invalid;uefi' | tee -a /etc/fwupd/daemon.conf") # Remove WARNING: Firmware can not be updated in legacy BIOS mode.
        run_cmd("fwupdmgr get-updates")
        run_cmd("fwupdmgr update")
    
    elif OS == "Ubuntu":
        
        # Update system.
        run_cmd("apt update")
        run_cmd("apt -y upgrade")
        run_cmd("apt -y dist-upgrade")
        run_cmd("apt autoremove") # -y ??
        run_cmd("apt autoclean") # -y ??
        
        # Update disk drivers.
        run_cmd("fwupdmgr get-devices")
        run_cmd("fwupdmgr get-updates")
        run_cmd("fwupdmgr update")
        # run_cmd("reboot now") # Nedds to save STATE if enable reboot.
        
        # System Utilities.
        run_cmd("apt install -y snapd")
        run_cmd("apt install -y flatpak")
        run_cmd("flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo")
        run_cmd("flatpak install flatseal") # Tool to check or change the permissions of your flatpaks
        run_cmd("apt install -y nautilus-admin")
        run_cmd("apt install -y caffeine") # A little helper in case my laptop needs to stay up all night
        
        # Install Codecs and VLC.
        run_cmd("apt install -y vlc")
        run_cmd("apt install -y libavcodec-extra libdvd-pkg; dpkg-reconfigure libdvd-pkg")
        
      
    elif PC == "Laptop":
        
        if OS == "Fedora":
            # Reduce Battery Usage - TLP.
            run_cmd("dnf install -y tlp tlp-rdw")
            run_cmd("systemctl enable tlp")
            
        if OS == "Ubuntu":
            run_cmd("add-apt-repository ppa:linuxuprising/apps") # -y ??
            run_cmd("apt-get update")
            run_cmd("apt-get install tlp tlpui")
            run_cmd("tlp start")

def install_gpu():

    if GPU == "Nvidia":
        run_cmd("modinfo -F version nvidia")
        run_cmd("dnf install -y akmod-nvidia") # rhel/centos users can use kmod-nvidia instead
        run_cmd("dnf install -y xorg-x11-drv-nvidia-cuda") #optional for cuda/nvdec/nvenc support
        run_cmd("dnf install -y xorg-x11-drv-nvidia-cuda-libs")
        run_cmd("dnf install -y vdpauinfo libva-vdpau-driver libva-utils")
        run_cmd("dnf install -y vulkan")
        run_cmd("modinfo -F version nvidia")
    
    #elif GPU == "AMD": # Disable for now until we have installation process
        #run_cmd("dnf install -y xorg-x11-drv-amdgpu.x86_64")
        
        # Creats AMD_GPU file to X11 config, *NEED TO TEST IT BEFORE!
        #run_cmd('Section "Device"\n\tIdentifier "AMD"\n\tDriver "amdgpu"\nEndSection" > /etc/X11/xorg.conf.d/20-amdgpu.conf') 

    #elif GPU == "Intel": Disable for now until we have installation process    
 
def install_dropbox():
    if OS == "Fedora":
        run_cmd("dnf install -y dropbox nautilus-dropbox")

    elif OS == "Ubuntu":
        run_cmd("apt install -y nautilus-dropbox")
        
def install_nextcloud():
    if OS == "Fedora":
        run_cmd("dnf install -y nextcloud-client nextcloud-client-nautilus")
        run_cmd("-i")
        run_cmd("echo 'fs.inotify.max_user_watches = 524288' >> /etc/sysctl.conf")
        run_cmd("sysctl -p")
        
    elif OS == "Ubuntu":
        run_cmd("apt install -y nextcloud-desktop")
        

def install_google():
    run_cmd("dnf install -y python3-devel python3-pip python3-inotify python3-gobject cairo-devel cairo-gobject-devel libappindicator-gtk3")
    run_cmd("python3 -m pip install --upgrade google-api-python-client")
    run_cmd("python3 -m pip install --upgrade oauth2client")
    run_cmd("yum install -y overgrive-3.3.*.noarch.rpm")

def install_skype():
    run_cmd("flatpak install -y skype")

def install_zoom():    
    run_cmd("flatpak install -y zoom")
        
def install_chrome():
    if OS == "Fedora":
        run_cmd("dnf install -y fedora-workstation-repositories")
        run_cmd("dnf config-manager --set-enabled google-chrome")
        run_cmd("dnf install -y google-chrome-stable")
        
    elif OS == "Ubuntu":
        run_cmd("wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
        run_cmd("dpkg -i google-chrome-stable_current_amd64.deb")
        
def install_chromium():
    if OS == "Fedora":
        run_cmd("dnf install -y chromium")
        
    elif OS == "Ubuntu":
        run_cmd("apt install -y chromium-browser")

if __name__ == "__main__":
    main()