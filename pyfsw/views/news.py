from flask import render_template

from pyfsw import app, db
from pyfsw import News, Player
from pyfsw import ForumPost

@app.route('/')
def route_news():
	news = db.session().query(News).order_by(News.id.desc()).limit(5).all()
	for entry in news:
		player = db.session().query(Player.name).filter(Player.id == entry.author_id).first()
		if player:
			entry.author = player.name

		posts = db.session().query(ForumPost.id).filter(ForumPost.thread_id == entry.thread_id).count()
		entry.comments = posts

	return render_template('news/news.htm', news=news)

@app.route('/news/<int:id>')
def route_news_single(id):
	entry = db.session().query(News).filter(News.id == id).first()
	if not entry:
		return redirect(url_for('route_news'))

	player = db.session().query(Player.name).filter(Player.id == entry.author_id).first()
	if player:
		entry.author = player.name

	posts = db.session().query(ForumPost.id).filter(ForumPost.thread_id == entry.thread_id).count()
	entry.comments = posts

	return render_template('news/single.htm', entry=entry)

@app.route('/news/archive')
def route_news_archive():
	dicks()
	news = db.session().query(News).order_by(News.id.desc()).all()
	for entry in news:
		player = db.session().query(Player.name).filter(Player.id == entry.author_id).first()
		if player:
			entry.author = player.name

	return render_template('news/archive.htm', news=news)
