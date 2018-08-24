import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from flask_session import Session
from app import create_app, db
from app.models import Field

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.cli.command()
def deploy():
    """Creating the database"""
    print('Deploying...')
    db.create_all()
    sess = Session(app)
    sess.app.session_interface.db.create_all()
    fields = [
        Field(size=6, fox_count=4, name='Small'),
        Field(size=10, fox_count=8, name='Classic'),
        Field(size=12, fox_count=10, name='Large'),
    ]
    for field in fields:
        db.session.add(field)
    db.session.commit()


if __name__ == '__main__':
    app.run()
