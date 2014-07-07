from flask import render_template, request

from pyfsw import app, db
from pyfsw import QUESTS, TOWNS, HOUSE_PRICE
from pyfsw import Player, PlayerStorage, PlayerDeath, PlayerOnline
from pyfsw import House
from pyfsw import MarketOffer, MarketHistory
from pyfsw import GuildWar, GuildWarKill

HS_TYPES = {
	'level': ('Level', Player.experience.desc(), 'level', 'experience', 'experience'),
	'mag': ('Magic Level', Player.maglevel.desc(), 'maglevel', 'manaspent', 'mana spent'),
	'fist': ('Fist Fighting', Player.skill_fist.desc(), 'skill_fist', 'skill_fist_tries', 'hits'),
	'club': ('Club Fighting', Player.skill_club.desc(), 'skill_club', 'skill_club_tries', 'hits'),
	'sword': ('Sword Fighting', Player.skill_sword.desc(), 'skill_sword', 'skill_sword_tries', 'hits'),
	'axe': ('Axe Fighting', Player.skill_axe.desc(), 'skill_axe', 'skill_axe_tries', 'hits'),
	'dist': ('Distance', Player.skill_dist.desc(), 'skill_dist', 'skill_dist_tries', 'hits'),
	'shield': ('Shielding', Player.skill_shielding.desc(), 'skill_shielding', 'skill_shielding_tries', 'blocks'),
	'fish': ('Fishing', Player.skill_fishing.desc(), 'skill_fishing', 'skill_fishing_tries', 'tries')
}

@app.route('/community/player', methods=['GET'])
def route_community_player_get():
	return render_template('community/player_search.htm')

@app.route('/community/player/<string:name>')
def route_community_player_get_name(name):
	player = Player.query.filter(Player.name == name).first()

	if player is None:
		return render_template('community/player_search.htm', error=True)

	return render_template('community/player_view.htm', player=player, guild=player.getGuild(), quests=QUESTS)

@app.route('/community/player', methods=['POST'])
def route_community_player_post():
	name = request.form.get('name', '', type=str)
	player = Player.query.filter(Player.name == name).first()

	if player is None:
		return render_template('community/player_search.htm', error=True)

	return render_template('community/player_view.htm', player=player, guild=player.getGuild(), quests=QUESTS)

@app.route('/community/highscores/<string:type>')
def route_community_highscores(type):
	current = HS_TYPES.get(type)
	if current is None:
		return redirect(url_for('route_community_highscores', type='level'))

	highscores = Player.query.filter(Player.group_id == 1)
	highscores = highscores.order_by(current[1])
	highscores = highscores.limit(100).all()

	for player in highscores:
		player.value = getattr(player, current[2])
		player.subvalue = getattr(player, current[3])

	return render_template('community/highscores.htm', type=type, name=current[0], highscores=highscores, suffix=current[4])

@app.route('/community/houses/<int:town_id>')
def route_community_houses(town_id):
	houses = House.query.order_by(House.id)

	if town_id != 0:
		houses = houses.filter(House.town_id == town_id)

	return render_template('community/houses.htm', towns=TOWNS, town_id=town_id, price=HOUSE_PRICE, houses=houses.all())

@app.route('/community/staff')
def route_community_staff():
	gms = Player.query.filter(Player.group_id == 3).all()
	tutors = Player.query.filter(Player.group_id == 2).all()

	return render_template('community/staff.htm', gms=gms, tutors=tutors)

@app.route('/community/deaths')
def route_community_deaths():
	deaths = PlayerDeath.query.limit(25).all()
	for death in deaths:
		player = db.session().query(Player.name).filter(Player.id == death.player_id).first()
		if player:
			death.name = player.name
		else:
			death.name = 'Unknown'

	return render_template('community/deaths.htm', deaths=deaths)

@app.route('/community/online')
def route_community_online():
	online = PlayerOnline.query.all()
	return render_template('community/online.htm', online=online)

@app.route('/community/market')
def route_community_market():
	sell = MarketOffer.query.filter(MarketOffer.sale == 1).all()
	buy = MarketOffer.query.filter(MarketOffer.sale == 0).all()
	history = MarketHistory.query.all()

	return render_template('community/market.htm', sell=sell, buy=buy, history=history)

@app.route('/community/wars')
def route_community_wars():
	active = GuildWar.query.filter(GuildWar.status == GuildWar.Active).all()
	pending = GuildWar.query.filter(GuildWar.status == GuildWar.Pending).all()
	ended = GuildWar.query.filter(GuildWar.status == GuildWar.ended).all()

	return render_template('community/wars.htm', active=active, pending=pending, ended=ended)

@app.route('/community/war/<int:id>')
def route_community_war(id):
	war = GuildWar.query.filter(GuildWar.id == id).first()
	if not war:
		return redirect(url_for('route_community_wars'))

	return render_template('community/war.htm', war=war)
