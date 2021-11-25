#!/bin/bash
cd /home/logshipping/bshop;
echo 'Обновление репозитория...'
git fetch --all;
git stash;
git checkout master;
git pull;
echo 'Рестарт сервисов supervisor...'
sudo supervisorctl restart uwsgi;
sudo supervisorctl restart celery;
sudo supervisorctl restart celery_beat;
echo 'Сборка фронтенда...'
cd /home/logshipping/bshop/frontend/ssr;
npm run build:ssr;