from app import create_app
from app import update_ad

app = create_app()
update_ad.check_and_update_announcements()


if __name__ == '__main__':
    app.run(host='192.168.88.10', debug = True)