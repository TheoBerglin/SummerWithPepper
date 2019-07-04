import time
import sys
import argparse
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
    ip = args.ip
    port = args.port

    try:
        while True:
            hg = HumanGreeter(ip, port, "HumanGreeter")
            hg.run()
            mod_string = hg.get_module()
            hg.shutoff()
            print mod_string
            globals()[mod_string](ip, port, "test")
            time.sleep(10)
            # Run services here
    except KeyboardInterrupt:
        print "Interrupted by user, stopping HumanGreeter"
        sys.exit(0)
