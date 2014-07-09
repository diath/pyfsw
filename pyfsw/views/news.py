from flask import render_template

from pyfsw import app, db
from pyfsw import News, Player

@app.route('/')
def route_news():
	news = db.session().query(News).order_by(News.id.desc()).limit(5).all()
	return render_template('news/news.htm', news=news)

@app.route('/news/<int:id>')
def route_news_single(id):
	entry = db.session().query(News).filter(News.id == id).first()
	if not entry:
		return redirect(url_for('route_news'))

	return render_template('news/single.htm', entry=entry)

@app.route('/news/archive')
def route_news_archive():
	news = db.session().query(News).order_by(News.id.desc()).all()
	return render_template('news/archive.htm', news=news)
