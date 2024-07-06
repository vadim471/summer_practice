from app import create_app
from app import UpdateService


app = create_app()
updateService = UpdateService

#updateService.UpdateService.check_and_update_announcements()
if __name__ == '__main__': 
    app.run(debug = True)
    #service.run()
    #host='192.168.88.10'