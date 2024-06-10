# xPaste

<img src="https://github.com/diegojgb/xPaste/blob/main/screenshot.png" width="828" height="597">

## What is it?

xPaste is a simple application that allows you to bypass paste-blocking websites and applications by simulating keystrokes and typing the text from your clipboard.

It is written in Python, using the Tkinter standard library for the GUI, and the [keyboard](https://github.com/boppreh/keyboard "https://github.com/boppreh/keyboard") module for the typing.

## Installation

- You can download the latest release from [here](https://github.com/diegojgb/xPaste/releases/latest "https://github.com/diegojgb/xPaste/releases/latest")
- It is a standalone executable, just one file, that's it. It stores its settings in a 'config.ini' file within the same directory.

## Usage
1. &nbsp;Open xPaste and make sure it's turned on.  
2. &nbsp;Copy the text you want to paste.  
3. &nbsp;Press CTRL+V (or your customized hotkey).  
4. &nbsp;The text will be typed, with simulated keystrokes.  

It comes with a few settings you can play around with, nothing special.

## Build from source

If you want to build the application from the source code by yourself, just clone/download the repository, and build it with pyinstaller, using the xpaste.spec I included.

1\. &nbsp;Install pyinstaller if you don't have it

```
pip install pyinstaller
```

2\. &nbsp;Run xpaste.spec with pyinstaller
```
pyinstaller xpaste.spec
```
