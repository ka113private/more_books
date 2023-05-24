import os

from .settings_common import *

#　本番環境用にセキュリティキーを生成し、環境変数から読み込む
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# デバッグモードを有効にするかどうか
DEBUG = False

#　許可するホスト名のリスト
ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOSTS')]

# 静的ファイルを配置する場所
STATIC_ROOT = '/usr/share/nginx/html/static'
MEDIA_ROOT = '/usr/share/nginx/html/media'

# AWS SES関連設定
AWS_SES_ACCESS_KEY_ID = os.environ.get('AWS_SES_ACCESS_KEY_ID')
AWS_SES_SECRET_ACCESS_KEY = os.environ.get('AWS_SES_SECRET_ACCESS_KEY')
EMAIL_BACKEND = 'django_ses.SESBackend'

# ロギング設定
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    #ロガーの設定
    'loggers': {
        #Djangoが利用するロガー
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        #booksアプリケーションが利用するロガー
        'books': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },

    #ハンドラの設定
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/django.log'),
            'formatter': 'prod',
            'when': 'D', #ログローテーション（新しいファイルへの切り替え）間隔の単位(D=日）
            'interval': 1, #ログローテーション間隔
            'backupCount': 7, #保存しておくログファイル数
        },
    },

    #フォーマッタの設定
    'formatters': {
        'prod':{
            'format': '\t'.join([
                '%(asctime)s',
                '[%(levelname)s]',
                '%(pathname)s(Line:%(lineno)d)',
                '%(message)s'
            ])
        }
    }
}
