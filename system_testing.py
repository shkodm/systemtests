"""Script for system testing preCICE with docker and comparing output.

This script builds a docker image for an system test of preCICE.
It starts a container of the builded image and copys the output generated by the
simulation within the test to the host.
The output is compared to a reference.
It passes if files are equal, else it raises an exception.

Example:
    System test of-of and use local preCICE image

        $ python system_testing.py -s of-of -l
"""

import argparse, filecmp, os, sys
import common
from common import call

# Parsing flags
parser = argparse.ArgumentParser(description='Build local.')
parser.add_argument('-l', '--local', action='store_true', help="use local preCICE image (default: use remote image)")
parser.add_argument('-s', '--systemtest', help="choose system tests you want to use", choices = common.get_tests())
parser.add_argument('-b', '--branch', help="preCICE branch to use", default = "develop")
args = parser.parse_args()

def build(systest):
    """Building docker image.

    This function builds a docker image with the respectively system test,
    runs a container in background to copy the output generated by the
    simulation to the host:

    Args:
        systest (str): Name of the system test.
    """
    dirname = "/Test_" + systest
    print(os.getcwd() + dirname)
    os.chdir(os.getcwd() + dirname)
    print(os.getcwd())
    if args.local:
        call("docker build -t {systest} --build-arg from=precice-{branch}:latest .".format(systest = systest, branch = args.branch))
    else:
        call("docker build -t " + systest + " .")
    call("docker run -it -d --name "+ systest +"_container " + systest)
    call("docker cp " + systest + "_container:Output_" + systest + " .")

def comparison(pathToRef, pathToOutput):
    """Building docker image.

    This function builds a docker image with the respectively system test,
    runs a container in background to copy the output generated by the
    simulation to the host:

    Args:
        pathToRef (str): Path to the reference files.
        pathToOutput (str): Path to the output files.

    Raises:
        Exception: Raises exception then output differs from reference.
    """
    fileListRef = os.listdir(pathToRef)
    fileListOutput = os.listdir(pathToOutput)

    fileListRef.sort()
    fileListOutput.sort()

    for x, y in zip(fileListRef, fileListOutput):
        if os.path.isdir(pathToRef+x):
            comparison(pathToRef+x+'/', pathToOutput+y+'/')
        else:
            if not filecmp.cmp(pathToRef + x, pathToOutput + y):
                raise Exception('Output differs from reference')

if __name__ == "__main__":
    # Build
    build(args.systemtest)
    # Preparing string for path
    pathToRef = os.getcwd() + "/referenceOutput_" + args.systemtest + "/"
    pathToOutput = os.getcwd() + "/Output_" + args.systemtest + "/"
    # Comparing
    comparison(pathToRef, pathToOutput)
