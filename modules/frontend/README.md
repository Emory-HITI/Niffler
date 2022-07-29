# A Frontend Framework for Niffler

```diff
- This is an experimental module. You are advised against using it.
- Please use the relevant modules (cold-extraction, meta-extraction, and png-extraction) directly from their backend.

```

This is a frontend module for Niffler which consists 2 modules:
a. On-Demand Extracion or Cold-Extraction (cold-extraction)
b. PNG-Extraction (png-extraction)
This module is using **Flask** as a backend engine to run all the frontend.

## Install Requirements

```
$ pip3 install -r requirements.txt
```

## Steps for running Frontend Module

1. Run server.py file by navigating into frontend directory and running:

    ```
    python server.py
    ```

    or

    ```
    python3 server.py
    ```

    (user level access)

2. Then navigate to `<SERVER-IP-ADDRESS>:5000` to view your Niffler Frontend.

## Admin level access

1. Run server.py file by navigating into frontend directory and running:

    ```
    python server.py --admin
    ```

    or

    ```
    python3 server.py --admin
    ```

    (admin level access)

2. The admin access enables only admins to create new users.

**NOTE: `__init__.py` file is important as it serves the frontend directory as a package, so the values can be accessed from other modules also**
