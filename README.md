# HiShop Web

1. Create Virtual env : virtualenv -p python3.8 <env_name>
2. change dir to virtualenv : cd env_name
3. creae "cdn/static" and "cdn/media" in virtual env.
4. active virtual env. : source bin/activate
5. change dir to src : cd src
6. migrate database : python manage.py migrate
7. for staticfile : python manage.py collectstatic
8. create superuser : python manage.py createsuperuser
9. runserver : python manage.py runserver


# For running api on mobile application

9. runserver : python manage.py runserver 0.0.0.0:8000

  then check your computer ip:8000

  to get your computer ip : open terminal and type $ ifconfig
