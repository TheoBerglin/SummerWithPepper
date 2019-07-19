import time
import sys
import argparse
import qi
from Modules.humangreeter_module import HumanGreeter
from Modules.vasttrafik_module import VasttrafikModule
from Modules.weather_module import WeatherModule
from Modules.survey_module import SurveyModule
from Modules.news_module import NewsModule
from Modules.imdb_module import IMDBModule
IP = "192.168.1.102"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default=IP,
                        help="Robot IP address. On robot or Local Naoqi: use '192.168.1.102'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    name = "HumanGreeter"

    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application([name, "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) + ".\n"
                "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    # Create human greeter
    human_greeter = HumanGreeter(app, name)

    # Create dict for storing modules
    modules = dict()

    # Loop until user interrupts
    try:
        while True:
            human_greeter.run()
            mod_string = human_greeter.get_module()

            # If module hasn't been used before
            if mod_string not in modules:
                print "Adding " + mod_string + " to dict"
                mod = globals()[mod_string](app, "test", args.ip)
                modules[mod_string] = mod
            else:
                print "Module exists in dict"
                mod = modules[mod_string]
            mod.run()
            time.sleep(1)
    except KeyboardInterrupt:
        print "Interrupted by user, stopping HumanGreeter"
        # Shut down modules
        for module in modules.itervalues():
            module.shutoff()
        human_greeter.shutoff()
        human_greeter.go_to_sleep()
        sys.exit(0)
