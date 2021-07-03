# A Frontend Framework for Niffler

Here we have created a frontend module for Niffler for ease of acccess of it's modules.
This module is using **Flask** as an engine to run all the frontend.

**Make sure you have installed Flask from requirements.txt file.**

## Steps for running Frontend Module

1. Run server.py file by navigating into frontend directory and running:
`python server.py` or `python3 server.py` (user level access)

2. Then navigate to `localhost:9000` to view your Niffler modules.

## Admin level access

1. Run server.py file by navigating into frontend directory and running:
`python server.py --admin` or `python3 server.py --admin` (admin level access)

2. The admin access enables only admins to create new users.



*Currently PNG extraction Frontend is developed and it can take values from frontend and can be passed into backend*

**NOTE: `__init__.py` file is important as it serves the frontend directory as a package, so the values can be accessed from other modules also**
