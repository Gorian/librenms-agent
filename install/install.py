#!/usr/bin/env python
################################################################################
# Layne "Gorian" Breitkreutz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# standards: https://www.python.org/dev/peps/pep-0008/
################################################################################

################################################################################
# IMPORTS
################################################################################
import sys
import os
import datetime
import argparse
import socket
import yaml
from logging.handlers import RotatingFileHandler

################################################################################
# DEFINE GLOBAL CONSTANTS
################################################################################
SCRIPT = {}
SCRIPT["name"] = "Test Script"
SCRIPT["version"] = "0.0.1"
SCRIPT["execution"] = os.path.basename(__file__)
HOSTNAME = socket.gethostname()
HOST_FQDN = socket.getfqdn()
TODAY = datetime.date.today()
HOME_DIRECTORY = os.path.expanduser('~')
COLUMNS = os.getenv("COLUMNS",80)
FORMAT_WIDTH = 30


################################################################################
# DEFINE CLASSES
################################################################################
class Person(object):
    def __init__(self, name='', food=''):
        self.name = name
        self.food = food

    def test(self):
        print("user's name is \"{0}\" and their favorite food is \"{1}\"")\
            .format(self.name, self.food)



################################################################################
# DEFINE FUNCTIONS
################################################################################


def main():
    """program entry point

    Args:
        Accepts all program arguments

    Returns:
        Program exit code as an integer
    """

    ############################################################################
    # PARSE PROGRAM ARGUMENTS
    ############################################################################
    parser = argparse.ArgumentParser(prog=sys.argv[0],
        description="LibreNMS client install script", add_help=False)
    arggroup_options = parser.add_argument_group("options")

    arggroup_options.add_argument("--name",
        help="user name", type=str, required=False)

    arggroup_options.add_argument("-d", "--debug",
        help="enables debug messages. Sets logging level to DEBUG.",
        action="store_true", dest="debug",
        required=False)

    arggroup_options.add_argument("-v", "--version", action="version",
        version="{0} {1}".format(SCRIPT["name"], SCRIPT["version"]))

    arggroup_options.add_argument("-h", "--help", action="help",
        help="show this help message and exit")

    # we handle no arguments
    # (always at least 1. sys.argv[0] is the program name)
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    # parse the arguments and assign them to "args"
    args = parser.parse_args()

    data=yaml.load("""
    !!python/object:__main__.Person
    Gorian:
        name: Gorian
        food: pasta
    Murrant:
        name: Murrant
        food: pizza
    """)

    #user = getattr(Persons, args.name)
    user = Person(**getattr(data, args.name))
    user.test()


    if args.debug:
        print("\nDEBUG INFO")
        print('-' * int(COLUMNS))
        print("Globals:")
        for key, value in globals().items():
            print("\t{0} {1}".format(str(key).ljust(FORMAT_WIDTH),
                str(value).ljust(FORMAT_WIDTH)))
        print("\nArguments:")
        for arg in vars(args):
            print("\t{0} {1}".format(str("args." + str(arg))\
                .ljust(FORMAT_WIDTH),
                str(getattr(args, arg)).ljust(FORMAT_WIDTH)))
        print("\nVariables:")
        for key,value in locals().items():
            if key not in ["var_dict", "key", "value", "parser", "args", "arg"]:

                print("\t{0} {1}".format(str(key).ljust(FORMAT_WIDTH),
                    str(value).ljust(FORMAT_WIDTH)))

# we call main()
if __name__ == "__main__":
    main()
