# BT4222
Saikang mod 102

## Setup Instructions (optional - as long as you get it to work and you know what youre doing its fine)

1. Install `anaconda` URL: https://docs.continuum.io/anaconda/install/
2. Set up `conda` environment with `conda create env --new bt4222 python pip`
3. `activate bt4222` (windows) /  `source activate bt4222` (mac / linux)
4. `pip install -r requirements.txt`

You now need to settle environment variables, and the database 

1. install postgres
2. Follow the instructions here https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04 to install postgres and stuff, then run the following commands (instead of what they say in the URL)


  `CREATE DATABASE bt4222db;`
  
  `CREATE USER djangouser WITH PASSWORD 'password';`
  
  `ALTER ROLE djangouser SET client_encoding TO 'utf8';`
  
  `ALTER ROLE djangouser SET default_transaction_isolation TO 'read committed';`
  
  `ALTER ROLE djangouser SET timezone TO 'UTC';`
  
  `GRANT ALL PRIVILEGES ON DATABASE bt4222db TO djangouser;`
  
  `ALTER USER djangouser CREATEDB;`

3. Set up environment variables for conda (unfortunately not auto) follow instructions at https://conda.io/docs/user-guide/tasks/manage-environments.html#win-save-env-variables and set the only environment variable to `export DATABASE_URL='postgres://djangouser:password@localhost/bt4222db`

Install Heroku toolchain cli
1. `https://devcenter.heroku.com/articles/heroku-cli`

## Test installation

1. Navigate to the `bt4222` folder
2. Run `python manage.py makemigrations`
3. Run `python manage.py migrate`
4. Run `python manage.py runserver`
5. Go to the URL that it prints out