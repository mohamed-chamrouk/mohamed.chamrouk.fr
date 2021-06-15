from mohamed_chamrouk_fr import app
import uwsgi

application = app

if __name__ == "__main__":
    uwsgi.cache_clear()
    application.run()
