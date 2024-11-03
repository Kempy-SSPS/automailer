from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from automailer import main as automail

app = Flask(__name__)


@app.route('/automail', methods=['POST'])
def run_endpoint():
    automail()
    return "Endpoint hit, automailing", 200


scheduler = BackgroundScheduler()
scheduler.add_job(automail, 'cron', hour=12, minute=0)
scheduler.start()


if __name__ == '__main__':
    app.run(port=5000)
