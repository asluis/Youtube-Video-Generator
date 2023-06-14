from crontab import CronTab
import yaml
import sys
import pika

'''
Reading through the config.yaml file for a schedule and a list of subreddits that will be processed
following that schedule.
'''
def loadConfig() -> dict:
    config = None
    try:
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)

    except OSError:
        print("config.yaml does not exist. Please make sure it is named correctly.")
        exit(1)

    return config


'''
For each schedule this will create a cronjob that will call main.py (this file) and pass to it
the subreddits found in the yaml config as parameters.
'''
def addCronJob(schedule: dict) -> None:
    #  TODO: Consider changing user to something else so it does not require sudo access
    cron = CronTab(user='luis')  # Assumes Linux OS

    subreddits = str.join(',', schedule['subreddits'])
    #  Create cron job and pass the subreddits as an argument
    job = cron.new(command=f"python3 {__file__} {subreddits}")

    minute = schedule['minute']
    hour = schedule['hour']
    day = schedule['day']
    month = schedule['month']
    day_of_week = schedule['day_of_week']

    job.setall(f"{minute} {hour} {day} {month} {day_of_week}")
    cron.write()


'''
Iterates through the list of schedules extracted from loadConfig and adds each schedule as a cron job
'''
def processSchedules() -> None:
    schedules = loadConfig()['schedule']

    for schedule in schedules:
        addCronJob(schedule)


if __name__ == "__main__":
    #  Make a call to fetch node to fetch data for these subreddits
    if len(sys.argv) == 2:
        #  This is the argument execution of main.py, which will be what the cronjob executes
        data = sys.argv[1]

        # Establishing connection to rabbitmq
        connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        channel = connection.channel()
        #  Declaring a q
        channel.queue_declare(queue="subreddits")
        #  Publishing a message to q
        channel.basic_publish(exchange='', routing_key='subreddits', body=data)
        #  Close conn.
        connection.close()
    else:
        #  This is the standard execution of main.py, which is what the user must execute initially
        processSchedules()
