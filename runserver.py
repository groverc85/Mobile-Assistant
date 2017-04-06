#-*- coding:utf-8 -*-

from moblife import app

if __name__ == '__main__':
    import webbrowser
    webbrowser.open('http://localhost:5000')
    app.run()

else:

    from bae.core.wsgi import WSGIApplication
    application = WSGIApplication(app)

    
