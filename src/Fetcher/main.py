import pika
import requests
import json


'''
Fetches data from Reddit's .json API and applies two query parameters: sorting and timeframe. The sort is set to 
top and timeframe is set to day (today). 

subreddit: subreddit to fetch data for
nsfw_allowed: determined whether nsfw posts are considered
'''
def fetchData(subreddit: str, nsfw_allowed: bool = False) -> None:
    reddit_api = f"https://www.reddit.com/r/{subreddit}.json?sort=top?t=day"

    #  TODO: Issue could be here if reddit API bans this user agent. Fix is to simply change the version portion of the string.
    headers = {'User-agent': 'Youtube_Video_Automator/0.0.1'}

    response = requests.get(reddit_api, headers=headers)

    if response.status_code == 200:
        print(f"Success fetching data for {subreddit}")

        data = response.json()  # Deserialize data
        data = extract_data(data)

        if data['selftext'] == "":
            print(f"No text available. Skipping for {subreddit}")
            return

        sendData(data)

    else:
        print(f"Error fetching data. Response code is {response.status_code}")


'''
Saves the desired fields of the dictionary (denoted in desired_data) into a new dictionary.
nsfw_allowed will not process the post if it's set to false. post_count denotes how many posts we want to grab from
the api call.

Extracts data from the results of an API call for one particular subreddit at a time.

This is a recursive function that will skip over all mod stickied posts by recursively incrementing the post_count
and start parameters. Post count indicates the number of posts to grab and start indicates which post to start
processing from.
'''
def extract_data(datasrc: dict, post_count: int = 1, desired_data=None,
                 nswf_allowed: bool = False, start: int = 0) -> dict:
    if desired_data is None:
        desired_data = ['title', 'url', 'is_video', 'score', 'num_comments', 'view_count', 'ups', 'downs',
                        'selftext', 'over_18', 'author_fullname', 'stickied']

    data = {}

    for i in range(start, post_count):
        #  Skip all stickied posts
        if datasrc['data']['children'][i]['data']['stickied'] is True:
            return extract_data(datasrc, post_count=post_count + 1, desired_data=desired_data,
                                nswf_allowed=nswf_allowed, start=start + 1)

        for e in desired_data:
            if e == 'over_18' and datasrc['data']['children'][i]['data'][e] and not nswf_allowed:
                continue
            print(f"{e}: {datasrc['data']['children'][i]['data'][e]}")
            data[e] = datasrc['data']['children'][i]['data'][e]

    data['desired_data'] = desired_data

    return data


'''
Connects to a RabbitMQ channel and creates the binds to the imageWorker and audioWorker queues. Serializes data
and sends to those channels.
'''
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


'''
Decodes bytes into string and splits the string into an array using ',' as delimiter. See Scheduler node for
more info on the subreddit queue's data.
'''
def processSubreddits(ch, method, properties, body) -> None:
    subreddits = body.decode()
    subreddits = subreddits.split(',')

    for sub in subreddits:
        fetchData(sub)


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare('subreddits')

    channel.basic_consume(queue='subreddits', on_message_callback=processSubreddits, auto_ack=True)
    channel.start_consuming()  # Looping call to receive data from queue
