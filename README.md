###### 
<p align="center">
<img width="420px" src="https://i.ibb.co/vQBTZSj/Logo-small.png" alt="GAME DEALS">
</p>

# BACKEND DOCUMENTATION

Game deals is an application that collects the best game offers on Steam, GOG and Humble Store in one place.<br>
Registered users can browse, filter and sort deals.

The application is written with Django (Backend) and React.js (Frontend).<br>
This documentation explains all necessary steps to run and test the backend application.

Game Deals frontend is located at the following URL:<br>
> https://github.com/ghiandFe/game_deals_frontend

## REQUIREMENTS

- Python v3.9.6 (and venv) installed on your system
- Git installed on your system

## CLONING REPOSITORY

Open command line and run:
```sh
$ git clone https://github.com/ghiandFe/game_deals_backend.git
```
When the command is executed, open the folder created (game_deals_backend) and check for the manage.py file:
```sh
$ cd game_deals_backend

# Linux
$ ls

# Windows
> dir
```
If check successfully, go to the next step.

## SYSTEM CONFIGURATION

From now on, all commands must be launched from within the repo folder (game_deals_backend)

### Creating virtual environment

Creation of virtual environment is done by executing the command "venv":

```sh
$ python -m venv gamedeals_venv
```

If you have more than one version of Python installed on your system you may need one of the following:

```sh
$ python3 -m venv gamedeals_venv
$ python3.9 -m venv gamedeals_venv
```

Now, we should activate the virtual environment:

```sh
# linux
$ source gamedeals_venv/bin/activate

# windows
> gamedeals_venv\Scripts\activate
```

The result should look like this:

```sh
(gamedeals_venv) $
```

### Installing dependencies

Dependencies are necessary for the app to work properly.<br>
The list is on the requirements.txt, so we can install all with only a command:

```sh
(gamedeals_venv) $ pip install -r requirements.txt
```

## DJANGO SETTINGS

### Create DB

Now we need to create the tables in the database.<br>
To do that, run the following commands:

```sh
(gamedeals_venv) $ python manage.py makemigrations
(gamedeals_venv) $ python manage.py migrate
```

### Populate DB

To populate the created tables run these custom commands:

```sh
(gamedeals_venv) $ python manage.py fetch_stores
(gamedeals_venv) $ python manage.py fetch_deals
```

### Create a superuser

Run the command:

```sh
(gamedeals_venv) $ python manage.py createsuperuser
```

## TESTING THE APPLICATION

To run the test, use the command:

```sh
(gamedeals_venv) $ python manage.py test
```
> The testing phase could take several minutes due to the rate limiting set to call the API

## START THE DJANGO SERVER

The last step: run the server!

```sh
(gamedeals_venv) $ python manage.py runserver
```