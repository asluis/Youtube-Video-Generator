# Disclaimer
This repo is being made public since I no longer plan on actively working on this. This was made from scratch while I was in university.

### What is this?

This is a very convoluted video generator that I created to learn about message queues and rabbitMQ. Essentially, it does as follows:

1) Grabs reddit post based on a recurring schedule you'd like to generate videos
2) Passes reddit post content through a text to speech model to generate audio
3) Passess reddit post content to text to image model to generate visuals.
4) Uses a video editing library to create a video based on step 2 and 3 above
5) Saves video to a local database

Sample video generated with this can be seen (here)[https://www.youtube.com/shorts/bPet9PRHRqE]

