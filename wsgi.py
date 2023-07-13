from app import init_app

application = init_app()

if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)
	