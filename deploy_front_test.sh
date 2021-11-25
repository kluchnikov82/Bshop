#!/bin/bash
cd /home/logshipping/bshop;
echo 'Обновление репозитория...'
git checkout front-01;
git pull;
echo 'Сборка server-side-rendering версии фронтенда...'
cd /home/logshipping/bshop/frontend/test-ssr;
node node_modules/.bin/ng build --prod;
echo 'Удаление файлов старой сборки...'
sudo rm /var/www/html/*.ico /var/www/html/*.js /var/www/html/*.map /var/www/html/*.html;
echo 'Копирование файлов...'
sudo cp -r dist/frontend/test-ssr/* /var/www/html;