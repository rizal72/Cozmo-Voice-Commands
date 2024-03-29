# Cozmo voice Commands (CvC)

Issue multiple voice commands to [Cozmo](https://anki.com/en-us/cozmo), and watch him execute all of them sequentially: highly customizable, you can add new commands with ease. Recognizes *English, Italian, French, German, Dutch* but it's very easy to add new languages!

# **IMPORTANT!**  
Unfortunately Cozmo and Cozmo SDK are no longer supported or updated by their developers so, as time goes by, they will be no longer compatible with newer Python versions and libraries.  
**Cozmo SDK works well with Python 3.6**, so what I sugget is to create a Python **virtual environment** with that specific version, then let this app run inside it.   

I suggest to use [Miniconda](https://docs.conda.io/en/latest/miniconda.html), because it's easy to specify a custom Python version on the fly.   
First create the virtual environment and name it as you like (here I use cvc for simplicity):  
`conda create -n cvc python=3.6`  
then activate it:  
`conda activate cvc`  
and then you can install CvC package as described below:  
`pip install --upgrade git+https://github.com/rizal72/Cozmo-Voice-Commands` 
then run it, typing:  
`cvc`

*note: remeber that you will still need `portaudio` to be installed on your system as described in the installation section below.
#

### Description
You can say _"Cozmo, **forward** 20 THEN **right** 90"_, or _"Hello Cozmo, my little friend, could you please drive forward for 3 seconds **THEN** rotate left 90 degrees **THEN** dance **THEN** drive back to your charger?"_, **and Cozmo will execute the commands in both cases**: the application will always dynamically match the recognized spoken words with the code methods and arguments, **it even parses verbs in their different conjugations**, and numbers as arguments of the action to perform.  

**Tested on macOS, Windows and Linux**

### Two steps installation
Assuming that you've already performed the [**Cozmo SDK Setup**](http://cozmosdk.anki.com/docs/), specific for your platform:  

1. **CvC** requires `portaudio`:

  * on **MacOS** (see [Homebrew](http://brew.sh/index_it.html) if you don't know what `brew` is):  
`brew install portaudio`

  * on **Linux**:  
`sudo apt-get install flac portaudio19-dev python-all-dev python3-all-dev && pip3 install --user PyAudio`

  * on **Windows**:  
you only need to [install git](https://git-scm.com/download/win) as it is not included by default.  

2. install `cvc` package:  
`pip install --upgrade git+https://github.com/rizal72/Cozmo-Voice-Commands`  
  * If you are having permission issues (happens mainly on Linux) try:  
  `pip install --upgrade --user git+https://github.com/rizal72/Cozmo-Voice-Commands`

**note:** to update **CvC**, repeat step **2**.

### Usage
* run command `cvc` from the Terminal application.
  * Optional arguments:  
`--version[-V]`: print version and exit  
`--no-wait[-N]`: enable deprecated continuous listening mode  
`--log[-L]`: enable verbose logging  
* choose speech recognition language and press enter.
* press **SHIFT** when you are ready, then issue your commands by voice (you have 5 seconds to start talking before it Timeouts), not too far from your PC, taking care to include the words "**Cozmo**" or "**Robot**" before any command you'll say: _"Ok COZMO, my friend, would you enjoy DANCING?"_  
**You can issue multiple commands at once:** use the word *"THEN"* (_"POI"_ in Italian, _"ALORS"_ in French, _"DAARNA"_ in Dutch, and so on...), to separate them. Right now these commands will be executed in a sequence. I plan to make some of them to be executed in parallel in the near future.
* **A list of supported commands and arguments is provided at runtime.**

### Customization
From version 0.6 you can now add new languages and commands with ease: inside `cvc/languages` folder you'll find one .json file for each language (i.e. `en.json`). To add a new command just duplicate one of the existing commands inside the .json, changing its parameters with the desired ones (_be careful to keep the same structure_):  

* **DO NOT FORGET** to change the id number, that decides language order (it's the first parameter).
* `'action'` is the name of the method/function you are going to create in `voice_commands.py`
* `'words'` are the recognized words  
* `'usage'` is a description/usage of your command  

then open `voice_commands.py` and create the new method/function for your command, just copying an existing one, taking care to use the same name you set in the `'action'` parameter, inside the .json.  
**You can even add new words to existing commands**, only be careful to not use the same words in different commands.  
To add a new language, duplicate one of the included .json language files, using the same naming, and **translate its contents**.
Your new language will be automatically loaded on startup, and a new language menu item automatically generated ;)

#### Note for Developers:
If you want to just run the App **without installing the package**, you need to execute `./cvc.py` from the root folder, after you have cloned/downloaded the [repository](https://github.com/rizal72/Cozmo-Voice-Commands) content.

### Todo next
* Allow more commands at once, to be executed in parallel, using the word _"and"_.   

**Please note:** Cozmo does not have built-in microphone, so you should talk with your computer ;)  

**If you want the code, get it here:**
https://github.com/rizal72/Cozmo-Voice-Commands
