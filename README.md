To do:
- ~~Add filters to show all categories, top 5, and top 10~~
- add functionality to save all data in a backup repo and keep only the last month in the main repo
- add auto commit and push to git with cron
- add a table with chart information
- add button to switch between last 48 hours, last 7 days, and last month
- make display times eastern
- prettify text on charts a bit
- add cron tab creation to a python script?

How to install:

1. Create a 'fivecalls' user on the host system; log into that account

2. Create the python virtual environment. In a terminal:

# Create a directory for your project (optional)
mkdir ~/my_project
cd ~/my_project

# Create the virtual environment
python3 -m venv ".fivecalls"

3. Activate the environment
source .fivecalls/bin/activate

4. Install dependencies
pip install -r requirements.txt

5. Create .tmp directory in project file if it doesn't exist

6. Create cron job in editor

crontab -e

In the file editor that opens, something along the lines of the below, depending on how often the scripts should run:

0 * * * * cd /home/fivecalls/Projects/fivecalls && /bin/bash -c 'source .fivecalls/bin/activate && python fetch_data.py && deactivate >> .tmp/cron_fetch_data_logfile.log 2>&1'
0 */2 * * * cd /home/fivecalls/Projects/fivecalls && /bin/bash -c 'source .fivecalls/bin/activate && python create_charts.py && deactivate >> .tmp/cron_create_charts_logfile.log 2>&1'



