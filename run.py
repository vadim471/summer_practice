from app import create_app
from app.update_ad import ApartmentUpdateService

app = create_app()
service = ApartmentUpdateService()


if __name__ == '__main__':
    app.run(host='192.168.88.10', debug = True)
    #service.run()