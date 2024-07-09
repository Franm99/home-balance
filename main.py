from app import create
import settings

if __name__ == '__main__':
    app = create(settings.DEV_MODE)
    
    app.run(debug=settings.DEV_MODE)
