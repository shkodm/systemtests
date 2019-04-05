"""Script for pushing output and logfile to a repository.

This script pushes output files of a system test, if they exists, and a logfile
to the repository: https://github.com/precice/precice_st_output.

    Example:
        Example use to push output files and logfile of system test of-of:

            $ python push.py -s -t of-of
"""

from trigger_systemtests import last_successfull_commit, get_job_commit
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import argparse, os, sys, time
from common import ccall, capture_output, get_test_participants

def get_travis_job_log(job_id, tail = 100):

    txt_url = "https://api.travis-ci.org/v3/job/{}/log.txt".format(job_id)
    req = Request(txt_url)
    response = urlopen( req ).read().decode()
    job_log = "\n".join( response.split("\n")[-tail:] )
    return job_log


def create_job_log(test, log, exit_status):

    make_md_link = lambda name, link: "[{name}]({link})".format(name=
            name, link=link)

    build_url = os.environ["TRAVIS_BUILD_WEB_URL"]
    log.write(" # Status : " + (" Passing " if not exit_status else\
        "Failing") + "\n")
    log.write(" # " + make_md_link("Job url", build_url) + "\n")

    event_type = os.environ["TRAVIS_EVENT_TYPE"]
    triggered_commit = os.environ["TRAVIS_COMMIT"]
    job_id = os.environ["TRAVIS_JOB_ID"]

    # Decipher commit from the job message
    if (event_type == "api"):

        commit_message = os.environ["TRAVIS_COMMIT_MESSAGE"]
        job_that_triggered = commit_message.split("Triggered by:")[-1]
        if job_that_triggered == "manual script call":
           event_type = "manual trigger"
        else:
           *_, adapter_name, _, adapter_job_id = job_that_triggered.split('/')
           triggered_commit = get_job_commit(adapter_job_id)
           event_type = "commit to the {}".format(adapter_name)
    else:
        triggered_commit = get_job_commit(job_id)

    log.write("## Triggered by: " + ( make_md_link(event_type, triggered_commit['compare_url'])) + "\n")

    if exit_status:

        adapters =  get_test_participants(test)
        last_good_commits = {}

        if adapters:
            for adapter in adapters:
                last_good_commits[adapter] = last_successfull_commit('precice', adapter).get('compare_url')

        last_good_commits['systemtests'] = last_successfull_commit('precice', 'systemtests').get('compare_url')

        failed_info = "## Last succesfull commits \n* " + "\n* ".join([make_md_link(name, commit) for name, commit in
                last_good_commits.items()]) + "\n"

        log.write(failed_info)

    log.write("## Last 100 lines of the job log...\n")
    log.write('```\n')
    log.write(get_travis_job_log(job_id))
    log.write('```\n')
    log.write(make_md_link("Full job log", "https://api.travis-ci.org/v3/job/{}/log.txt".format(job_id)))

if __name__ == "__main__":

    # Parsing flags
    parser = argparse.ArgumentParser(description='Build local.')
    parser.add_argument('-t', '--test', help="choose system tests you want to use")
    parser.add_argument('-s', '--success', action='store_true' ,help="only upload log file")
    parser.add_argument('-o', '--os', type=str,help="Version of Ubuntu to use", choices =
                ["1804", "1604"], default= "1604")

    args = parser.parse_args()

    systest = args.test
    # Creating new logfile
    log = open("log_" + systest + ".md", "w")
    localtime = str(time.asctime(time.localtime(time.time())))
    log.write("System testing at " + localtime + "\n")
    create_job_log(systest,log, not args.success)
    log.close()
    # Push output file and logfile to repo.
    # Clone repository.
    ccall("git clone https://github.com/precice/precice_st_output")
    log_dir = os.getcwd() + "/precice_st_output/Ubuntu" + args.os
    ccall("mkdir -p " + log_dir)
    ccall("mv log_" + systest + ".md " + log_dir)

    commit_msg_lines = []

    if not args.success:

        system_suffix = args.os
        # Move ouput to folder of this test case
        test_folder = os.getcwd() + '/Test_' + systest + system_suffix
        if not os.path.isdir(test_folder):
            test_folder = 'Test_' + systest
        source_dir = test_folder + "/Output"
        dest_dir = log_dir + "/Output_" + systest
        # source folder was not created, we probably failed before producing
        # any of the results
        travis_build_number = os.environ["TRAVIS_BUILD_NUMBER"]
        travis_job_web_url = os.environ["TRAVIS_JOB_WEB_URL"]

        if (not os.path.isdir(source_dir)):
            os.chdir(log_dir)
            ccall(["git add ."])
            commit_msg_lines = ["Failed to produce results", "Build url: {}".format(travis_job_web_url)]
        else:
            os.chdir(log_dir)
            # something was committed to that folder before -> overwrite it
            if os.path.isdir(dest_dir):
                ccall("git rm -rf {}".format(dest_dir))
            ccall("mv {} {}".format(source_dir, dest_dir))
            ccall("git add .")
            commit_msg_lines = ["Output != Reference build number: {}".format(travis_build_number), "Build url:\ {}".format(travis_job_web_url)]
    else:
        os.chdir(log_dir)
        ccall("git add .")
        # remove previously failing results, if we succeed
        ccall("git rm -r --ignore-unmatch Output_" + systest)
        commit_msg_lines = ["Output == Reference build number: {}".format(travis_build_number), "Build url: {}".format(travis_job_web_url)]

    commit_msg = " ".join(map( lambda x: "-m \"" + x + "\"", commit_msg_lines))
    ccall("git commit " + commit_msg)
    ccall("git remote set-url origin https://${GH_TOKEN}@github.com/precice/precice_st_output.git > /dev/null 2>&1")
    ccall("git push")
