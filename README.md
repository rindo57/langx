# Language-exchange-app

This is a location-based web application that allows users to connect with other nearby users with the sole purpose
of learning and practicing new languages. The app is available on heroku at https://nsm-flask-app.herokuapp.com/

<img width="400" height="200" alt="app_bg" src="https://user-images.githubusercontent.com/83452606/164338617-fecb7fc0-cd12-4f92-b472-b054e9856b0f.png">

## Initializing the project

#### The below instructions are suitable for Windows OS

---

Create a new directory for the app

```git
mkdir app-name
cd app-name
```

Create a python virtual environment

```python
python3 -m venv venv
.\venv\Scripts\activate
```

---

## Install packages with pip3

Check for all dependencies in the requirements.txt file. This file tracks all the dependencies and makes it easier to install required packages

All dependencies were installed with the below command:

```python
pip3 install "dependency-name"
```

The following command will install the packages according to the configuration file requirements.txt

```python
pip install -r requirements.txt
```

**pip freeze** outputs the package and its version installed in the current environment in the form of a configuration file that can be used with pip install -r

If later on you install more libraries on your local virtual env, remember to generate the requirements.txt file again and push that change so the next time you deploy to Heroku it gets installed there as well.

```
$ pip freeze
atomicwrites==1.4.0
attrs==21.4.0
bcrypt==3.2.0
certifi==2021.10.8
cffi==1.15.0
charset-normalizer==2.0.12
click==8.0.4
colorama==0.4.4
dnspython==2.2.1
email-validator==1.1.3
Flask==2.0.3
Flask-Bcrypt==0.7.1
Flask-Cors==3.0.10
Flask-Login==0.5.0
Flask-SQLAlchemy==2.5.1
Flask-WTF==1.0.0
GeoAlchemy2==0.10.2
greenlet==1.1.2
gunicorn==20.1.0
idna==3.3
iniconfig==1.1.1
itsdangerous==2.1.0
Jinja2==3.0.3
jyserver==0.0.5
MarkupSafe==2.1.0
packaging==21.3
Pillow==9.0.1
pluggy==1.0.0
psycopg2==2.9.3
py==1.11.0
pycparser==2.21
pyparsing==3.0.7
pytest==7.1.1
requests==2.27.1
Shapely==1.8.1.post1
six==1.16.0
SQLAlchemy==1.4.31
toml==0.10.2
urllib3==1.26.9
Werkzeug==2.0.3
WTForms==3.0.1
```

---

## Heroku CLI setup and creating Heroku app with Postgres DB

Set up a free Heroku account at [Heroku Sign up]("https://signup.heroku.com/")

The Heroku command-line interface (CLI) is a tool that allows you to create and manage Heroku applications from the terminal. It’s the quickest and the most convenient way to deploy your application. You can check the developer’s documentation for installation instructions for your operating system. On window distributions, you can install the Heroku CLI by running the following commands on the following at [Heroku CLI set up]("https://devcenter.heroku.com/articles/heroku-cli#install-the-heroku-cli")

### Verify the installation

```
heroku --version
```

Then log into heroku:

```
heroku login
```

This opens a website with a button to complete the login process. Click Log In to complete the authentication process and start using the Heroku CLI

Now create a new app with a unique name inside your Heroku account:

```
heroku create flask-app-name
```

If the above command works you will see the below output

```
Creating ⬢ flask-app-name... done
https://flask-app-name.herokuapp.com/ | https://git.heroku.com/flask-app-name.git
```

Now add a PostGres database to your app

```
sudo heroku addons:create heroku-postgresql:hobby-dev
```

You will see an output similar to below

```
Creating heroku-postgresql:hobby-dev on ⬢ flask-app-name... free
Database has been created and is available
 ! This database is empty. If upgrading, you can transfer
 ! data from another database with pg:copy
Created postgresql-parallel-63698 as DATABASE_URL
Use heroku addons:docs heroku-postgresql to view documentation
```

As the last step in setting up the database, we install PostGis, this is the xtendion library to deal with geolocated data. To be able to do this we need our database name,

In my example that is 'postgresql-parallel-63698' (notice that is mentioned on the output when we created the db, otherwise you can see the db name from the Heroku web console)

```
sudo heroku pg:psql postgresql-parallel-63698
```

This will open a command line for you to run commands on your database. Run the following:

```
CREATE EXTENSION postgis;
```

You should see the following output if the installation went well:

```
CREATE EXTENSION
```

Use 'exit' to get out of the db command line.

---

## Running the app locally

Set up two environment variables

1. DATABASE_URL: this is the connection string for the PostGres database. Because the DB is hosted by Heroku, it also defines the user / password / etc for us. These are 'ephemeral' credentials that heroku will rotate periodically to make your db more secure. We don't know how often the credentials change, but we should assume they will, so no hardcoding these anywhere. To get the proper value you can use the heroku cli, and below you get a bit of command line magic to directly put that into a local env variable
2. GOOGLE_MAPS_API_KEY: You need to get this for yourself. It will be sent to the Google Maps API to render the map on the initial page of the sample app

So, before running the app locally, always set up the above environment variables

Windows command for exporting the DATABASE_URL above is using some additional utility (sed) to get the value directly from the output from the heroku client query. This is useful, but maybe you do not have sed, or you are running these commands on Windows.

In that case you can do a little bit more manual work to get the same result:

First call Heroku to get the db URL:

```
sudo heroku pg:credentials:url postgresql-parallel-63698
```

OR

```
sudo heroku pg:credentials:url postgresql-parallel-63698 -a flask-app-name
```

**'postgresql-parallel-63698' with the name of your own database**

If Heroku complains about

`Error: Missing required flag: -a, --app APP app to run command against`

then add the flag -a` like above but using your own app name.

This will output something like this:

```
$ sudo heroku pg:credentials:url postgresql-parallel-63698
Connection information for default credential.
Connection info string:
   "dbname=xxxxxxxxxxxxxx host=ec2-XXX-XXX-XXX-XXX.compute-X.amazonaws.com port=XXXX user=XXXXXXX password=XXXXXXXXXXXXXX sslmode=XXXXXX"
Connection URL:
   postgres://XXXXXXX:YYYYYYYYYYYYYYYYYYYYYYY@ec2-XXX-XXX-XXX-XXX.compute-X.amazonaws.com:XXXX/XXXXXXXXXXXXXXX
```

What we want to set as DATABASE_URL is the value shown as Connection URL, that starts with 'postgres://' You can copy that value from the output and use it to set the variable.

In Windows, that would look like this:

```
SET DATABASE_URL=postgres://XXXXXXX:YYYYYYYYYYYYYYYYYYYYYYY@ec2-XXX-XXX-XXX-XXX.compute-X.amazonaws.com:XXXX/XXXXXXXXXXXXXXX

SET GOOGLE_MAPS_API_KEY=ssdfsdfsAAqfdfsuincswdfgcxhmmjzdfgsevfh

SET FLASK_ENV=development
```

**The third command above ensures that during development the app reloads automatically whenever modifcations are made**

The above Google Map API key is a dummy value. Note the above commands as you have to rerun them everytime you are working on your app locally on a new instance of command line.

Verify the environment variables on windows:

```
echo %DATABASE_URL%
echo %GOOGLE_MAPS_API_KEY%
```

Finally run the app:

```
flask run
```

The output will be something as below:

```
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

Use Ctrl+C to quit / shut down the flask app

## Deploy app to Heroku

---

Create a file named Procfile in the project's root directory.This file ells Heroku how to run the app. You can create it by running the following command:

```
echo "web: gunicorn app:app" > Procfile
```

Commit the file to the remote Github repo:

```
git add Procfile
git commit -m "Procfile for heroku"
git push
```

Before deploying remember that we need 2 environment variables for the sample code to work. DATABASE_URL is by default provided by Heroku because we have a DB attached to our app. The second env variable is something we define, so we need to set it manually as a Heroku config variable:

```
sudo heroku config:set GOOGLE_MAPS_API_KEY=ssdfsdfsAAqfdfsuincswdfgcxhmmjzdfgsevfh
```

Now all is ready. To deploy that current state into your Heroku app, run:

```
sudo git push heroku main
```

This will output a lot of things as heroku installs all components. If all is ok with the app ou will see the URL of your launched app:

```
remote: -----> Launching...
remote:        Released v5
remote:        https://flask-app-name-delete.herokuapp.com/ deployed to Heroku
remote:
remote: Verifying deploy... done.
```

For any commits pushed to Github do not forget to deploy the same changes in heroku

```
sudo heroku login
sudo git push heroku main
```

---

## .idea Folder

Project settings are stored with each specific project as a set of xml files under the this folder.

If you specify the default project settings, these settings will be automatically used for each newly created project.

---

## Issues I faced during development - specific to Windows OS

The app wasn't 'running' in heroku due to numerous errors. After sourcing online and reading through plenty of documentation online I concluded that:

- I had to create a runtime.txt folder on the root directory and include the accepted python version as allowed in Heroku:

```
> touch runtime.txt
> python-3.9.11
```

- One needs additional dependencies on windows as opposed to the main ones below:

```
pip3 install Flask
pip3 install gunicorn
pip3 install psycopg2
pip3 install Flask-SQLAlchemy
pip3 install Geoalchemy2
pip3 install shapely
pip3 install flask_cors
pip3 install flask_wtf
```
