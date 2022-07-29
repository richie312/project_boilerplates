@echo OFF
set current_dir=%cd%
SET user_name=%USERNAME%
SET project_name=%1
SET env_file_name=%project_name%.bat
echo The working directory is %current_dir%
echo The current user is %user_name%
echo Virtual env and project setup is initialised for %project_name% ...

timeout /t 10
cd C:\users\%user_name%\envs
pip install virtualenv
virtualenv %project_name%
%project_name%\Scripts\Activate.bat
pip install -r requirements.txt
cd %current_dir%
echo c:\users\%user_name%\envs\%project_name%\bin\Scripts\Activate.bat > %env_file_name%
echo The environment filename %env_file_name% is created to activate the environment.
