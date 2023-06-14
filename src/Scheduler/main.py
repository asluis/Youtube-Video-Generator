from crontab import CronTab
import yaml
import os
import sys
import requests
import json
import pika

"""
Reading through the config.yaml file for a schedule and a list of subreddits that will be processed
following that schedule.
"""
def loadConfig() -> dict:
    config = None
    try:
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)

    except OSError:
        print("config.yaml does not exist. Please make sure it is named correctly.")
        exit(1)

    return config


def addCronJob(schedule: dict) -> None:
    cron = CronTab(user='root')  # Assumes Linux OS

    data = str(schedule['subreddits'])
    job = cron.new(command=f"python3 {os.path.abspath(__file__)} {data}")

    minute = schedule['minute']
    hour = schedule['hour']
    day = schedule['day']
    month = schedule['month']
    day_of_week = schedule['day_of_week']

    job.setall(f"{minute} {hour} {day} {month} {day_of_week}")
    cron.write()


def processSchedules() -> None:
    schedules = loadConfig()['schedule']

    for schedule in schedules:
        addCronJob(schedule)


if __name__ == "__main__":
    #  Make a call to fetch node to fetch data for these subreddits
    if sys.argv[1] is not None:
        data = json.loads(sys.argv[1])





