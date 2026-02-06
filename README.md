# INSTALL & SETUP INSTRUCTIONS

    to clone project open terminal & write: git clone https://gitlab.com/,
    then: cd ,
    if you have got other branch than master, write: git checkout your_branch

#### 1. Create a virtual environment to isolate our package dependencies locally

    pip install virtualenv
    python -m venv env

    source env/bin/activate for Linux/MacOS
    env\Scripts\activate for Windows

#### 3. Install requirements

    pip install -r requirements.txt

#### 4. Migrate

    python manage.py makemigrations
    python manage.py migrate

#### 5. Create superuser

    python manage.py createsuperuser

#### 6. Run server
    env\Scripts\activate

    celery -A main beat --loglevel=info 
    celery -A main worker --loglevel=info --pool=solo 

    python manage.py runserver

#### 7. Enjoy

    http://localhost:8000/api/v1/
    http://localhost:8000/admin/
