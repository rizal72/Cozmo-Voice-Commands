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
    from pynput.keyboard import Key, Listener
    import speech_recognition as sr
except ImportError:
    sys.exit('some packages are required, install them doing: `pip3 install --user termcolor SpeechRecognition PyAudio Pyinput` to run this script.\nIf you are on linux do: `sudo apt-get install flac portaudio19-dev python-all-dev python3-all-dev && sudo pip3 install pyinput pyaudio`')

from . import voice_commands

###### VARS ######
title = "Cozmo-Voice-Commands (CvC) - Version 0.5.0"
author =" - Riccardo Sallusti (http://riccardosallusti.it)"
log = False
lang = "en"
commands_activate = ["cosmo", "cosimo", "cosma", "cosima", "kosmos", "cosmos", "cosmic", "osmo", "kosovo", "peau", "kosmo", "kozmo", "gizmo"]
recognizer = sr.Recognizer()
vc = None
text_start_en = "\nPRESS <SHIFT> WHEN YOU ARE READY TO SPEAK..."
text_start_it = "\nPREMI <SHIFT> QUANDO SEI PRONTO A PARLARE..."
text_start_fr = "\nAPPUYEZ SUR <SHIFT> LORSQUE VOUS ÊTES PRÊT À PARLER..."
en_seq_action_separator = " then "# don't foget spaces!
it_seq_action_separator = " poi " # don't foget spaces!
fr_seq_action_separator = " alors " # don't foget spaces!

##### MAIN ######
def main():
    clearScreen = os.system("clear")
    cprint(title, "green", attrs=['bold'], end='')
    cprint(author, "cyan")
    cozmo.robot.Robot.drive_off_charger_on_connect = False
    try:
        cozmo.run_program(run)
        #cozmo.run_program(run, use_viewer=True, force_viewer_on_top=True)
    except SystemExit as e:
        print('exception = "%s"' % e)
        #ONLY FOR TESTING PURPOSES
        cprint('\nGoing on without Cozmo: for testing purposes only!', 'yellow')
        run(None)

##### APP ######
def run(robot: cozmo.robot.Robot):
    '''The run method runs once the Cozmo SDK is connected.'''
    global vc

    vc = voice_commands.VoiceCommands(robot)

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
        set_language()
        printSupportedCommands()
        prompt(1)

        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

    except KeyboardInterrupt:
        print("")
        cprint("Exit requested by user", "yellow")

def set_language():
    global lang, lang_sphinx

    cprint('\nCHOOSE YOUR LANGUAGE (hit "enter" for default [English]):', 'green')
    print('1: English')
    print('2: Italian')
    print('3: French')

    newLang = 0
    while not newLang:
        try:
            newLang = int(input('>>> ').strip())
            if newLang not in range(1, 4):
                raise ValueError
        except ValueError:
            if not newLang:
                break
            else:
                newLang = 0
                cprint("That's not an option!", "red")

    if newLang == 1 or not newLang:
        lang = "en"
        lang_sphinx = "en-US"
        cprint("You can issue voice commands to Cozmo.\nYou can give multiple commands separating them with the word 'THEN'.\nAvailable Commands are:", "green")
    elif newLang == 2:
        lang = "it"
        lang_sphinx = "it-IT"
        cprint("Puoi impartire comandi vocali a Cozmo.\nPuoi dare comandi in sequenza separandoli con la parola 'POI'.\nI comandi disponibiloi sono:", "green")
    elif newLang == 3:
        lang = "fr"
        lang_sphinx = "fr-FR"
        cprint("Donnez une commande vocale à Cozmo.\nVous pouvez en donner plusieurs en les séparant par le mot 'ALORS'.\nI Les commandes disponibles sont:", "green")

    cprint("\nlanguage set to: " + lang + "\n", "yellow")

def listen(robot: cozmo.robot.Robot):

    if robot:
        checkBattery(robot)
        flash_backpack(robot, True)

    '''SETUP MIC'''
    with sr.Microphone(chunk_size=512) as source:

        prompt(2)

        recognizer.pause_threshold = 0.8
        recognizer.dynamic_energy_threshold = True
        recognized = None

        '''STARTS LISTENING'''
        try:
            audio = recognizer.listen(source, timeout = 5)

            '''for testing purposes, we're just using the default API key
            to use another API key, change key=None to your API key'''
            recognized = recognizer.recognize_google(audio, key=None, language=lang_sphinx).lower() #GOOGLE
            #recognized = recognizer.recognize_wit(audio, key=WIT_AI_KEY_EN) #WIT
            #recognized = recognizer.recognize_sphinx(audio, language=lang_sphinx).lower() #SPINX
            print("You said: " + recognized)

            '''Check if one of the activation commands is in the recognized string'''
            if set(commands_activate).intersection(recognized.split()):
                cprint("Action command recognized", "green")
                cmd_funcs, cmd_args = extract_commands_from_string(recognized) #check if a corresponding command exists
                executeComands(robot, cmd_funcs, cmd_args)
            else:
                cprint("You did not say the magic word " + commands_activate[0], "red")
                if robot:
                    robot.play_anim("anim_pounce_reacttoobj_01_shorter").wait_for_completed()
            prompt()

        except sr.UnknownValueError:
            cprint("Speech Recognition service could not understand audio", "red")
            prompt()
        except sr.RequestError as e:
            cprint("Could not request results from Speech Recognition service, check your web connection; {0}".format(e), "red")
            prompt()
        except sr.WaitTimeoutError:
            cprint("Timeout...", "red")
            prompt()

def executeComands(robot: cozmo.robot.Robot, cmd_funcs, cmd_args):
    if robot:
        vc.check_charger(robot,distance=70)
    for i in range(len(cmd_funcs)):
        if cmd_funcs[i] is not None:
            result_string = cmd_funcs[i](robot, cmd_args[i]) #remember: cmd_func contains vc as well thanks to 'getattr', like vc.en_dance()
            if result_string:
                print(result_string)
        else:
            if lang=="en":
                cprint("Sorry I didn't understand all of your commands, available commands are:", "red")
            elif lang == "it":
                cprint("Mi spiace non ho capito tutti i comandi, i comandi disponibili sono:", "red")
            elif lang == "fr":
                cprint("Je suis désolé, je n'ai pas compris toutes les commandes, les commandes disponibles sont:", "red")
            printSupportedCommands()

    if len(cmd_funcs) == 0:
        if lang=="en":
            cprint("Sorry I didn't understand any of your commands, available commands are:", "red")
        elif lang == "it":
            cprint("Mi spiace non ho capito nessuno dei comandi, i comandi disponibili sono:", "red")
        elif lang == "fr":
            cprint("Je suis désolé, je n'ai compris aucune de vos commandes, les commandes disponibles sont:", "red")
        printSupportedCommands()
        if robot:
            robot.play_anim("anim_pounce_reacttoobj_01_shorter").wait_for_completed()

###### HELPER METHODS #######

def prompt(id = 1):
    if id == 1:
        cprint(eval("text_start_"+lang), "green", attrs=['bold'])
    elif id == 2:
        cprint("\nSay your commands (Tiemout: 5 seconds - ctrl+c to exit)", "magenta", attrs=['bold'], end="")
        cprint(" >>>", "green", attrs=['bold'])

def checkBattery(robot: cozmo.robot.Robot):

    if (robot.battery_voltage <= 3.5):
        color = "red"
    else:
        color = "yellow"
    cprint("BATTERY LEVEL(RED=LOW): %f" % robot.battery_voltage + "v", color)

def flash_backpack(robot: cozmo.robot.Robot, flag):
    robot.set_all_backpack_lights(cozmo.lights.green_light.flash() if flag else cozmo.lights.off_light)

def get_supported_commands():
    '''Construct a list of all methods in this class that start with 'lang' variabler content - these are commands we accept'''
    prefix_str = lang + "_"
    supported_commands = []
    for func_name in dir(vc):
        if func_name.startswith(prefix_str):
            supported_commands.append({"name": func_name[len(prefix_str):], "usage": getattr(vc, func_name)()})
    return supported_commands

def printSupportedCommands():
    commands = get_supported_commands()
    for command in commands:
        cprint(command['name'], "cyan", end="")
        print(": " + command['usage'])

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

###### ENTRY POINT ######
if __name__ == "__main__":
    main()
