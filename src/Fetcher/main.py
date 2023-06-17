import pika
import requests



def fetchData(subreddit: str, nsfw_allowed: bool = False) -> None:
    reddit_api = f"https://www.reddit.com/r/{subreddit}.json?sort=top?t=day"

    #  Issue could be here if reddit bans this user agent. Fix is to simply change the version portion of the string.
    headers = {'User-agent': 'Youtube_Video_Automator/0.0.1'}

    response = requests.get(reddit_api, headers=headers)

    if response.status_code == 200:
        print(f"Success fetching data for {subreddit}")
        # sendData(response.json()) TODO: properly extract data before you send it
    else:
        print(f"Error fetching data. Response code is {response.status_code}")


def extract_data(datasrc, post_count = 1, desired_data=None):
    if desired_data is None:
        desired_data = ['title', 'url', 'is_video', 'score', 'num_comments', 'view_count', 'ups', 'downs', 'selftext']
    for i in range(0, post_count):
        for e in desired_data:
            print(f"{e}: {datasrc['data']['children'][i]['data'][e]}")


def sendData(data: dict) -> None:
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="imageWorker")
    channel.queue_declare(queue="audioWorker")

    #  Might need to serialize dict data prior to sending to queues
    channel.basic_publish(exchange='', routing_key='imageWorker', body=data)
    channel.basic_publish(exchange='', routing_key='audioWorker', body=data)
    #  Close conn.
    connection.close()



if __name__ == '__main__':
