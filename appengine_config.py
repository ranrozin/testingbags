from gaesessions import SessionMiddleware
def webapp_add_wsgi_middleware(app):
     app = SessionMiddleware(app, cookie_key="ajdk378nve'kasmfgivnje875894AHSH_dsjknsdkjns", no_datastore=True)
     return app