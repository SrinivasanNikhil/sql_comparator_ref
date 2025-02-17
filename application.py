from app import create_app

application = create_app()

if __name__ == "__main__":
    context = ('/app/ssl/certificate.crt', '/app/ssl/private.key')
    application.run(host='0.0.0.0', port=443, debug = True, ssl_context = context)
