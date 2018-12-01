#!/bin/sh

# body of the new travis build
# we don't want to trigger rebuild of everything
# so we need to specify only needed job explicitely
# envirionment variables for pushing to github are presereved
# since config are new and old config are saved using 'push-strategy'
# generation of jobs should be also automated somehow
body='{
"request": {
  "message": "OpenFOAM new commit test",
  "branch":"master",
    "config": {
      "language": "python",
      "services": "docker",
      "python": "3.5",
      "jobs": {
        "include":[
          {
            "name": "[16.04] OpenFOAM <-> OpenFOAM",
            "script": "python system_testing.py -s of-of",
            "after_success": "python push.py -s -t of-of",
            "after_failure": "python push.py -t of-of; bash trigger_systemtests.sh -c shkodm openfoam-adapter"
          },
          {
            "name": "[18.04] OpenFOAM <-> OpenFOAM",
            "script": "python system_testing.py -s of-of -o 1804",
            "after_success": "python push.py -s -t of-of -o 1804",
            "after_failure": "python push.py -t of-of -o 1804; bash trigger_systemtests.sh -c shkodm openfoam-adapter"
          }
        ]
      }
    }
}}'


callback_body='{
"request": {
  "message": "Build failed",
  "branch":"master",
    "config": {
      "jobs": {
      "include":{
          "name": "Systemtest failure callback",
          "script": "false"
        }
      }
    }
}}'

# get if we are calling back or not
for i in "$@"
do
  case $i in
    -c|--callback)
      body="${callback_body}"
      shift
      ;;
  esac
done

TRAVIS_URL=travis-ci.org
USER=$1
REPO=$2

curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Travis-API-Version: 3" \
  -H "Authorization: token ${TRAVIS_ACCESS_TOKEN}" \
  -d "$body" \
  https://api.${TRAVIS_URL}/repo/${USER}%2F${REPO}/requests \
