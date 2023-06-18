import pika
import requests
import json


'''
Fetches data from Reddit's .json API and applies two query parameters: sorting and timeframe. The sort is set to 
top and timeframe is set to day (today). 

param - subreddit: subreddit to fetch data for
param - nsfw_allowed: determined whether nsfw posts are considered
'''
def fetchData(subreddit: str, nsfw_allowed: bool = False) -> None:
    reddit_api = f"https://www.reddit.com/r/{subreddit}.json?sort=top?t=day"

    #  TODO: Issue could be here if reddit API bans this user agent. Fix is to simply change the version portion of the string.
    headers = {'User-agent': 'Youtube_Video_Automator/0.0.1'}

    response = requests.get(reddit_api, headers=headers)

    if response.status_code == 200:
        print(f"Success fetching data for {subreddit}")

        data = json.loads(response.json())  # Deserialize data
        data = extract_data(data)
        sendData(data)

    else:
        print(f"Error fetching data. Response code is {response.status_code}")


def extract_data(datasrc, post_count = 1, desired_data=None, nswf_allowed: bool = False) -> dict:
    if desired_data is None:
        desired_data = ['title', 'url', 'is_video', 'score', 'num_comments', 'view_count', 'ups', 'downs',
                        'selftext', 'over_18', 'author_fullname']

    data = {}

    for i in range(0, post_count):
        for e in desired_data:
            if e == 'over_18' and not nswf_allowed:
                continue
            print(f"{e}: {datasrc['data']['children'][i]['data'][e]}")
            data[e] = datasrc['data']['children'][i]['data'][e]

    return data


def sendData(data: dict) -> None:
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()

    channel.queue_declare(queue="imageWorker")
    channel.queue_declare(queue="audioWorker")

    #  Serializing data into json format and sending thru q
    channel.basic_publish(exchange='', routing_key='imageWorker', body=json.dumps(data))
    channel.basic_publish(exchange='', routing_key='audioWorker', body=json.dumps(data))
    #  Close conn.
    connection.close()


if __name__ == '__main__':
