#!/usr/bin/env groovy

pipeline {
    agent any

    triggers {
      cron('0 6 * * *') // run every day at 11pm PST
    }

    options {
      buildDiscarder(logRotator(daysToKeepStr: '2'))
    }

    environment {
      SF_ROLE="SYSADMIN"
      SF_DATABASE="SPLIT"
      SF_WAREHOUSE="COMPUTE_WH"
      SF_CRED=credentials("SNOWFLAKE")
      SF_ACCOUNT="bv23770.us-east-1"

      // State File
      DATADOG_STATE="./states/datadog.json"

      // Python Enviroments
      VENV_DATADOG="venv/tap-datadog"
      VENV_SF="venv/target-snowflake"

    }

    stages {

        stage('Create States directory') {
          steps {
            sh "mkdir -p ./states"
          }
        } // Stage States Directory

        stage('Create Venvs') {
          parallel {
            stage('Venv Datadog') {
              environment {
                SOURCE_INSTALL='.[dev]'
                FLAG="-e"
              }
              steps {
                sh './createVenv.sh "${VENV_DATADOG}" "${SOURCE_INSTALL}" "${FLAG}"'
              }
            }// stage Venv Datadog
            stage('Venv Snowflake') {
              environment {
                SOURCE_INSTALL='git+https://gitlab.com/meltano/target-snowflake.git@master#egg=target-snowflake'
                FLAG="-e"
              }
              steps {
                sh './createVenv.sh "${VENV_SF}" "${SOURCE_INSTALL}" "${FLAG}"'
              }
            } // Stage Venv Snowflake
            stage('State Datadog'){
              steps{
                setState("${DATADOG_STATE}")
              }
            }// stage State Datadog
          } // Parallel
        } // Stage Create Venv

        stage('Run Tap-datadog'){
          environment{
            DATADOG_START_MONTH="2019-07"
            DATADOG_START_HOUR="2019-06-17T12"
            DATADOG_API_KEY=credentials('DATADOG_API_KEY')
            DATADOG_APPLICATION_KEY=credentials('DATADOG_APPLICATION_KEY')
            SF_SCHEMA="DATADOG"
            SF_CONFIG_FILE="config-snoflake-datadog.json"
            TAP_OUTPUT="tap-datadog-output.json"
            STDERRFILE="stderr_datadog.out"
          }
          steps{
            script{
                sh(returnStdout: false, script: 'set -euo pipefail')
                sh(returnStdout: false, script: 'envsubst < config-datadog.json.tpl > config-datadog.json')
                sh(returnStdout: false, script: 'envsubst < config-snowflake.json.tpl > "${SF_CONFIG_FILE}"')
                status=sh(returnStatus: true, script: '${VENV_DATADOG}/bin/tap-datadog -c config-datadog.json --catalog datadog-properties.json -s "${DATADOG_STATE}" > "${TAP_OUTPUT}" 2>"${STDERRFILE}"')
                catchError(status, "Tap-datadog", "Failed to collect data.", "${STDERRFILE}")
                status=sh(returnStdout: false, script:'echo -e "\n" >>  ${DATADOG_STATE}')
                status=sh(returnStatus: true, script: 'cat ${TAP_OUTPUT} | ${VENV_SF}/bin/target-snowflake -c "${SF_CONFIG_FILE}" >> ${DATADOG_STATE} 2>"${STDERRFILE}"')
                catchError(status, "Tap-datadog", "Failed to send data.", "${STDERRFILE}")
            }
          }
        }// stage Run Tap-datadog

    } // Stages

    post{

      success{
        slackSend(channel: "#analytics-alerts", message: "Tap-datadog Worked.", color: "#008000")
      }
      always{
        cleanWs (
          deleteDirs: false,
          patterns: [
            [pattern: 'config*.json', type: 'INCLUDE'],
            [pattern: '*output*.json', type: 'INCLUDE'],
            [pattern: 'stderr*.out', type: 'INCLUDE']
          ]
        )
      }//always
    }// post
} // Pipeline

def setState(state){
  def exists = fileExists state
  if (exists) {
    def file = readFile state
    def last = file.split("\n")[file.split("\n").length-1]
    writeFile file: state, text : last
    def count = sh(returnStdout:true, script:'cat '+ state + ' | tr \' \' \'\n\' | grep bookmark | wc -l').trim()
    echo count
    sh(returnStdout:true, script:'cat ' + state)
  }
  else {
    writeFile file: state, text: '{}'
  }
}

def catchError(status, tap, message, stderrfile){
  if (status != 0) {
    def output = readFile(stderrfile)
    print(output)
    slackSend(channel: "#analytics-alerts", message: "*$tap:* $message \n *Reason:* $output", color: "#ff0000")
    currentBuild.result = 'FAILED'
    error "$message"
  }
}
