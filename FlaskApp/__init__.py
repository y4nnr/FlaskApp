from flask import Flask, render_template, request
import flask_resize
import redis
import time

w = redis.Redis(host='cluster.blog.redis.live', port=6379, db=0, charset="utf-8", decode_responses=True)
r = redis.Redis(host='oregon-ro.wraqgj.ng.0001.usw2.cache.amazonaws.com', port=6379, db=0, charset="utf-8", decode_responses=True)


def get_hit_count():
    retries = 5
    while True:
        try:
            return w.incr("foo")
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

def show_top10_phones():
    retries = 5
    while True:
        try:
            phones_table = r.zrevrange("top10:phones", 0, -1, withscores=True)
            return phones_table
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

def show_top10_tablets():
    retries = 5
    while True:
        try:
            tablets_table = r.zrevrange("top10:tablets", 0, -1, withscores=True)
            return tablets_table
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

def show_top10_all():
    retries = 5
    while True:
        try:
            w.zunionstore('top10:all', ['top10:phones', 'top10:tablets'])
            all_table = r.zrevrange("top10:all", 0, 9, withscores=True)
            return all_table
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)



app = Flask(__name__)
@app.route("/")
@app.route("/index")
def index():
    count = get_hit_count()
    top10_tablets = show_top10_tablets()
    top10_phones = show_top10_phones()
    top10_all = show_top10_all()
    return render_template("index.html", title="Y4N", count=count,top10_tablets=top10_tablets, top10_phones =top10_phones, top10_all=top10_all, len_phones = len(top10_phones), len_tablets = len(top10_tablets), len_all = len(top10_all), )

@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response


@app.route("/input")
def input():
    return render_template("input.html", title="Y4N")


@app.route("/save", methods=['POST'])
def save():
    field = request.form['field']
    value = request.form['value']
    ret = w.zincrby('top10:phones', field, value)
    app.logger.debug(ret)
    new_value = r.zscore('top10:phones', value)
    return render_template('output.html', saved=1, phone=value, value=new_value,)

@app.route("/save_tablet", methods=['POST'])
def save_tablet():
    field_tablet = request.form['field_tablet']
    value_tablet = request.form['value_tablet']
    ret = w.zincrby('top10:tablets', field_tablet, value_tablet)
    app.logger.debug(ret)
    new_value_tablet = r.zscore('top10:tablets', value_tablet)
    return render_template('output.html', saved_tablet=1, tablet=value_tablet, value_tablet=new_value_tablet,)


@app.route("/get", methods=['POST'])
def get():
    field = request.form['field']
    value = r.get(field)
    if value is None:
        return render_template('output.html', field=field, value="Not defined yet")
    return render_template('output.html', field=field, value=value)

if __name__ == "__main__":
    app.run(host= '0.0.0.0', debug=True)
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0



