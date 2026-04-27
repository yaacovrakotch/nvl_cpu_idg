:: Hy Huynh
::
::
:: ww33'2025
:: Auto Load & INIT TP
::

@ECHO OFF
SETLOCAL ENABLEEXTENSIONS ENABLEDELAYEDEXPANSION
CLS

SET CURRENT_VERSION=3.0
SET HDMTTOS_SingleScriptCmd=%HDMTTOS%\Runtime\Release\SingleScriptCmd.exe
SET HDMTTOS_CTRL=%HDMTTOS%\Runtime\Release\HdmtSuperVisorService\HdmtTosCtrl.exe

SET DEBUG=False
:: Default for common repo that does not have Shared directory
SET CURRENT_TP_DIR=%CD%

SET CURRENT_DIR=%CD%
:: Extract the last directory name from CURRENT DIRECTORY
FOR %%A IN ("%CURRENT_DIR%") DO SET LAST_DIR=%%~nxA

IF /I "!DEBUG!" == "True" (
	ECHO CURRENT_TP_DIR=%CURRENT_TP_DIR%
	ECHO CURRENT_DIR=%CURRENT_DIR%
	ECHO LAST_DIR=%LAST_DIR%
)

:: Assume always perfect built TP with no QGate
SET TP_STATUS=POR_TP
SET TP_STATUS_FAILED=POR_TP_FAILED
SET TP_SHARED=True
:: TP was built through GitHub TPBuild
:: Have 1 BOM only in the TP!
IF /I "!LAST_DIR!" == "Shared" (
	
	:: Get the main TP folder (go up one level from TP_DIR\Shared)
	CALL :SUB_GET_CURRENT_TP_DIR
	
	IF /I "!DEBUG!" == "True" (
		ECHO CURRENT_TP_DIR=!CURRENT_TP_DIR!
	)
	CALL :SUB_CHECK_POR_TP_EXIST
	CALL :SUB_COUNT_CURRENT_DIR TP_DIR_COUNT
	
	IF /I "!DEBUG!" == "True" (
		ECHO TP_DIR_COUNT=!TP_DIR_COUNT!
	)
	IF !TP_DIR_COUNT! == 1 (
		:: Get BOM from the TP_STATUS subdirectory
		FOR /D %%C IN ("!CURRENT_TP_DIR!\!TP_STATUS!\*") DO SET TP_BOM=%%~nxC
		IF /I "!DEBUG!" == "True" (
			ECHO TP_BOM=!TP_BOM!
		)
	) ELSE (
		ECHO MUTLIPLE BOMS
		CALL :SUB_SELECT_BOM_FROM_DIR
	)
	
	CALL :SUB_GET_TP_PACKAGE
	IF /I "!DEBUG!" == "True" (
		ECHO TP_PACKAGE=!TP_PACKAGE!
	)
) ELSE (
	SET TP_SHARED=False
	SET CURRENT_TP_DIR=%CD%
	IF /I "!DEBUG!" == "True" (
		ECHO CURRENT_TP_DIR=!CURRENT_TP_DIR!
	)
	CALL :SUB_CHECK_POR_TP_EXIST
	CALL :SUB_SELECT_BOM_FROM_DIR
	CALL :SUB_GET_TP_PACKAGE
)

:: TP built failed
IF /I !TP_STATUS! == !TP_STATUS_FAILED! (
	START EXPLORER "!CURRENT_TP_DIR!\!TP_STATUS!\!TP_BOM!\Reports"
	ECHO *** Check for errors:
	ECHO *** !CURRENT_TP_DIR!\!TP_STATUS!\!TP_BOM!\Reports\build_errors.txt
	ECHO *** !CURRENT_TP_DIR!\!TP_STATUS!\!TP_BOM!\Reports\QGate_report.txt
	ECHO *** Will attempt to load !CURRENT_TP_DIR!\!TP_STATUS!
	ECHO ***
	ECHO *****************************************************************************************************
	ECHO *****************************************************************************************************
)

TITLE " !TP_BOM! TP !CURRENT_TP_DIR! Version: %CURRENT_VERSION% "

:: TP info
SET TP_TPL=BaseTestPlan.tpl
SET TP_PLIST=!TP_STATUS!\!TP_BOM!\PLIST_ALL_!TP_BOM!.plist.xml
SET TP_ENV=!TP_STATUS!\!TP_BOM!\EnvironmentFile.env
SET TP_STPL=!TP_STATUS!\!TP_BOM!\SubTestPlan.stpl

IF /I "!TP_SHARED!" == "True" (
	SET TP_SOCKET=Shared\BaseInputs\Common\Common_!TP_BOM!\HVM_STA.soc
) ELSE (
	SET TP_SOCKET=BaseInputs\Common\Common_!TP_BOM!\HVM_STA.soc
)

ECHO *****************************************************************************************************
ECHO *****************************************************************************************************
:: Check all TP files exist prior to load
IF NOT EXIST "!CURRENT_TP_DIR!\!TP_TPL!" (
	ECHO TPL file does not exist: !CURRENT_TP_DIR!\!TP_TPL!
	GOTO SUB_FILES_NOT_FOUND
)

IF NOT EXIST "!CURRENT_TP_DIR!\!TP_PLIST!" (
	ECHO PLIST file does not exist: !CURRENT_TP_DIR!\!TP_PLIST!
	GOTO SUB_FILES_NOT_FOUND
)

IF NOT EXIST "!CURRENT_TP_DIR!\!TP_ENV!" (
	ECHO ENV file does not exist: !CURRENT_TP_DIR!\!TP_ENV!
	GOTO SUB_FILES_NOT_FOUND
)

IF NOT EXIST "!CURRENT_TP_DIR!\!TP_STPL!" (
	ECHO STPL file does not exist: !CURRENT_TP_DIR!\!TP_STPL!
	GOTO SUB_FILES_NOT_FOUND
)

IF NOT EXIST "!CURRENT_TP_DIR!\!TP_SOCKET!" (
	ECHO SOC file does not exist: !CURRENT_TP_DIR!\!TP_SOCKET!
	GOTO SUB_FILES_NOT_FOUND
)

:: Prompt to restart HDMT TOS
:: Press <Enter> will also restart 
SET /P restartSelection="Do you want to restart HDMT TOS? (<Enter> will also restart HDMT TOS) (Y/N): " || SET restartSelection=Y

:: Press <Enter> will skip Bench Top script(s) before/after INIT
SET /P btTester="Is this a Bench Top tester? (<Enter> default No) (Y/N): " || SET btTester=N
CALL :SUB_CONVERT_TO_UPPER btTester

ECHO *****************************************************************************************************
ECHO *** Override user vars after common batch script call
ECHO *** 
:: Prompt to update SCVars.SC_PACKAGE
:: Press <Enter> will use default from Base TP
SET /P scpackageSelection="Update SCVars.SC_PACKAGE (2 characters)? (<Enter> to use default from Base TP): " || SET scpackageSelection=NOTHINGCHOSEN
CALL :SUB_CONVERT_TO_UPPER scpackageSelection

:: Prompt to update SCVars.SC_STEP
:: Press <Enter> will use default from Base TP
SET /P scstepSelection="Update SCVars.SC_STEP (1 character)? (<Enter> to use default from Base TP): " || SET scstepSelection=NOTHINGCHOSEN
CALL :SUB_CONVERT_TO_UPPER scstepSelection

:: Prompt to update SCVars.SC_DEVICE
:: Press <Enter> will use default from Base TP
SET /P scdeviceSelection="Update SCVars.SC_DEVICE (6 characters)? (<Enter> to use default from Base TP): " || SET scdeviceSelection=NOTHINGCHOSEN
CALL :SUB_CONVERT_TO_UPPER scdeviceSelection

:: Prompt to update SCVars.SC_REV
:: Press <Enter> will use default from Base TP
SET /P screvSelection="Update SCVars.SC_REV (1 character)? (<Enter> to use default from Base TP): " || SET screvSelection=NOTHINGCHOSEN
CALL :SUB_CONVERT_TO_UPPER screvSelection

:: Prompt to update SCVars.SC_DIESLCT
:: Press <Enter> will use default from Base TP
SET /P dieSelection="Update SCVars.SC_DIESLCT? (<Enter> to use default from Base TP): " || SET dieSelection=NOTHINGCHOSEN
CALL :SUB_CONVERT_TO_UPPER dieSelection

:: Restart TOS?
IF /I "%restartSelection%" == "Y" (
	ECHO *****************************************************************************************************
	ECHO HDMT TOS restart, please wait...
	ECHO ***
	%HDMTTOS_CTRL% restarttos
)

:: Load TP
ECHO *****************************************************************************************************
ECHO TP LOAD, please wait...
ECHO ***
ECHO   !CURRENT_TP_DIR!
ECHO      !TP_TPL!
ECHO      !TP_STPL!
ECHO      !TP_ENV!
ECHO      !TP_PLIST!
ECHO      !TP_SOCKET!

:: Close Site Controller
TASKKILL /F /IM HdmtSiteControllerStudio.exe /FI "STATUS eq RUNNING"
%HDMTTOS_SingleScriptCmd% loadTP "!CURRENT_TP_DIR!" "!TP_TPL!" "!TP_PLIST!" "!TP_ENV!" "!TP_STPL!" "!TP_SOCKET!"

:: Wait 120 seconds and re-open Site Controller
TIMEOUT /T 120 /NOBREAK
START %HDMTTOS%\Runtime\Release\GUIs\HdmtSiteControllerStudio.exe

ECHO *****************************************************************************************************
ECHO Call common batch script, please wait...
ECHO ***
IF /I "!TP_SHARED!" == "True" (
	CALL !CURRENT_TP_DIR!\Shared\nvl_common_cmd_!TP_PACKAGE!.bat
	IF /I "!TP_SHARED!" == "True" (
		ECHO !CURRENT_TP_DIR!\Shared\nvl_common_cmd_!TP_PACKAGE!.bat
	)
) ELSE (
	CALL !CURRENT_TP_DIR!\nvl_common_cmd_!TP_PACKAGE!.bat
	IF /I "!TP_SHARED!" == "True" (
		ECHO !CURRENT_TP_DIR!\nvl_common_cmd_!TP_PACKAGE!.bat
	)
)

IF /I "!btTester!" == "Y" (
	ECHO *****************************************************************************************************
	ECHO Bench Top tester, remember to execute before_init batch script.
	ECHO Open before_init directory for scripts
	ECHO ***
	IF /I "!TP_SHARED!" == "True" (
		START EXPLORER "!CURRENT_TP_DIR!\Shared\!TP_STATUS!\!TP_BOM!\Scripts\before_init"
		IF /I "!TP_SHARED!" == "True" (
			ECHO "!CURRENT_TP_DIR!\Shared\!TP_STATUS!\!TP_BOM!\Scripts\before_init"
		)
	) ELSE (
		START EXPLORER "!CURRENT_TP_DIR!\!TP_STATUS!\!TP_BOM!\Scripts\before_init"
		IF /I "!TP_SHARED!" == "True" (
			ECHO "!CURRENT_TP_DIR!\!TP_STATUS!\!TP_BOM!\Scripts\before_init"
		)
	)
	PAUSE
)

:: Update SCVars.SC_PACKAGE
IF NOT "%scpackageSelection%" == "NOTHINGCHOSEN" (
	ECHO *****************************************************************************************************
	ECHO Updating SCVars.SC_PACKAGE to: %scpackageSelection%
	ECHO ***
	%HDMTTOS_SingleScriptCmd% setUserVar "SCVars" "SC_PACKAGE" "%scpackageSelection%"
)

:: Update SCVars.SC_STEP
IF NOT "%scstepSelection%" == "NOTHINGCHOSEN" (
	ECHO *****************************************************************************************************
	ECHO Updating SCVars.SC_STEP to: %scstepSelection%
	ECHO ***
	%HDMTTOS_SingleScriptCmd% setUserVar "SCVars" "SC_STEP" "%scstepSelection%"
)

:: Update SCVars.SC_DEVICE
IF NOT "%scdeviceSelection%" == "NOTHINGCHOSEN" (
	ECHO *****************************************************************************************************
	ECHO Updating SCVars.SC_DEVICE to: %scdeviceSelection%
	ECHO ***
	%HDMTTOS_SingleScriptCmd% setUserVar "SCVars" "SC_DEVICE" "%scdeviceSelection%"
)

:: Update SCVars.SC_REV
IF NOT "%screvSelection%" == "NOTHINGCHOSEN" (
	ECHO *****************************************************************************************************
	ECHO Updating SCVars.SC_REV to: %screvSelection%
	ECHO ***
	%HDMTTOS_SingleScriptCmd% setUserVar "SCVars" "SC_REV" "%screvSelection%"
)

:: Update SCVars.SC_DIESLCT
IF NOT "%dieSelection%" == "NOTHINGCHOSEN" (
	ECHO *****************************************************************************************************
	ECHO Updating SCVars.SC_DIESLCT to: %dieSelection%
	ECHO ***
	%HDMTTOS_SingleScriptCmd% setUserVar "SCVars" "SC_DIESLCT" "%dieSelection%"
)

ECHO *****************************************************************************************************
ECHO TP INIT, please wait...
%HDMTTOS_SingleScriptCmd% init
ECHO *****************************************************************************************************
ECHO *****************************************************************************************************
ECHO ***Confirm INIT PASS prior to LOT start.
ECHO *****************************************************************************************************
ECHO *****************************************************************************************************
PAUSE

IF /I "!btTester!" == "Y" (
	ECHO *****************************************************************************************************
	ECHO Bench Top tester, remember to execute after_init batch script.
	ECHO Open after_init directory for scripts
	ECHO ***
	IF /I "!TP_SHARED!" == "True" (
		START EXPLORER "!CURRENT_TP_DIR!\Shared\!TP_STATUS!\!TP_BOM!\Scripts\after_init"
		IF /I "!TP_SHARED!" == "True" (
			ECHO "!CURRENT_TP_DIR!\Shared\!TP_STATUS!\!TP_BOM!\Scripts\after_init"
		)
	) ELSE (
		START EXPLORER "!CURRENT_TP_DIR!\!TP_STATUS!\!TP_BOM!\Scripts\after_init"
		IF /I "!TP_SHARED!" == "True" (
			ECHO "!CURRENT_TP_DIR!\!TP_STATUS!\!TP_BOM!\Scripts\after_init"
		)
	)
	PAUSE
)

ECHO *****************************************************************************************************
ECHO TP LOT START, please wait...
%HDMTTOS_SingleScriptCmd% startLot
ECHO *****************************************************************************************************
ECHO *****************************************************************************************************
ECHO ***LOT START DONE
ECHO ***Confirm LOT START PASS prior to socket the unit.
ECHO *****************************************************************************************************
ECHO *****************************************************************************************************
PAUSE
GOTO EOF


:SUB_FILES_NOT_FOUND
ECHO *****************************************************************************************************
ECHO *****************************************************************************************************
ECHO TEST PROGRAM WILL NOT AUTO LOAD!
ECHO *****************************************************************************************************
ECHO *****************************************************************************************************
PAUSE
GOTO EOF


:SUB_CHECK_POR_TP_EXIST
:: TP_DIR\POR_TP does not exist, set TP_DIR\POR_TP_FAILED
IF NOT EXIST "!CURRENT_TP_DIR!\%TP_STATUS%" (
	ECHO *****************************************************************************************************
	ECHO *****************************************************************************************************
	ECHO *** !CURRENT_TP_DIR!\!TP_STATUS! doesn't exist!
	ECHO ***
	SET TP_STATUS=%TP_STATUS_FAILED%
)
EXIT /B

:SUB_GET_TP_PACKAGE
:: Get the last underscore value from the BOM
FOR /F "tokens=3 delims=_" %%D IN ("!TP_BOM!") DO SET TP_PACKAGE=%%D

:SUB_GET_CURRENT_TP_DIR
IF /I "!TP_SHARED!" == "True" (
	:: Get the main TP folder (go up one level from TP_DIR\Shared)
	FOR %%A IN ("%CD%\..") DO SET CURRENT_TP_DIR=%%~fA
	IF /I "!DEBUG!" == "True" (
		ECHO "SHARED TP: CURRENT_TP_DIR=%CURRENT_TP_DIR%"
	)
) ELSE (
	SET CURRENT_TP_DIR=%CD%
	IF /I "!DEBUG!" == "True" (
		ECHO "NOT SHARED TP: CURRENT_TP_DIR=%CURRENT_TP_DIR%"
	)
)
EXIT /B


:SUB_COUNT_CURRENT_DIR
:: Initialize counter
SET COUNT=0

IF /I "!DEBUG!" == "True" (
	ECHO Counting directories in: !CURRENT_TP_DIR!\!TP_STATUS!
)

:: Count directories (non-recursive)
FOR /D %%D IN ("!CURRENT_TP_DIR!\!TP_STATUS!\*") DO (
	SET /a COUNT+=1
	IF /I "!DEBUG!" == "True" (
		ECHO Directory !COUNT!: %%~nxD
	)
)
SET %~1=!COUNT!
EXIT /B


:SUB_SELECT_BOM_FROM_DIR
:: Initialize variables
SET BOM_COUNT=0

:: Loop through directories and build the BOM list
IF /I "!DEBUG!" == "True" (
	ECHO Building directory list...
	ECHO !CURRENT_TP_DIR!\!TP_STATUS!
)

FOR /D %%B IN ("!CURRENT_TP_DIR!\!TP_STATUS!\*") DO (
	SET /A BOM_COUNT+=1
	IF /I "!DEBUG!" == "True" (
		ECHO BOM_FOUND=%%~nxB
	)
	SET "DIR_NAME[!BOM_COUNT!]=%%~nxB"
)

:: Display the menu options
ECHO Select BOM to load
FOR /L %%i IN (1,1,!BOM_COUNT!) DO (
	ECHO     %%i. !DIR_NAME[%%i]!
)
ECHO     0. Exit

:: Get user selection
SET /P BOM_SELECTION="Enter your BOM selection (0-!BOM_COUNT!): "

:: Validate the selection
SET "VALID=False"
IF "!BOM_SELECTION!"=="0" (
	ECHO Exiting...
	EXIT
)

:: Check if selection is a number within range
FOR /L %%i IN (1,1,!BOM_COUNT!) DO (
	IF "!BOM_SELECTION!"=="%%i" SET "VALID=True"
)

IF /I "!VALID!"=="False" (
	ECHO Invalid selection. Please enter a number between 0 and !BOM_COUNT!.
	PAUSE
	GOTO SUB_SELECT_BOM_FROM_DIR
)

IF /I "!DEBUG!" == "True" (
	ECHO BOM_SELECTION=%BOM_SELECTION%
	ECHO TP_BOM=!DIR_NAME[%BOM_SELECTION%]!
)
SET TP_BOM=!DIR_NAME[%BOM_SELECTION%]!
EXIT /B


:SUB_CONVERT_TO_UPPER
:: Convert the content of the variable to UPPERCASE
SET %~1=!%~1:a=A!
SET %~1=!%~1:b=B!
SET %~1=!%~1:c=C!
SET %~1=!%~1:d=D!
SET %~1=!%~1:e=E!
SET %~1=!%~1:f=F!
SET %~1=!%~1:g=G!
SET %~1=!%~1:h=H!
SET %~1=!%~1:i=I!
SET %~1=!%~1:j=J!
SET %~1=!%~1:k=K!
SET %~1=!%~1:l=L!
SET %~1=!%~1:m=M!
SET %~1=!%~1:n=N!
SET %~1=!%~1:o=O!
SET %~1=!%~1:p=P!
SET %~1=!%~1:q=Q!
SET %~1=!%~1:r=R!
SET %~1=!%~1:s=S!
SET %~1=!%~1:t=T!
SET %~1=!%~1:u=U!
SET %~1=!%~1:v=V!
SET %~1=!%~1:w=W!
SET %~1=!%~1:x=X!
SET %~1=!%~1:y=Y!
SET %~1=!%~1:z=Z!
EXIT /B