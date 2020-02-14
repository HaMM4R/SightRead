# SightRead

This is an game app to help you learn to signt read rhythms in western art music notation.
It will phone on mobile devices including Android and iOS, and also on Linux desktop.
It plays an mp3 of your choice and displays bars of rhythms sync'd to the music.
You score points by tapping out the rhythms in time with the music, similar to games like Guitar hero.
But learning western art music notation as you go.

The app is written using Python3 with the Kivy library, which provides a cross-platform (Android, iOS, Linux and more) graphics and touch API.

INSTALLATION:

First install Kivy: (from https://kivy.org/doc/stable/installation/installation-linux.html)

```
$ python3 -m pip install --upgrade --user pip setuptools virtualenv
$ python3 -m virtualenv ~/kivy_venv
$ source ~/kivy_venv/bin/activate
$ python3 -m pip install kivy
$ python3 -m pip install kivy_examples
$ python3 -m pip install ffpyplayer
```

Then to run on Ubuntu, clone and do
```
$ python3 main.py
```

To run on Android etc, first install the "Kivy Laucnher" from your "app store" or direct from it's package for your phone type.

e.g. for Android, via Google's Play Store:  https://play.google.com/store/apps/details?id=org.kivy.pygame&hl=en_US

The Kivy launcher allows you to load different Kivy-based apps as data files rather than having to install them individually.

(When this app is more stable we may package it as a standalone Android and other platform app to run without the Laucher.)
