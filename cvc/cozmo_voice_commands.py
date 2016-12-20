#!/usr/bin/env python3
'''
Cozmo Voice Commands (CvC) - Version 0.1.0
Author: Riccardo Sallusti - http://riccardosallusti.it
Description: Issue complex voice commands to Cozmo, and watch him execute them.
More informations: https://github.com/rizal72/Cozmo-Voice-Commands
License: GNU
'''
import sys
import os
import asyncio
import cozmo
try:
    from termcolor import colored, cprint
except ImportError:
    sys.exit('run `pip3 install --user termcolor SpeechRecognition PyAudio` to run this script\nIf you are on linux you must: `sudo apt-get install flac portaudio19-dev python-all-dev python3-all-dev && sudo pip3 install pyaudio`')
try:
    import speech_recognition as sr
except ImportError:
    sys.exit('run `pip3 install --user SpeechRecognition PyAudio` to run this script.\nIf you are on linux you must: `sudo apt-get install flac portaudio19-dev python-all-dev python3-all-dev && sudo pip3 install pyaudio`')
import cvc.voice_commands as voice_commands
'''try: #this try is needed if you want to run cvc.voice_commands.py standalone without installing cvc
    import cvc.voice_commands as voice_commands
except ImportError:
    import voice_commands'''


###### VARS ######
lang = "en"
command_activate = "Cosmo"
recognizer = sr.Recognizer()
vc = None

def main():
    clearScreen = os.system("clear")
    cozmo.setup_basic_logging()
    try:
        cozmo.connect(run)
        #cozmo.connect_with_tkviewer(run, force_on_top=True)
    except cozmo.ConnectionError as e:
        #sys.exit("A connection error occurred: %s" % e)
        cprint("A connection error occurred: %s" % e, "red")
        #ONLY FOR TESTING PURPOSES
        cprint('\nGoing on without Cozmo.', 'yellow')
        run(None)

def run(sdk_conn):
    '''The run method runs once the Cozmo SDK is connected.'''
    global vc

    if sdk_conn:
        robot = sdk_conn.wait_for_robot()
    else:
        #ONLY FOR TESTING PURPOSES
        robot = None

    vc = voice_commands.VoiceCommands(robot)

    try:
        set_language()
        cprint("You can give voice commands to Cozmo. Available Commands are:\n" + str(get_supported_commands()), "green")
        with sr.Microphone(chunk_size=512) as source:
            while 1:
                if robot:
                    checkBattery(robot)
                    flash_backpack(robot, True)
                    #robot.say_text(text="", play_excited_animation=True).wait_for_completed()
                print("\nSay something (ctrl+c to exit):")
                hear(source, robot)
    except KeyboardInterrupt:
        print("")
        cprint("Exit requested by user", "yellow")

def set_language():
    global lang

    cprint('\nCHOOSE YOUR LANGUAGE (hit "enter" for default [English]):', 'green')
    print('1: English')
    print('2: Italian')

    newLang = 0
    while not newLang:
        try:
            newLang = int(input('>>>').strip())
            if newLang not in (1, 2):
                raise ValueError
        except ValueError:
            if not newLang:
                break
            else:
                newLang = 0
                print("That's not an option!")

    if newLang == 1 or not newLang:
        lang = "en"
    elif newLang == 2:
        lang = "it"

    cprint("\nlanguage set to: " + lang + "\n", "green")

def checkBattery(robot):

    if (robot.battery_voltage <= 3.5):
        color = "red"
    else:
        color = "yellow"
    cprint("BATTERY LEVEL: %f" % robot.battery_voltage, color)


def get_supported_commands():
    '''Construct a list of all methods in this class that start with 'lang' variabler content - these are commands we accept'''
    prefix_str = lang + "_"
    prefix_len = len(prefix_str)
    supported_commands = []
    for func_name in dir(vc.__class__):
        if func_name.startswith(prefix_str):
            supported_commands.append(func_name[prefix_len:])
    return supported_commands

def get_command(command_name):
    '''Find a matching function inside 'VoiceCommands' class and return it. return None if there's no match'''
    try:
        return getattr(vc, lang + "_" + command_name.lower()) #here the magic happens
    except AttributeError:
        return None

def extract_command_from_string(in_string):
    '''Separate inString at each space, loop through until we find a command, return tuple of cmd_func and cmd_args'''

    split_string = in_string.split()

    for i in range(len(split_string)):

        cmd_func = get_command(split_string[i])

        if cmd_func:
            cmd_args = split_string[i + 1:]
            #cmd_first_int = re.search(r'\d+', cmd_args).group()
            return cmd_func, cmd_args

    # No valid command found
    return None, None

def flash_backpack(robot, flag):
    robot.set_all_backpack_lights(cozmo.lights.green_light.flash() if flag else cozmo.lights.off_light)

def hear(source, robot):
    # Speech recognition using Google Speech Recognition
    # for testing purposes, we're just using the default API key
    audio = recognizer.listen(source)
    recognized = None
    try:
        # to use another API key, use:
        #recognized = recognizer.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY", language=lang)
        recognized = recognizer.recognize_google(audio, key=None, language=lang)
        print("You said: " + recognized)
        if command_activate in recognized or command_activate.lower() in recognized:
            cprint("Action command recognized", "green")
            cmd_func, cmd_args = extract_command_from_string(recognized) #check if a corresponding command exists

            if cmd_func is not None:
                result_string = cmd_func(robot, cmd_args) #remember: cmd_func contains vc as well thanks to 'getattr', like vc.en_dance()
                if result_string:
                    print(result_string)
            else:
                cprint("Sorry I don't understand your command, available commands are:", "red")
                cprint(str(get_supported_commands()), "green")
        else:
            cprint("You did not say the magic word " + command_activate, "red")

    except sr.UnknownValueError:
        cprint("Google Speech Recognition could not understand audio", "red")
    except sr.RequestError as e:
        cprint("Could not request results from Google Speech Recognition service; {0}".format(e), "red")

#ENTRY POINT
if __name__ == "__main__":
    main()
