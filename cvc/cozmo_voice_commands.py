#!/usr/bin/env python3
'''
Cozmo Voice Commands (CvC)
Author: Riccardo Sallusti - http://riccardosallusti.it
Description: Issue complex voice commands to Cozmo, and watch him execute them.
More informations: https://github.com/rizal72/Cozmo-Voice-Commands
License: GNU
'''
import sys
import os
import asyncio
import operator
import glob
import json

import cozmo

try:
    from termcolor import colored, cprint
    from pynput.keyboard import Key, Listener
    import speech_recognition as sr
except ImportError:
    sys.exit('some packages are required, install them doing: `pip3 install --user termcolor SpeechRecognition PyAudio Pynput` to run this script.\nIf you are on linux do: `sudo apt-get install flac portaudio19-dev python-all-dev python3-all-dev && sudo pip3 install Pynput pyaudio`')

from . import voice_commands

###### VARS ######
version = "Version 0.6.8"
title = "Cozmo-Voice-Commands (CvC) - " + version
author =" - Riccardo Sallusti (http://riccardosallusti.it)"
log = False
wait_for_shift = True
lang = None
lang_data = None
commands_activate = ["cozmo", "robot", "cosmo", "cosimo", "cosma", "cosima", "kosmos", "cosmos", "cosmic", "osmo", "kosovo", "peau", "kosmo", "kozmo", "gizmo"]
vc = None
languages = []

##### MAIN ######
def main():
    parse_arguments()
    clearScreen = os.system('cls' if os.name == 'nt' else 'clear')
    cprint(title, "green", attrs=['bold'], end='')
    cprint(author, "cyan")
    cozmo.robot.Robot.drive_off_charger_on_connect = False


    try:
        cozmo.run_program(run)
        #cozmo.run_program(run, use_viewer=True, force_viewer_on_top=True)
    except SystemExit as e:
        print('exception = "%s"' % e)
        #ONLY FOR TESTING PURPOSES
        cprint('\nGoing on without Cozmo: for testing purposes only!', 'red')
        run(None)

##### APP ######
def run(robot: cozmo.robot.Robot):
    '''The run method runs once the Cozmo SDK is connected.'''
    global vc

    vc = voice_commands.VoiceCommands(robot,log)

    def on_press(key):
        #print('{0} pressed'.format(key))
        if key == Key.shift_l or key == Key.shift_r:
            listen(robot)

    def on_release(key):
        #print('{0} release'.format(key))
        if key == Key.shift_l or key == Key.shift_r:
            #listen(robot)
            pass

    if robot:
        vc.check_charger(robot)
        robot.play_anim("anim_cozmosays_getout_short_01")

    try:
        load_jsons()
        set_language()
        set_data()
        printSupportedCommands()
        prompt()

        if wait_for_shift:
            with Listener(on_press=on_press, on_release=on_release) as listener:
                listener.join()
        else:
            while 1:
                listen(robot)

    except KeyboardInterrupt:
        print("")
        cprint("Exit requested by user", "yellow")

def load_jsons():
    global languages
    cprint("\nloading languages files...","yellow")
    package_location = os.path.dirname(os.path.realpath(__file__))
    relative_location = 'languages/*.json'
    absolute_location =  package_location + "/" + relative_location

    if log:
        print("Package Location: " + package_location + "\nRelative location: " + relative_location)

    for file in glob.glob(absolute_location):
        with open(file) as json_file:
            languages.append(json.load(json_file))
            if (log):
                cprint("loaded: " + str(file) + " ", "yellow")

    '''ALT VERSION
    for file in glob.glob(absolute_location):
        with open(file) as json_file:
            filename = file.rpartition("/")[-1] #get filename from path
            id = int(filename[0]) #get index from filename
            languages.insert(id-1, json.load(json_file)) #insert json at index
            cprint("loaded: " + str(filename) + " ", "yellow")
    '''

    if len(languages) == 0:
        cprint("\nno languages found! Quitting...", "red")
        sys.exit()
    else:
        #languages = sorted(languages, key=lambda k: k['id']) #sort lang by ID
        languages.sort(key=operator.itemgetter('id'))

    #if log:
    #    print("LANGUAGES:\n"+str(languages))

def set_language():
    global lang, lang_ext, lang_data

    cprint('\nCHOOSE YOUR LANGUAGE (hit "enter" for default [English]):', 'green')
    for i in range(len(languages)):
        print(i+1, end='')
        print(". " + str(languages[i]['name']))

    lang = 0
    while not lang:
        try:
            lang = int(input('>>> ').strip())
            if lang not in range(1,len(languages)+1):
                raise ValueError
        except ValueError:
            if not lang:
                break
            else:
                lang = 0
                cprint("That's not an option!", "red")

    if lang == 1 or not lang:
        lang = 0
    else:
        lang = lang - 1


def set_data():
    global vc, lang_data

    try:
        #SETTING HERE THE LANGUAGE DATA VARIABLE
        lang_data = languages[lang]
    except:
        cprint("Language is not set! Quitting...", "red")
        sys.exit()

    vc.lang_data = lang_data

    cprint("\nlanguage set to: " + lang_data['lang'] + "\n", "yellow")
    cprint(lang_data['instructions'], "green")


def listen(robot: cozmo.robot.Robot):

    cprint("wait...")

    if robot:
        checkBattery(robot)
        flash_backpack(robot, True)

    recognizer = sr.Recognizer()

    '''SETUP MIC'''
    with sr.Microphone() as source:

        recognizer.pause_threshold = 0.8
        recognizer.dynamic_energy_threshold = False #was True
        recognizer.adjust_for_ambient_noise(source)
        recognized = None

        prompt(2)

        '''LISTENING'''
        try:
            audio = recognizer.listen(source, timeout = 5)
        except sr.WaitTimeoutError:
            cprint("Timeout...", "red")
            if robot:
                flash_backpack(robot, False)
            prompt()
            return

        cprint("Done Listening: recognizing...","green")

        if robot:
            flash_backpack(robot, False)

        '''RECOGNIZING'''
        try:
            '''for testing purposes, we're just using the default API key
            to use another API key, change key=None to your API key'''
            recognized = recognizer.recognize_google(audio, key=None, language=lang_data['lang_ext']).lower() #GOOGLE
            #recognized = recognizer.recognize_wit(audio, key=WIT_AI_KEY_EN) #WIT
            #recognized = recognizer.recognize_sphinx(audio, language=lang_ext).lower() #SPINX
            print("You said: " + recognized)

            '''Check if one of the activation commands is in the recognized string'''
            found_command = set(commands_activate).intersection(recognized.split())
            if found_command:
                cprint("Action command recognized: " + str(found_command), "green")
                cmd_funcs, cmd_args = extract_commands_from_string(recognized) #check if a corresponding command exists
                executeCommands(robot, cmd_funcs, cmd_args)
            else:
                cprint("You did not say the magic words: " + commands_activate[0] + ", " + commands_activate[1], "red")
                if robot:
                    robot.play_anim("anim_pounce_reacttoobj_01_shorter").wait_for_completed()
            prompt()

        except sr.UnknownValueError or LookupError:
            cprint("Speech Recognition service could not understand audio", "red")
            prompt()
        except sr.RequestError as e:
            cprint("Could not request results from Speech Recognition service, check your web connection; {0}".format(e), "red")
            prompt()


def executeCommands(robot: cozmo.robot.Robot, cmd_funcs, cmd_args):
    if robot:
        vc.check_charger(robot,distance=70)
    for i in range(len(cmd_funcs)):
        if cmd_funcs[i] is not None:
            if robot:
                result_string = getattr(vc, cmd_funcs[i]['command'])(robot, cmd_args[i]) #HERE IS WHERE WE CALL THE ACTION, FINALLY!
                if result_string and log:
                    print(result_string)
            else: #DEBUG
                commands = lang_data['commands']
                index = cmd_funcs[i]['index']
                print(commands[index]['usage'])
        else:
            cprint(lang_data['error_one'], "red")
            printSupportedCommands()

    if len(cmd_funcs) == 0:
        cprint(lang_data['error_all'], "red")
        printSupportedCommands()
        if robot:
            robot.play_anim("anim_pounce_reacttoobj_01_shorter").wait_for_completed()

###### HELPER METHODS #######

def parse_arguments():
    global wait_for_shift, log
    if "--version" in sys.argv or "-V" in sys.argv:
        print(version)
        sys.exit()
    if "--no-wait" in sys.argv or "-W" in sys.argv:
        wait_for_shift = False
    if "--log" in sys.argv or "-L" in sys.argv:
        log = True

    if log:
        print ('Arguments list:', str(sys.argv[1:]))


def prompt(id = 1):
    if id == 1 and wait_for_shift:
        cprint(lang_data['text_wait'], "green", attrs=['bold'])
    elif id == 2:
        cprint(lang_data['text_say'], "magenta", attrs=['bold'], end="")
        cprint(" >>>", "green", attrs=['bold'])

def checkBattery(robot: cozmo.robot.Robot):

    if (robot.battery_voltage <= 3.5):
        color = "red"
    else:
        color = "yellow"
    cprint("BATTERY LEVEL(RED=LOW): %f" % robot.battery_voltage + "v", color)

def flash_backpack(robot: cozmo.robot.Robot, flag):
    robot.set_all_backpack_lights(cozmo.lights.green_light.flash() if flag else cozmo.lights.off_light)

def printSupportedCommands():
    commands = lang_data['commands']
    #for command in sorted(commands, key=lambda a :(a['words'])): #TO GET SORTED RESULTS!
    for command in commands:
        cprint("[ ", "cyan", end="")
        words = command['words']
        for i in range(0, len(words)):
            cprint(words[i], "cyan", end="")
            if i<len(words)-1:
                cprint(", ", end="")

        cprint(" ] : ", "cyan", end="")
        cprint(command['usage'])

def get_command(command_name): #iterates json and returns the command and its index
    commands = lang_data['commands']

    #splitted = func_name[len(prefix_str):-1] #get only the right part minus the last letter
    for i,command in enumerate(commands):
        #cycle through all the words in the commands list and look for one that is contained in the command as a substring!
        for word in command['words']:
            wordcut = word[0:-1] #getting the word minus the last letter for conjugations
            if wordcut in command_name.lower(): #checking if the word is contained in the command (driv in drive)
                func_name = commands[i]['action'] #getting the action that corresponds to the spoken command
                if log:
                    print("found the function: " + func_name + " matching the word: " + word)
                #return getattr(vc, func_name)
                return func_name, i
    return None, None

def extract_commands_from_string(in_string):
    '''Separate inString at each "and" or "then", loop through until we find commands, return tuples of cmd_func and cmd_args'''
    sentences = in_string.split(" " + lang_data['separator'] + " ")
    cmd_funcs = []
    cmd_args = []
    if log:
        print("splitted sentences: ", sentences)
    for sentence in sentences:
        words = sentence.split()
        for i in range(len(words)):
            cmd_func, cmd_index = get_command(words[i])
            if cmd_func:
                cmd_funcs.append({'index':cmd_index,'command':cmd_func})
                cmd_arg = words[i + 1:] #this one passes only the words after the command
                #cmd_arg = words[i:] #this one passes all words included the command
                cmd_args.append(cmd_arg)
                break
    if log:
        print("commands: ", cmd_funcs, "\narguments: ", cmd_args)
    return cmd_funcs, cmd_args # returns a touple of arrays of commands and arguments

###### ENTRY POINT ######
if __name__ == "__main__":
    main()
