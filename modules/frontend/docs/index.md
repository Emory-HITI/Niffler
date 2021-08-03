# Developer Cookbook

---

## Introduction

This particular module deals with the frontend of Niffler. It has two modules:

1. On - Deamand Extraction
2. PNG - Extraction

This module makes use of Flask and web-sockets to run asynchronous tasks.
It has it's very own authentication system.

## Modules

### 1. Basics

We have a **_server.py_** file which handles all the main logic of the Niffler-Frontend and also this is the file we will run to access the frontend.

To run the Niffler frontend module make sure you have all the python modules installed in your project environment. You can do this by following steps:

-   Clone the repo

```
$ git clone https://github.com/Emory-HITI/Niffler.git
```

-   Now navigate to frontend module, open terminal and type this command to install all the required modules.
    **Make sure you are using virtual environment for development purpose**

```
$ pip3 install -r requirements.txt
```

and all the required packages would be installed.

### 2. Running the frontend module

After install the required modules, make sure you are in the frontend module and open terminal in this module and make sure you are in your developer environment and type

```
$ python3 server.py
```

This will make the server run on port **5000**.

There is also **ADMIN** mode for frontend module. To run frontend in **ADMIN** mode, follow above step but type

```
$ python3 server.py --admin
```

and the server will be switched to **ADMIN MODE.**

-   **Niffler Admin Mode:** Only admin has the ability to signup other users
    ![NIFFLER ADMIN MODE](/modules/frontend/static/images/Niffler_admin.png)

-   **Niffler User Mode:** Normal users can LOGIN and use Niffler
    ![NIFFLER USER MODE](/modules/frontend/static/images/Niffler_normal.png)

### 3. Project Structure

In this particular module we have the following files/folders:

-   **_server.py:_** This is the main file of Niffler-Frontend module. It has all the logic and working of the module.

-   **_init.py:_** This file has all the basic importing of function such as importing database, sockets so it can be used in other files.

-   **_models.py:_** Models have a user model which is defined for _db.sqlite3_ (This is our database).

-   **_db.sqlite3:_** We are using sqlite3 database as it is light-weight and this only stores users login credentials. So, for now, we are just storing users in this database.

-   **_templates:_** This folder stores all the HTML templates which are used in this module. We have one _base.html_ templatewhich we are extending for all other templates.

-   **_static:_** This folder contains the CSS and images used in the website.
