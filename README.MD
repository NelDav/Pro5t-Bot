# PRO5T - BOT

This is the discord bot, that is running on the PRO5T Discord server.
Feel free to reuse it on your own server.

## Installation

1. Clone the repository. You can clone it on your local system. Note, that the discord bot will only run if the system where you cloned the repository, also runs.
That's why we recommend to clone it so a server of yours.

2. First you have to install some dependencies. We strongly recommend to do that with a virtual environment.
But before doing that, install python3 and pip.
Now install virtualenv: `python3 -m pip install virtualenv`.

3. Navigate into the cloned repository and create the virtual environment: `python3 -m virtualenv .venv`.
After doing so, activate it:
    * Linux: `source .venv/bin/activate`
    * Windows: `.venv/Scribts/activate.bat`

4. Now you can install all dependencies with pip:
`pip install -r requirements.txt`

5. Before you start the bot, you need to connect the bot with your discord account.
Therefore, visit the developer page of discord: https://discord.com/developers/
Here, you want to crate a new application. Give a name of your choice.

6. Now navigate on to "Bot". On this page, you have to turn on the "Presence Intent" and "Server Members Intent" switch.

7. Next step is to copy the token. Somewhere at the top of the page, click on "Reset Token". You will be asked to enter your discord password. After entering you password, a new token will be displayed. You can just click on the copy button. Note, that you cannot retrieve the token again. If you forget it, you have to reset it again.

8. The PRO5T bot will check for a environment variable named "TOKEN" to retrieve you token. That means, that you have to generate a new environment variable and put your token there. On Linux, you want to add this line to the `/etc/environment` file: `TOKEN:<your-token>`.
On windows, search for "environment variables". A window will open. Click on the button "Environment variables..." and add it there.

9. Now you are ready to start the bot.
Just start it via `python3 bot.py`.
Note that the your virtual environment but be activate before doing so.
