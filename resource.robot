*** Settings ***
Documentation     A resource file for checking Steamship ferry availability.
Library           SeleniumLibrary     run_on_failure=NOTHING
Library           DateTime
Library           String

*** Variables ***
${STEAMSHIP URL}  https://www.steamshipauthority.com/schedules/availability
${BROWSER}        headlesschrome
${DELAY}          0
${PUSHBULLET KEY}    o.WsFOYRwuiBUF0VZwSiD1LZmcAM4PbEMw

*** Keywords ***
Open Browser To Login Page
    ${chrome_options} =     Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
    ${options}=     Call Method     ${chrome_options}    to_capabilities
    Open Browser    ${STEAMSHIP URL}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    Title Should Be    Car Reservation Availability to Nantucket & Martha’s Vineyard | The Steamship Authority

Select Date From Datepicker
    [Arguments]    ${elem}    ${date}
    ${month}    ${day} =    Split String    ${date}
    Click Element    name:${elem}
    Select From List By Label    class:ui-datepicker-month    ${month}
    Click Element    xpath://*[@id='ui-datepicker-div']/table/tbody/tr/td[contains(., ${day})]

Select Route
    [Arguments]    ${route}    ${departure}    ${return}
    Select From List By Label    name:route    ${route}
    Select Date From Datepicker    depart_date    ${departure}
    Select Date From Datepicker    return_date    ${return}
    Click Button    Show Me
    Wait Until Element Is Visible    class:returned_trips

Convert Time To Integer
    [Arguments]    ${clock_time}
    ${hour_minute}    ${am_flag} =    Split String    ${clock_time}
    ${time_as_minutes} =    Convert Time    ${hour_minute}
    ${time_am} =    Evaluate    ${time_as_minutes} % (12*60)
    ${time_pm} =    Evaluate    ${time_am} + (12*60)
    ${time_24} =    Set Variable If    "${am_flag}" == "am"    ${time_am}    ${time_pm}
    [return]    ${time_24}

Find Availability
    [Arguments]    ${class_val}    ${after}=12:00 am    ${before}=11:59 pm
    ${after_int} =     Convert Time To Integer    ${after}
    ${before_int} =    Convert Time TO Integer    ${before}

    ${rows} =    Get Element Count    xpath://*[@class="${class_val}"]/table/tbody/tr
    FOR    ${index}    IN RANGE    1    ${rows} + 1
        ${time_text} =    Get Text    xpath://*[@class="${class_val}"]/table/tbody/tr[${index}]/td[1]
        ${time_int} =    Convert Time To Integer    ${time_text}
        ${availability} =    Get Text    xpath://*[@class="${class_val}"]/table/tbody/tr[${index}]/td[6]
        Run Keyword If    "${availability}" != "Full" and ${time_int} > ${after_int} and ${time_int} < ${before_int}     Notify    "Ferry found for ${class_val} at ${time_text}!"
    END

Notify
    [Arguments]    ${message}
    Run    export PUSHBULLET_KEY=${PUSHBULLET KEY} && pb push ${message}

Cleanup
    Close Browser

