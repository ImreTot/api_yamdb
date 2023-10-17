# API YaMDB
## _Post, read, comment. Or all at once_
This is the API version of YaMDB - social network where users can publish their diaries and notes, subscribe to other users, and comment on their articles. If you need version based on Django templates please check this [link][YaMDB-templates].

Powered by
[![N|Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![N|DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)](https://www.django-rest-framework.org/)
[![N|SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html)

## Installing
### For linux system or WSL
Get source
```sh
git clone git@github.com:ImreTot/api_final_yatube.git
```
Make virtual environment
```sh
python3 -m venv venv
source venv/bin/activate
```
Install pip and dependencies
```sh
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Migrations
```sh
python manage.py makemigrations
python manage.py migrate
```

## License

MIT
**Free Software, Hell Yeah!**

[YaMDB-templates]: <https://github.com/ImreTot/YaMDB-templates>
