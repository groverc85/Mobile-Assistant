git pull origin unicom
killall -9 uwsgi
uwsgi --ini uwsgi.ini
