*** Settings ***
Documentation     Check if given dates have available reservations
Suite Setup       Open Browser To Login Page
Suite Teardown    Cleanup
Resource          resource.robot
Library           OperatingSystem

*** Variables ***
${ROUTE}          Hyannis to Nantucket

${DEPART DATE}    Aug 20
${DEPART AFTER}    12:00 am
${DEPART BEFORE}   5:30 pm

${RETURN DATE}    Aug 27
${RETURN AFTER}    12:00 am
${RETURN BEFORE}  11:59 pm

*** Test Cases ***
Ferry check
    Select Route    ${ROUTE}    ${DEPART_DATE}    ${RETURN_DATE}
    Find Availability    departures    ${DEPART AFTER}    ${DEPART BEFORE}
    Find Availability    returns    ${RETURN AFTER}    ${RETURN BEFORE}

