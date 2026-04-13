# Sketchy-Connections
Built for: CS3050 Final Project

James LeMahieu, Joe Liotta, Mathew Neves, Kent Schneider

Welcome to Sketchy Connections!
In this game, hop online with your friends and combine miscommunication with your lovely drawing skills! Inspired by the popular games 'Telestrations'
and 'Gartic Phone', Sketchy Connections is a round-based party game consisting of drawing prompts and guessing others.

## Gameplay:

-Create a name and join or host a room with your friends

-Start a round, beginning with choosing a prompt you want to draw

-Draw your prompt, and then pass it

-Guess what image you received, and pass it again

-Draw the new prompt

-Repeat

At the end of the game, reflect upon the sketchy connections you and your friends made, sharing a laugh along the way.

## Design:

Organized in Engine.py and backend-supported by model.py

## Installation:

On Windows, you can install and run the application by using:
```batch
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .\shared
pip install -e .\client
python -m sketchy_client.main
```

On macOS, you can install and run the application by using:
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -e ./shared
pip install -e ./client
python -m sketchy_client.main
```

## Client Development:

With uv, client can be run using:
```sh
uv run --package sketchy-client sketchy-client
```

On Windows, you can run the client from the repo root without installing the packages by using:
```bat
run_client.bat
```

On macOS, you can run the client from the repo root without installing the packages by using:
```sh
bash run_client.sh
```

## Server Installation:

For convenience, the server can be packaged as a docker container and run using:
```sh
docker build -f server/Dockerfile -t sketchy-server .
docker run --rm -p 8000:8000 sketchy-server
```

## Known Bugs:

On some occasions, the server can freeze after submission, preventing the game from stepping forward to the next phase
