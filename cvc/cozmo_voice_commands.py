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
import cozmo
try:
    from termcolor import colored, cprint
    import speech_recognition as sr
except ImportError:
    sys.exit('some packages are required, install them doing: `pip3 install --user termcolor SpeechRecognition PyAudio` to run this script.\nIf you are on linux do: `sudo apt-get install flac portaudio19-dev python-all-dev python3-all-dev && sudo pip3 install pyaudio`')
import cvc.voice_commands as voice_commands

###### VARS ######
log = False
lang = "en"
commands_activate = ["cosmo", "cosimo", "kosmos", "osmo"]
recognizer = sr.Recognizer()
vc = None
en_seq_action_separator = " then "# don't foget spaces!
it_seq_action_separator = " poi " # don't foget spaces!

##### MAIN ######
def main():
    clearScreen = os.system("clear")
    try:
        cozmo.run_program(run)
        #cozmo.run_program(run, use_viewer=True, force_viewer_on_top=True)
    except SystemExit as e:
        print('exception = "%s"' % e)
        #ONLY FOR TESTING PURPOSES
        cprint('\nGoing on without Cozmo. Fer testing purposes only!', 'yellow')
        run(None)

##### APP ######
def run(robot: cozmo.robot.Robot):
    '''The run method runs once the Cozmo SDK is connected.'''
    global vc

    vc = voice_commands.VoiceCommands(robot)
    if robot:
        robot.play_anim("anim_cozmosays_getout_short_01")

    try:
        set_language()

        if lang=="en":
            cprint("You issue voice commands to Cozmo.\nYou can give multiple commands separating them with the word 'THEN'.\nAvailable Commands are:", "green")
        else:
            cprint("Puoi impartire comandi vocali a Cozmo.\nPuoi dare comandi in sequenza separandoli con la parola 'POI'.\nI comandi disponibiloi sono:", "green")
        print(*get_supported_commands(), sep="\n")

        with sr.Microphone(chunk_size=512) as source:
            while 1:
                if robot:
                    checkBattery(robot)
                    flash_backpack(robot, True)
                    '''try:
                        robot.play_anim("anim_meetcozmo_getin").wait_for_completed()
                    except:
                        pass'''
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
    supported_commands = []
    for func_name in dir(vc):
        if func_name.startswith(prefix_str):
            #supported_commands.append(func_name[len(prefix_str):])
            supported_commands.append(func_name[len(prefix_str):] + ": " + getattr(vc, func_name)())
    return supported_commands

def get_command(command_name):
    '''Find a matching function inside 'VoiceCommands' class and return it. return None if there's no match'''
    prefix_str = lang + "_"
    for func_name in dir(vc):
        '''cycle through all the methods in vc and look for one that is contained in the command as a substring!
        this allows us to use similar words like drive o driving to be executed as well!'''
        if func_name.startswith(prefix_str):
            splitted = func_name[len(prefix_str):-1] #get only the right part minus the last letter
            if splitted in command_name.lower(): #here the magic happens
                return getattr(vc, func_name)
    return None

def extract_command_from_string(in_string):
    '''Separate inString at each space, loop through until we find a command, return tuple of cmd_func and cmd_args'''
    split_string = in_string.split()
    for i in range(len(split_string)):
        cmd_func = get_command(split_string[i])
        if cmd_func:
            cmd_args = split_string[i + 1:]
            return cmd_func, cmd_args
    # No valid command found
    return None, None

def extract_commands_from_string(in_string):
    '''Separate inString at each "and" or "then", loop through until we find commands, return tuples of cmd_func and cmd_args'''
    sentences = in_string.split(eval(lang + "_seq_action_separator"))
    cmd_funcs = []
    cmd_args = []
    if log:
        print("splitted sentences: ", sentences)
    for sentence in sentences:
        words = sentence.split()
        for i in range(len(words)):
            cmd_func = get_command(words[i])
            if cmd_func:
                cmd_funcs.append(cmd_func)
                cmd_arg = words[i + 1:]
                cmd_args.append(cmd_arg)
    if log:
        print("commands: ", cmd_funcs, "arguments: ", cmd_args)
    return cmd_funcs, cmd_args # returns a touple of arrays of commands and arguments

def flash_backpack(robot, flag):
    robot.set_all_backpack_lights(cozmo.lights.green_light.flash() if flag else cozmo.lights.off_light)

def hear(source, robot):
    '''Speech recognition using Google Speech Recognition
    for testing purposes, we're just using the default API key'''
    audio = recognizer.listen(source)
    recognized = None
    try:
        #to your API key, change key="YOUR_KEY":
        recognized = recognizer.recognize_google(audio, key=None, language=lang).lower()
        #recognized = recognizer.recognize_wit(audio, key=WIT_AI_KEY_EN)
        print("You said: " + recognized)
        '''very nice: check if one of the activation commands is in the recognized string'''
        if set(commands_activate).intersection(recognized.split()):
            cprint("Action command recognized", "green")
            cmd_funcs, cmd_args = extract_commands_from_string(recognized) #check if a corresponding command exists
            executeComands(robot, cmd_funcs, cmd_args)

        else:
            cprint("You did not say the magic word " + commands_activate[0], "red")
            if robot:
                robot.play_anim("anim_pounce_reacttoobj_01_shorter").wait_for_completed()

    except sr.UnknownValueError:
        cprint("Speech Recognition service could not understand audio", "red")
    except sr.RequestError as e:
        cprint("Could not request results from Speech Recognition service, check your web connection; {0}".format(e), "red")

def executeComands(robot, cmd_funcs, cmd_args):

    for i in range(len(cmd_funcs)):
        if cmd_funcs[i] is not None:
            result_string = cmd_funcs[i](robot, cmd_args[i]) #remember: cmd_func contains vc as well thanks to 'getattr', like vc.en_dance()
            if result_string:
                print(result_string)
        else:
            if lang=="en":
                cprint("Sorry I didn't understand all of your commands, available commands are:", "red")
            else:
                cprint("Mi spiace non ho capito tutti i comandi, i comandi disponibili sono:", "red")
            print(*get_supported_commands(), sep="\n")

    if len(cmd_funcs) == 0:
        if lang=="en":
            cprint("Sorry I didn't understand any of your commands, available commands are:", "red")
        else:
            cprint("Mi spiace non ho capito nessuno dei comandi, i comandi disponibili sono:", "red")
        print(*get_supported_commands(), sep="\n")
        if robot:
            robot.play_anim("anim_pounce_reacttoobj_01_shorter").wait_for_completed()

###### ENTRY POINT ######
if __name__ == "__main__":
    main()
