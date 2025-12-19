# BDO Coupon Bot

A simple Discord bot that searches for Black Desert coupons once in a while, and broadcasts them to subscribing channels.

## Usage

You can run the bot either with Docker for convenience or natively as well.

__NOTE: please use this tool responsibly, as the sites scanned provide these for free. This tool is provided as a personal convenience so you don't have to manually search for them. Not to hit these sites hundreds of times a day.__

### With Docker

1. Clone the repo
2. Create a new filed called "discord_token", and paste your discord token here
3. Run "docker compose up --detach"

### Without Docker

1. Install Firefox browser
2. [Install Poetry](https://python-poetry.org/docs/#installing-with-pipx)
3. Clone the repo in the destination of your choice
4. Create a new filed called "discord_token", and paste your discord token here
5. Start with launch.sh (this will also pull the latest changes)
