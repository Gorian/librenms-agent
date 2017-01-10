#!/usr/bin/env python
################################################################################
# LibreNMS Client Install Script
# Layne "Gorian" Breitkreutz
# Sets up the client for monitoring with LibreNMS
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
from logging.handlers import RotatingFileHandler

################################################################################
# DEFINE GLOBAL CONSTANTS
################################################################################
SCRIPT_VERSION = "0.0.1"
SCRIPT_EXECUTION = os.path.basename(__file__)
SCRIPT_NAME = "LibreNMS Client Install"
HOSTNAME = socket.gethostname()
HOST_FQDN = socket.getfqdn()
TODAY = datetime.date.today()
HOME_DIRECTORY = os.path.expanduser('~')
ROWS, COLUMNS = os.popen('stty size', 'r').read().split()
FORMAT_WIDTH = 30

################################################################################
# DEFINE CLASSES
################################################################################

################################################################################
# DEFINE FUNCTIONS
################################################################################
def argparse_type_log_level(argument):
    """Defines a custom argparse argument type

    Defines a valid logging level

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
    """Defines a custom argparse argument type

    Defines a valid package manager options

    Args:
        argument: the argument passed to the parameter being checked by argparse

    Returns:
        package manager as a command

    Raises:
        argparse.ArgumentTypeError: argument must be a valid logging level
            either a valid string or integer log level
    """
    supported_PMs=["apt", "yum"]
    if str(argument) in supported_PMs:
        return argument
    else:
        raise argparse.ArgumentTypeError("\"{0}\" is not supported by {1}"\
            .format(argument, SCRIPT_NAME))


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
    parser = argparse.ArgumentParser(description=SCRIPT_NAME,
        add_help=False,)
    arggroup_options = parser.add_argument_group("options")

    arggroup_options.add_argument("--systemd",
        help="prefer systemd", action="store_true",
        dest="systemd", required=False)

    arggroup_options.add_argument("--collectd",
        help="install and config collectd", action="store_true",
        dest="collectd", required=False)

    arggroup_options.add_argument("--check_mk",
        help="install check_mk", action="store_true",
        dest="check_mk", required=False)

    arggroup_options.add_argument("--modules", nargs='+',
        help="list of modules to install for monitoring",
        required=False)

    arggroup_options.add_argument("--package-manager",
        help="package manager to use on host",
        type=argparse_type_package_manager, required=False)

    arggroup_options.add_argument("--snmps_extend",
        help="install snmpd extension scripts", action="store_true",
        dest="snmpd_extend", required=False)

    arggroup_options.add_argument("-l", "--log-file",
        help="specifies the file to log to.",
        metavar="FILE", dest="logging_file", type=str,
        required=False)

    arggroup_options.add_argument("-d", "--debug",
        help="enables debug messages. Sets logging level to DEBUG.",
        action="store_true", dest="debug",
        required=False)

    arggroup_options.add_argument("-v", "--version", action="version",
        version="{0} {1}".format(SCRIPT_NAME, SCRIPT_VERSION))

    arggroup_options.add_argument("-h", "--help", action="help",
        help="show this help message and exit")

    # we handle no arguments
    # (always at least 1. sys.argv[0] is the program name)
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    # parse the args and assign them to "args"
    args = parser.parse_args()

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
