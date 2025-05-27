## ROBOTICS S2 2025

## PROJECT: ROBOGO

###  ANDRES ARANGUREN S4403290 / 
###  FERNANDO FEJZULLA S4534719


#  RoboGo: Modular Vision-Based Robot Navigation with Gemini LLM 



**RoboGo** is a modular robotics system built on a Raspberry Pi 4 and PiCar-4WD that uses Google's Gemini API for vision-based navigation. The robot captures its environment using a camera, interprets the scene with a Large Language Model, and autonomously moves toward a user-specified object while avoiding obstacles.

## PROJECT STRUCTURE

project/

├── main.py # entry point to launching robot job

├── camera.py # Handles Picamera2

├── gemini_utils.py # Encodes images, configures Gemini, sends prompts, parses responses

├── navigation.py # Core pursuit logic to follow objects based on Gemini advice

├── speech.py # Text-to-speech output using gTTS + mpg123

├── robot_controller.py # Robot movement control (forward, left, right, stop, etc.)


## SET GEMINI API KEY 

Set the gemini api key in your shell

```sh
export GEMINI_API_KEY="your_api_key_here"

```

## RUN THE ROBOT PIPELINE

```sh
python main.py
```
When running main.py you expect to see the following

1. Robot will describe initial scene
2. From terminal it will request to user goal object (specify the object you want the robot to look it does not have to be in the initial visual field of the robot, only make sure that is somewhere in the environment)
3. Robot will start navigating looking for the user defined object (The model is defined to a maximum of 40 iterations)
4. If the current trajectory does not looks promising getting away from the goal object then interrupt job and run again : )


## Project setup


## 1. Install Python
Ensure you have Python installed. You can check by running:
```sh
python --version
```
or
```sh
python3 --version
```

If Python is not installed, download and install it from [python.org](https://www.python.org/downloads/).

## 2. Create a Virtual Environment
Navigate to your project directory and create a virtual environment:
```sh
python -m venv myenv
```
or (for Python 3)
```sh
python3 -m venv myenv
```
## 3. Activate the Virtual Environment
### On Windows:
```sh
myenv\\Scripts\\activate
```
### On macOS and Linux:
```sh
source myenv/bin/activate
```


## 4. Install Dependencies
Once the environment is activated, install dependencies as needed, e.g.:
```sh
pip install -r requirements.txt
```






