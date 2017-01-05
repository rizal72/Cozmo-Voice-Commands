# Cozmo voice Commands (CvC) - Version 0.4.0

Issue multiple voice commands to [Cozmo](https://anki.com/en-us/cozmo), and watch him execute all of them sequentially: highly customizable, you can add new commands with ease. Recognizes *English, Italian and French*.

### Description
You can say *"Cozmo, DRIVE 20"*, or *"Please Cozmo, would you mind DRIVING backwards for 20 seconds?"*, **and Cozmo will execute the command in both cases**: the application will always dynamically match the recognized spoken words with the code methods and arguments, **it even parses verbs in their different conjugations**, and numbers as arguments of the action to perform.  
**NEW FEATURE: now you can issue MULTIPLE COMMANDS at once!**  
**i.e.** _"Hello Cozmo, my little friend, could you please drive forward for 3 seconds **THEN** rotate 90 degrees **THEN** dance **THEN** drive back to your charger?"_

**Tested on macOS, Windows and Linux!**  
**Still in Beta - Work in Progress!**

### Two steps installation
Assuming that you've already performed the [**Cozmo SDK Setup**](http://cozmosdk.anki.com/docs/), specific for your platform:  

1. **CvC** requires `portaudio`:

  * on **MacOS** (see [Homebrew](http://brew.sh/index_it.html) if you don't know what `brew` is):
  ```shell
  brew install portaudio
  ```
  * on **Linux**:
  ```shell
  sudo apt-get install flac portaudio19-dev python-all-dev python3-all-dev && sudo pip3 install PyAudio
  ```
  * on **Windows**:  
  you only need to [install git](https://git-scm.com/download/win) as it is not included by default.  

2. install `cvc` package:  
```shell
pip3 install git+https://github.com/rizal72/Cozmo-Voice-Commands
```
**note:** to update **CvC**, repeat step **2**.

### Usage
* run command `cvc` from the Terminal application
* choose speech recognition language (English, Italian and French are currently supported)
* issue commands by voice, not too far from your PC, taking care to include the word "**Cozmo**" before any command you'll say: *"Ok COZMO, my friend, would you enjoy ROTATING 90 degrees?"*  
**You can issue multiple commands at once:** use the word *"THEN"* (*"POI"* in Italian, *"ALORS"* in French), to separate them. Right now these commands will be executed in a sequence. I plan to make some of them to be executed in parallel in the near future.
A list of supported commands and arguments is provided at runtime

### Customization
You can add as many new commands as you like, commands are located in `cvc/voice_commands.py` file: just prefix their function names with the language they are spoken in, *i.e. "it_" for Italian, "en_" for english so, for instance, you'll create the method `en_smile()` and the voice command you'll have to say will be "smile" (or "smiling" or "smiled", and so on...)*.  
Some commands support arguments, for example: if you say *"Cozmo, drive backwards for 10 seconds"*, `backwards` and `10` will be passed to the method `en_drive()`, any other words will be ignored.

#### Note for Developers:
If you want to just run the App **without installing the package**, you need to execute `./run.py` from the root folder, after you have cloned/downloaded the [repository](https://github.com/rizal72/Cozmo-Voice-Commands) content.

### Todo next
* Allow more commands at once, to be executed in parallel, using the word *"and"*.   

**Please note:** Cozmo does not have built-in microphone, so you should talk with your computer ;)  
**Please pardon** my python scripting capabilities, it's not my *"native language"* ;)

**If you want the code, get it here:**
https://github.com/rizal72/Cozmo-Voice-Commands
