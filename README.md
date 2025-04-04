To do:
- Add summary stats that identify the category (or two) with the most calls and largest increase in calls during the time period

How to install:

1. Create a 'fivecalls' user on the host system; log into that account
2. Create a Projects folder in the user directory
3. Clone the code the Projects repo: git clone git@github.com:31Oaks/fivecalls.git
3b. Optional: If you want to keep a historical backup, create a 'fivecallsdatabackup' folder. If not, be sure to change the code in 'fetch_data.py' to not write to 'fivecallsdatabackup'
4. Create the python virtual environment. In a terminal:

  python3 -m venv ".fivecalls"

5. Activate the environment
   
  source .fivecalls/bin/activate

6. Install dependencies

  pip install -r requirements.txt

7. Create .tmp directory in project file if it doesn't exist

8. Create cron job in editor
   
  crontab -e

In the file editor that opens, something along the lines of the below, depending on how often the scripts should run:

  50 * * * * cd /home/fivecalls/Projects/fivecalls && /bin/bash -c 'source .fivecalls/bin/activate && python fetch_data.py && deactivate >> .tmp/cron_fetch_data_logfile.log 2>&1'   
  55 * * * * cd /home/fivecalls/Projects/fivecalls && /bin/bash -c 'source .fivecalls/bin/activate && python create_charts.py && deactivate >> .tmp/cron_create_charts_logfile.log 2>&1'   



