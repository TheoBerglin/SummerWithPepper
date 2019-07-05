import time
import sys
import argparse
import qi
from Modules.humangreeter_service import HumanGreeter
from Modules.vasttrafik_service import VasttrafikService

IP = "192.168.1.102"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default=IP,
                        help="Robot IP address. On robot or Local Naoqi: use '192.168.1.101'.")
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

    human_greeter = HumanGreeter(app, name)
    modules = dict()
    try:
        while True:
            human_greeter.run()
            mod_string = human_greeter.get_module()
            if mod_string not in modules:
                print "Adding " + mod_string + " to dict"
                mod = globals()[mod_string](app, "test", args.ip)
                modules[mod_string] = mod
            else:
                print "Module exists in dict"
                mod = modules[mod_string]
            mod.run()
            time.sleep(10)
            # Run services here
    except KeyboardInterrupt:
        print "Interrupted by user, stopping HumanGreeter"
        for module in modules.itervalues():
            module.shutoff()
        human_greeter.shutoff()

        sys.exit(0)
