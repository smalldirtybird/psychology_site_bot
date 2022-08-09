# Psy-help info bot

## How it works:
The bot talks about the course of psychological assistance, available at [Anatomy of emotions site](https://kochet-psy.ru/anatomy_of_emotions).

## How to prepare:
1. Install Python 3.9.13. You can get it from [official website](https://www.python.org/).

2. Install libraries with pip:
```
pip3 install -r requirements.txt
```

3. Create a Telegram bot which will help user to choose and by your products - just send message `/newbot` to [@BotFather](https://telegram.me/BotFather) and follow instructions.
After bot will be created, get token from @BotFather and add to .env file:
```
TELEGRAM_BOT_TOKEN ='your_telegram_bot_token'
```
Put your token instead of value in quotes.

4. Create database on [Redislabs](https://redis.com/). 

5. Add the following lines to .env file:
```
DB_HOST = 'your_database_address'
DB_PORT = 'database_port'
DB_PASSWORD = 'database+password'
```

6. Specify the path to the `/images` and `/text_data` folders as variables in the `.env` file. These folders should contain the files necessary for the bot to work:

```
IMAGE_FOLDER_PATH = 'image_folder_path'
COURSE_CONTENT_PATH = 'text_data_folder_path'
```

7. Put into `/text_data` folder following files:
`lessons.json` - information about lessons structured by example:
`{
        "lesson_<lesson number>": {
			"header": "<lesson name>",
			"content": "<lesson description>",
...
}`;

`mentors_json` - bio of course mentors structured by example:

`{
        "mentor_<number>": {
			"name": "<mentor's name>",
			"description": "<mentors info>"
...
}`;

`main_header.txt` - text in the main menu; 

`mentors_header.txt` - general information about course mentors;

`program_general_info.txt` - general information about course conception;

`symptoms.txt` - information for user self-diagnosis.

## How to run:
Bot can be launched from the terminal with the commands: `$ python3 main.py`