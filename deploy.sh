#!/usr/bin/bash

# サービスを停止
sudo systemctl stop nginx.service
sudo systemctl stop gunicorn.service

# 最新資産をgitから持ってくる
git pull origin main

# 仮想環境に入る
source ../bin/activate

# CSSを適用する
python manage.py collectstatic
yes

# モデルのマイグレーションを行う
# python manage.py migrate

#　仮想環境から出る
deactivate

# サービスを再開する
sudo systemctl start nginx.service
sudo systemctl start gunicorn.service