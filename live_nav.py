from flask import Flask, render_template
import crawler


app = Flask(__name__)


@app.route('/livenav')
def live_nav():
    live_urls = crawler.live_urls()

    return render_template('live_nav.html',
                           live_urls=[live for live in live_urls if live.is_live],
                           notlive_urls=[live for live in live_urls if not live.is_live])


if __name__ == '__main__':
    app.run(debug=True)