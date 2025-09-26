# Ren-Guard

Made in Python for Raspberry Pi 4

Outputs:
- Detects a recycle object
- Deposits it in the correct bin
- Saves all objects in a separated webpage

## Table of Contents
- Requirements
- Installation
- Configuration
- How It Works

## Requirements
- [Raspberry Pi 4](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/)
- Any Compatible Camera
- MicroSD card(>32gb)
- [Raspberry Pi OS(64 bit)](https://www.raspberrypi.com/software/)
- Ultralytics
- OpenCV
- Numpy
- PiCamera2
- 

### Optional
- Visual Studio Code
- 

## Installation
- Install the Raspberry Pi imager from the website
- Make sure you have the MicroSD card plug in the pc
- Run Raspberry Pi imager and select Raspberry Pi 4>Raspberry Pi OS (64bit) version>MicroSD
- Click Next and Configure manually the OS settings
- After Configurating the settings Click Next and install the OS
- Plug the MicroSD in the Raspberry Pi 4
- **!** After Configuration - Install the correct Libraries on terminal
    - sudo apt update && sudo apt upgrade -y
    - sudo apt install python3-pip python3-opencv python3-picamera2 libcamera-apps -y pip install ultralytics numpy opencv-python
- **!** Some Libraries might need to be installed in an environment depending on the version of the OS.

## Configuration
- Connect the Raspberry Pi 4 to a monitor and powersource
- Plug in on the correct pins the Servo Motors and the Camera
- Install all the Hardware on its apropriate place in the desired 3d Models
- Put all files in a Folder in the Raspberry Pi 4
- To make sure the Camera is running properly run the code: "sudo python yolo_detect.py --model=yolo11n_ncnn_model --source="Port of the camera" --resolution=1280x720"
- **!**After everything is installed properly, simply run the main code: "sudo python detect.py"

## How It Works
- The user will place a object on the bin
- The camera will detect the object and identify it
- Than the program will save the object detected
- The servos will turn and deposit the object in the correct place
- The website will receive the information of the object and display it
