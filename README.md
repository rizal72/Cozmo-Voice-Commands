#Cozmo voice Commands (CvC) Version 0.2.1

Issue complex voice commands to Cozmo, and watch him execute them: highly customizable, you can add new commands with ease.
Recognizes *English* and *Italian*.

##Description
You can say *"Cozmo, DRIVE 20"*, or *"Please Cozmo, would you mind DRIVING for 20 seconds"*, **and Cozmo will execute the command in both cases**: the application will always dynamically match the recognized spoken words with the code methods and arguments, **it even parses verbs in their different conjugations**, and numbers inside long sentences ;)

**Tested on macOS an Linux!
Still in Beta - Work in Progress!**

##Installation
1. on **MacOS** install **portaudio**:  
`brew install portaudio` (see [Homebrew](http://brew.sh/index_it.html) if you don't know what `brew` is)  
on **Linux** from Terminal, do:  
`sudo apt-get install flac portaudio19-dev python-all-dev python3-all-dev && sudo pip3 install PyAudio`
2. install `cvc` package:  
`pip install git+https://github.com/rizal72/Cozmo-Voice-Commands`

##Note for Developers:
If you want to just run the App **without installing the package**, you need to execute `./run.py` from the root folder,  
after you have cloned/downloaded the [repository](https://github.com/rizal72/Cozmo-Voice-Commands) content.

##Usage
* run command `cvc` from the Terminal application
* choose speech recognition language (English and Italian are currently supported)
* issue commands by voice, starting with the activation word "**Cozmo**", then the command that may contain arguments if needed: a list of supported commands and arguments is provided at runtime

##Customization
You can add as many new commands as you like, commands are located in `cvc/voice_commands.py` file: just prefix their function names with the language they are spoken in, *i.e. "it_" for Italian, "en_" for english so, for instance, you'll create the method "en_smile()" and the voice command you'll have to say will be "smile" (or "smiling" or "smiled"... magic...)*.  
Some commands support one argument, for example: if you say *"drive for 10 seconds"*, 10 will be passed to the method *"en_drive"*, any other words will be ignored.

##Todo next
* Allow more commands in one sentence, to perform at the same time (async) using the word *"and"*, or make them sequential using the word *"then"* in between.   

**Please note:** Cozmo does not have built-in microphone, so you should talk with your computer ;)  
**Please pardon** my python scripting capabilities, it's not my *"native language"* ;)
