# Pepper HumanGreeter #

The HumanGreeter search for humans and when detected ask what they might need help with. The HumanGreeter contains modules for each task. A how to document for Pepper and writing new modules for the structure is available in the misc folder. All modules can be launched using the tablet on Peppers stomach or by saying specific key phrases. These can be found in the dialog *Dialogs/HumanGreeting_enu.top*. Logic for each module is best understood by having a look at there respective dialog files.

## Available Modules ##
![Image of available modules](https://github.com/TheoBerglin/SummerWithPepper/blob/master/Misc/IMG_4686.jpg)

### Vasttrafik
Public transportation application. You can either plan a trip or see the next departures from close by stations. Planning a trip can be done using speech but also in text by saying "*text*" to Pepper. There is no implementation for fetching Peppers current location which means that the coordinates of Pepper is fixed to Lindholmspiren. This can be implemented so that the departures from close by station makes more sense at other locations.
### Weather
Fetches and displays the weather from any location on earth. No speech input apart from exiting module. Displays either hour for hourly or daily. 
### Survey
Simple survey application where you click either a green, yellow or red face depending on what you thought about the event. Say "*Result*" to be prompted to a result screen. You can go back to the survey from the result screen by saying "*Go back*". You can only end the survey from the result screen, this done by saying "*Thank you Pepper*", "*Thanks*" or "*Bye Pepper*".
### News
Pepper will randomly fetch a news story from a selected source and read the title and a summary. Both speech and buttons implemented
### Movie suggestions
Will give you a movie recommendation. Say for example "*no*" to get another movie. If you get movies which you think are to old, say "*new*" to get newer movies.

### Random fact
Pepper can tell you a random fact. Can be triggered both by speech or button click.

### Tell a joke
Pepper can tell you a Chuck Norris joke. Can be triggered both by speech or button click. Chuck Norris is changed to Zlatan, Zlatan is the best.



## Try the HumanGreeter ##
- Make sure Pepper is on
- Set him out of autonomous mode
- Make sure you're connected to the same WiFi
- Run program by writing "python main.py" in the terminal. Add the flag "w" if you want Pepper to walk around when searching for humans.
- Add a flag "--ip" followed by the IP of Pepper if it differs from the default one.
- Write "python main.py -h" for a help text of the program
- Quit the program with "Ctrl+c"

