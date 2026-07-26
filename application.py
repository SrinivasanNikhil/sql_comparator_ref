from app import create_app

application = create_app()

if __name__ == "__main__":
    context = ('app/ssl/certificate.crt', 'app/ssl/private.key')
    application.run(host='0.0.0.0', debug = True, ssl_context = context, port=5000)
