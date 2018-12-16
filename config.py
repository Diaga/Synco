import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('CRYPT') or 'cats-are-overlords'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True


class Extensions:
    document_list = [".txt", ".py"]
    audio_list = ['.mp3', '.ogg', '.wav']
    video_list = ['.mp4', '.ogg', '.webm']
    image_list = ['.jpeg', '.jpg', '.png', '.gif']
