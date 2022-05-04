from server import app


app.run(port=5000,
        threaded=True,
        processes=1)
