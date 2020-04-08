# RhythmTrain

This is an game app to help you learn to sight read rhythms in western art music notation.
It will run on Android devices, and also on Linux desktop. Windows will likely work also though is untested.
It plays an mp3 of your choice and displays random bars of rhythms sync'd to the music.
Users can also chart out where the beats lay in the music if they so wish though it is time consuming to chart and not recommended.
You score points by tapping out the rhythms in time with the music, similar to games like Guitar hero.
But learning western art music notation as you go.

The app is written using Python3 with the Kivy library, which provides a cross-platform (Android, iOS, Linux and more) graphics and touch API.

Please follow installation and song setup steps carefully as all stages are necessary for a smooth experience

# INSTALLATION LINUX:

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
Your own music may then be added to the music folder for detection. For further instructions on this process please see the Song Setup section below. 

# INSTALLATION FOR ANDROID

I have provided an APK in the release for those who would like to install on Android. You can download the APK directly to your phone 
and install, or alternatively download on desktop and use your chosen file manager to install the APK. Once the APK is install YOU MUST 
copy all of the contents from the music folder in this repository to your Android music folder, leaving the file structure intact as 
demonstrated below:

```
Phone
|
----->Music
|     | Can't Go 145BPM.mp3
|     | I Did It Wrong 145BPM.mp3
|     | etc......
|     --------> SidecarFiles
|     |        |
|     |        | Can't Go 145BPM.mp3.beats
```



Or alternatively, for those who would like to compile their own APK, I have included a buildozer spec file and instructions on how to 
use this can be seen here: https://kivy.org/doc/stable/guide/packaging-android.html

For compiling your own APK you will also need to install pyjnius: https://pyjnius.readthedocs.io/en/stable/

The kivy launcher may also be used to run on android though is untested, first install the "Kivy Laucnher" from your "app store" or 
direct from it's package for your phone type.
e.g. for Android, via Google's Play Store:  https://play.google.com/store/apps/details?id=org.kivy.pygame&hl=en_US
The Kivy launcher allows you to load different Kivy-based apps as data files rather than having to install them individually.
(When this app is more stable we may package it as a standalone Android and other platform app to run without the Laucher.)

# Song Setup

Once installation is complete you can begin adding your own songs to the game. Firstly all songs you want to add must be in the root of 
the music folder for the game to detect them. Secondly, a pairing beat file must be created with the same name as the mp3 you want it to 
pair to and added into the SidecarFiles folder in the music folder on your device. Some examples of these can be seen with the music provided. The structure of these files can be seen below:

```
120          <--- BPM
320          <--- Song length in seconds
0.02         <--- Song start offset in seconds incase the sound for the song doesn't start right at the beginning of the audio file
0.13         |
0.21         | For those who want to chart their own beats to a song, you are able to put where you want the notes to be placed
0.33         | in seconds and the game will do the rest. This however is not required for the main mode in the game (practising random)
0.45         | and so can be ignored. For an example of a file that has this, see Keep 'em Dry.mp3.beats
```

Naming conventions for pairing song files is as follows:

```
{exact name of song}.{file extension}.beats
```

For those who would like to add random rhythms to the rotation you are able to do so by modifying RandomBeats.txt. There are currently 
some limitations to the system. The system currently only supports up to 16th notes however the underlying code to support them is done, 
just assets are needed so if you would like to make some contributions to the project please feel free. Be very careful with formatting as incorrect formatting may cause the app to crash. An example of some bars you might add to the file can be seen below:

```
4 4 4 4       <----- A bar consisting of 4 quarter notes
2 2           <----- A bar consisting of 2 half notes
4r 4t 4 4     <----- A bar consisting of a quarter note rest, a quarter note triplet and 2 quarter notes
8 8 4 4 4     <----- A bar consisting of 2 eigth notes and 3 quarter notes
```

# Next Steps
```
Proper bars across the tops of notes to join appropriate groups together
A more diverse range of notes (base code complete)
Support for non 4/4 time signatures (base code complete)
Potentially automate BPM detection using tools like aubio
Detect length of a song automatically
```

CREATIVE COMMONS SONG USE REFERENCES
```
Elephants' Ride - Royalty-Free Music by https://audiohub.com
License: CC BY (https://creativecommons.org/licenses/by/4.0/)
Keep 'em dry - Royalty-Free Music by https://audiohub.com
License: CC BY (https://creativecommons.org/licenses/by/4.0/)
I Did It Wrong - Royalty-Free Music by https://audiohub.com
License: CC BY (https://creativecommons.org/licenses/by/4.0/)
Oppression For Your Dignity - Royalty-Free Music by https://audiohub.com
License: CC BY (https://creativecommons.org/licenses/by/4.0/)
Can't Go - Royalty-Free Music by https://audiohub.com
License: CC BY (https://creativecommons.org/licenses/by/4.0/)
Careless (2015) - Royalty-Free Music by https://audiohub.com
License: CC BY (https://creativecommons.org/licenses/by/4.0/)
Uncle Alp´s Song - Royalty-Free Music by https://audiohub.com
License: CC BY (https://creativecommons.org/licenses/by/4.0/)
```


