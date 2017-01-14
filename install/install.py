#!/usr/bin/env python
################################################################################
# LibreNMS Client Install Script
# Layne "Gorian" Breitkreutz
# Sets up the client for monitoring with LibreNMS
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
import urllib
from logging.handlers import RotatingFileHandler

################################################################################
# DEFINE GLOBAL CONSTANTS
################################################################################
SCRIPT = {}
SCRIPT["name"] = "LibreNMS Client Install Script"
SCRIPT["version"] = "0.0.1"
SCRIPT["execution"] = os.path.basename(__file__)
HOSTNAME = socket.gethostname()
HOST_FQDN = socket.getfqdn()
TODAY = datetime.date.today()
HOME_DIRECTORY = os.path.expanduser('~')
COLUMNS = os.getenv("COLUMNS",80)
FORMAT_WIDTH = 30

DEFAULTS = {}
DEFAULTS["snmpd_extend"] = "/etc/snmp/extends.d"
DEFAULTS["agent_dir"] = "/usr/lib/check_mk/local"
DEFAULTS["github_url"] = "https://raw.githubusercontent.com/Gorian/librenms-agent/client-install/install/"
DEFAULTS["os_yaml"] = "os.yaml"

################################################################################
# DEFINE CLASSES
################################################################################

class OperatingSystem(object):

    def __init__(self, name, package_manager,
        description="an operating system", snmpd_pkgs="", xinetd_pkgs=""):
        self.name = name
        self.description = description
        self.package_manager = package_manager
        self.snmpd_pkgs = snmpd_pkgs

    def test(self):
        print("My OS is \"{0}\", and my package manager is \"{1}\"")\
            .format(self.name,self.package_manager)
        print("My snmpd package is \"{0}\"").format(self.snmpd_pkgs)
        print("\"{0}\" is \"{1}\"").format(self.name,self.description)



################################################################################
# DEFINE FUNCTIONS
################################################################################
def argparse_type_log_level(argument):
    """argparse: Defines a valid logging level

    Args:
        argument: the argument passed to the parameter being checked by argparse

    Returns:
        logging level as an integer

    Raises:
        argparse.ArgumentTypeError: argument must be a valid logging level
            either a valid string or integer log level
    """
    if str(argument).isdigit() and argument in list(range(10, 60, 10)):
        return argument
    elif str(argument).upper() in ["DEBUG", "INFO", "WARNING", "ERROR",
    "CRITICAL"]:
        return getattr(logging, argument.upper())
    else:
        raise argparse.ArgumentTypeError("\"{0}\" not a valid log level"\
            .format(argument))

def argparse_type_package_manager(argument):
    """argeparse: Defines a valid package manager options

    Args:
        argument: the argument passed to the parameter being checked by argparse

    Returns:
        package manager as a command

    Raises:
        argparse.ArgumentTypeError: argument must be in the list of supported
        package managers. 
    """
    supported_PMs=["apt", "yum"]
    if str(argument) in supported_PMs:
        return argument
    else:
        raise argparse.ArgumentTypeError("\"{0}\" is not supported by {1}"\
            .format(argument, SCRIPT["name"]))

def argparse_type_verify_server(argument):
    """argeparse: verifies the server

    Args:
        argument: the argument passed to the parameter being checked by argparse

    Returns:
        ip or hostname of LibreNMS server or polling node

    Raises:
        argparse.ArgumentTypeError: argument must be a valid IP or hostname
    """
    server = argument
    response = os.system("ping -c 1 {0} >/dev/null 2>&1".format(server))
    if response == 0:
        return argument
    else:
        raise argparse.ArgumentTypeError("unable to connect to \"{0}\""\
            .format(server))

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

    arggroup_options.add_argument("--operating-system",
        help="Host Operating System", type=str,
        dest="operating_system", required=False)

    arggroup_options.add_argument("--systemd",
        help="prefer systemd", action="store_true", default=False,
        dest="systemd", required=False)

    arggroup_options.add_argument("--collectd",
        help="install and config collectd", action="store_true", default=False,
        dest="collectd", required=False)

    arggroup_options.add_argument("--check_mk",
        help="install check_mk", action="store_true", default=False,
        dest="check_mk", required=False)

    arggroup_options.add_argument("--modules", nargs='+',
        help="list of modules to install for monitoring",
        required=False)

    arggroup_options.add_argument("--server",
        help="LibreNMS server / polling node to attach to",
        type=argparse_type_verify_server, required=False)

    arggroup_options.add_argument("--snmpd-extend-dir",
        help="install snmpd extension scripts. Default: {0}"\
        .format(DEFAULTS["snmpd_extend"]), type=str,
        default=DEFAULTS["snmpd_extend"],
        dest="snmpd_extend_dir", required=False)

    arggroup_options.add_argument("-l", "--log-file",
        help="specifies the file to log to.",
        metavar="FILE", dest="logging_file", type=str,
        required=False)

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

    # set our defaults

    # we fetch the yaml file hosted on github
    response = urllib.urlopen("{0}{1}".format(DEFAULTS["github_url"],
        DEFAULTS["os_yaml"]))
    data=yaml.load(response.read())

    # we instantiate our objects from the yaml file, as OperatingSystem
    # objects
    _os = OperatingSystem(**getattr(data, args.operating_system))
    _os.test()

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
