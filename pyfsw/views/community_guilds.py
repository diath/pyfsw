from flask import render_template, request, flash, redirect, url_for, send_file
from sqlalchemy import or_
from werkzeug.utils import secure_filename

import re
import os
from time import time
from PIL import Image

from pyfsw import app, db, cache
from pyfsw import CACHE_TIME, UPLOAD_PATH
from pyfsw import filter_rank
from pyfsw import current_user, login_required, is_guild_leader, is_guild_vice
from pyfsw import Player
from pyfsw import Guild, GuildInvite, GuildMembership, GuildRank, GuildWar

GUILD_NAME_EXPR = re.compile('^([a-zA-Z ]+)$')

@app.route('/community/guilds')
@cache.cached(timeout=CACHE_TIME)
def route_community_guilds():
	guilds = Guild.query.order_by(Guild.name).all()
	return render_template('community/guilds/list.htm', guilds=guilds, user=current_user())

@app.route('/community/guild/<int:id>')
@cache.cached(timeout=CACHE_TIME)
def route_community_guild(id):
	guild = Guild.query.filter(Guild.id == id).first()
	members = GuildMembership.query.filter(GuildMembership.guild_id == guild.id).all()
	invites = GuildInvite.query.filter(GuildInvite.guild_id == guild.id).all()
	wars = GuildWar.query.filter(or_(GuildWar.guild1 == id, GuildWar.guild2 == id)).filter(GuildWar.status == GuildWar.Active).all()

	user = current_user()
	if user:
		ids = []
		for player in user.players:
			ids.append(player.id)

		for invite in invites:
			if invite.player_id in ids:
				invite.own = True

		for member in members:
			if member.player_id in ids:
				member.own = True

	return render_template(
		'community/guilds/view.htm', guild=guild, members=members, invites=invites,
		leader=is_guild_leader(id), vice=is_guild_vice(id), wars=wars
	)

@app.route('/community/guild/create', methods=['GET'])
@login_required
def route_community_guild_create():
	characters = current_user().players
	return render_template('community/guilds/create.htm', characters=characters)

@app.route('/community/guild/create', methods=['POST'])
@login_required
def route_community_guild_create_post():
	name = request.form.get('name', '', type=str)
	character = request.form.get('character', 0, type=int)
	motd = request.form.get('motd', '', type=str)
	user = current_user()
	error = False

	character = Player.query.filter(Player.id == character).first()
	if not character or character.account_id != user.id:
		flash('You can not create a guild with not your own character.', 'error')
		error = True

	if character and character.level < 100:
		flash('The character needs to be at least level 100.', 'error')
		error = True

	if character and character.getGuild():
		flash('The character can not be a member of another guild.', 'error')
		error = True

	if len(name) < 4 or len(name) > 32:
		flash('The guild name must be between 4 and 32 characters long.', 'error')
		error = True

	if not GUILD_NAME_EXPR.match(name):
		flash('The guild name may only contain latin characters (A-Z, a-z and spaces).', 'error')
		error = True

	if len(name.split(' ')) > 3:
		flash('The guild name may only consist of 3 words.', 'error')
		error = True

	guild = Guild.query.filter(Guild.name == name).first()
	if guild:
		flash('The guild name is taken by another guild.', 'error')
		error = True

	if error:
		return redirect(url_for('route_community_guild_create'))

	guild = Guild()
	guild.name = name
	guild.ownerid = character.id
	guild.creationdata = int(time())
	guild.motd = motd

	db.session().add(guild)
	db.session().commit()

	rank = db.session().query(GuildRank.id).filter(GuildRank.guild_id == guild.id).filter(GuildRank.level == 3).first()

	membership = GuildMembership()
	membership.player_id = character.id
	membership.guild_id = guild.id
	membership.rank_id = rank[0]

	db.session().add(membership)
	db.session().commit()

	flash('The guild has been created.', 'success')

	return redirect(url_for('route_community_guild', id=guild.id))

@app.route('/community/guild/<int:id>/invite', methods=['GET'])
@login_required
def route_community_guild_invite(id):
	if not is_guild_vice(id):
		return redirect(url_for('route_community_guild', id=id))

	return render_template('community/guilds/invite.htm', id=id)

@app.route('/community/guild/<int:id>/invite', methods=['POST'])
@login_required
def route_community_guild_invite_post(id):
	if not is_guild_vice(id):
		return redirect(url_for('route_community_guild', id=id))

	name = request.form.get('name', '', type=str)
	error = False

	player = Player.query.filter(Player.name == name).first()
	if not player:
		flash('The player you are trying to invite does not exist.', 'error')
		return redirect(url_for('route_community_guild', id=id))

	membership = GuildMembership.query.filter(GuildMembership.guild_id == id).filter(GuildMembership.player_id == player.id).first()
	if membership:
		flash('The player is already a member of your guild.', 'error')
		error = True

	invite = GuildInvite.query.filter(GuildInvite.guild_id == id).filter(GuildInvite.player_id == player.id).first()
	if invite:
		flash('The player is already invited to your guild.', 'error')
		error = True

	if not error:
		invite = GuildInvite()
		invite.player_id = player.id
		invite.guild_id = id

		db.session().add(invite)
		db.session().commit()

		flash('The player has been invited.', 'success')

	return redirect(url_for('route_community_guild', id=id))

@app.route('/community/guild/<int:id>/kick', methods=['GET'])
@login_required
def route_community_guild_kick(id):
	if not is_guild_vice(id):
		return redirect(url_for('route_community_guild', id=id))

	ranks = []
	for rank in GuildRank.query.filter(GuildRank.guild_id == id).all():
		ranks.append(rank.id)

	if len(ranks):
		members = GuildMembership.query.filter(GuildMembership.guild_id == id).filter(GuildMembership.rank_id.notin_(ranks)).all()
	else:
		members = []

	return render_template('community/guilds/kick.htm', id=id, members=members)

@app.route('/community/guild/<int:id>/kick', methods=['POST'])
@login_required
def route_community_guild_kick_post(id):
	if not is_guild_vice(id):
		return redirect(url_for('route_community_guild', id=id))

	player = request.form.get('id', 0, type=int)
	membership = GuildMembership.query.filter(GuildMembership.guild_id).filter(GuildMembership.player_id == player).first()
	if not membership:
		return redirect(url_for('route_community_guild', id=id))

	db.session().delete(membership)
	db.session().commit()

	flash('The player has been kicked from the guild.', 'success')

	return redirect(url_for('route_community_guild', id=id))

@app.route('/community/guild/<int:gid>/join/<int:pid>', methods=['GET'])
@login_required
def route_community_guild_join(gid, pid):
	user = current_user()
	found = False

	for player in user.players:
		if player.id == pid:
			found = True
			break

	if not found:
		return redirect(url_for('route_community_guild', id=gid))

	invite = GuildInvite.query.filter(GuildInvite.guild_id == gid)
	invite = invite.filter(GuildInvite.player_id == pid).first()

	if not invite:
		return redirect(url_for('route_community_guild', id=gid))

	rank = db.session().query(GuildRank.id).filter(GuildRank.guild_id == gid)
	rank = rank.filter(GuildRank.level == 1).first()

	if not rank:
		return redirect(url_for('route_community_guild', id=gid))

	membership = GuildMembership()
	membership.player_id = pid
	membership.guild_id = gid
	membership.rank_id = rank.id
	membership.nick = ''

	db.session().delete(invite)
	db.session().add(membership)

	db.session().commit()

	flash('You have joined the guild.', 'success')

	return redirect(url_for('route_community_guild', id=gid))

@app.route('/community/guild/<int:gid>/leave/<int:pid>', methods=['GET'])
@login_required
def route_community_guild_leave(gid, pid):
	user = current_user()
	found = False

	for player in user.players:
		if player.id == pid:
			found = True
			break

	if not found:
		return redirect(url_for('route_community_guild', id=gid))

	membership = GuildMembership.query.filter(GuildMembership.guild_id == gid)
	membership = membership.filter(GuildMembership.player_id == pid).first()

	if not membership:
		return redirect(url_for('route_community_guild', id=gid))

	rank = db.session().query(GuildRank.level).filter(GuildRank.id == membership.rank_id).first()
	if not rank:
		return redirect(url_for('route_community_guild', id=gid))

	if rank.level < 3:
		db.session().delete(membership)
		db.session().commit()

		flash('You left the guild.', 'success')
	else:
		flash('Guild leaders can not leave the guild, use the disband feature instead.', 'error')

	return redirect(url_for('route_community_guild', id=gid))

@app.route('/community/guild/<int:id>/ranks', methods=['GET'])
@login_required
def route_community_guild_ranks(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	ranks = GuildRank.query.filter(GuildRank.guild_id == id).all()
	if not ranks:
		return redirect(url_for('route_community_guild', id=id))

	return render_template('community/guilds/ranks.htm', id=id, ranks=ranks)

@app.route('/community/guild/<int:id>/ranks', methods=['POST'])
@login_required
def route_community_guild_ranks_post(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	for level in range(1, 4):
		value = request.form.get('rank{}'.format(level), '', type=str)
		error = False

		if not GUILD_NAME_EXPR.match(value):
			flash('{} rank name may only contain latin characters (A-Z, a-z and spaces).'.format(filter_rank(level)), 'error')
			error = True

		if len(value) < 4 or len(value) > 16:
			flash('{} rank name must be between 4 and 16 characters long.'.format(filter_rank(level)), 'error')
			error = True

		if not error:
			rank = GuildRank.query.filter(GuildRank.guild_id == id).filter(GuildRank.level == level).first()
			rank.name = value

			db.session().commit()

			flash('{} rank name has been updated.'.format(filter_rank(level)), 'success')

	return redirect(url_for('route_community_guild_ranks', id=id))

@app.route('/community/guild/<int:id>/rank', methods=['GET'])
@login_required
def route_community_guild_rank(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	ranks = []
	for rank in db.session().query(GuildRank.id).filter(GuildRank.guild_id == id).filter(GuildRank.level < 3).all():
		ranks.append(rank.id)

	membership = db.session().query(GuildMembership.player_id, GuildMembership.rank_id)
	membership = membership.filter(GuildMembership.guild_id == id)
	membership = membership.filter(GuildMembership.rank_id.in_(ranks)).all()

	members = []
	for entry in membership:
		player = db.session().query(Player.id, Player.name).filter(Player.id == entry.player_id).first()
		if player:
			members.append(player)

	return render_template('community/guilds/rank.htm', id=id, members=members)

@app.route('/community/guild/<int:id>/rank', methods=['POST'])
@login_required
def route_community_guild_rank_post(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	pid = request.form.get('id', 0, type=int)
	level = request.form.get('rank', 0, type=int)

	if level not in [1, 2]:
		return redirect(url_for('route_community_guild', id=id))

	if not db.session().query(Player.id).filter(Player.id == pid).first():
		flash('The player does not exist.', 'error')
		return redirect(url_for('route_community_guild', id=id))

	rank = db.session().query(GuildRank.id).filter(GuildRank.guild_id == id)
	rank = rank.filter(GuildRank.level == level).first()
	if not rank:
		flash('The rank does not exist', 'error')
		return redirect(url_for('route_community_guild', id=id))

	membership = GuildMembership.query.filter(GuildMembership.player_id == pid).first()
	if not membership:
		return redirect(url_for('route_community_guild', id=id))

	membership.rank_id = rank.id
	db.session().commit()

	flash('The rank has been updated.', 'success')

	return redirect(url_for('route_community_guild', id=id))

@app.route('/community/guild/<int:id>/motd', methods=['GET'])
@login_required
def route_community_guild_motd(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	guild = Guild.query.filter(Guild.id == id).first()
	if not guild:
		return redirect(url_for('route_community_guild', id=id))

	return render_template('community/guilds/motd.htm', id=id, motd=guild.motd)

@app.route('/community/guild/<int:id>/motd', methods=['POST'])
@login_required
def route_community_guild_motd_post(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	guild = Guild.query.filter(Guild.id == id).first()
	if not guild:
		return redirect(url_for('route_community_guild', id=id))

	motd = request.form.get('motd', '', type=str)
	guild.motd = motd

	db.session().commit()
	flash('The guild description has been changed.', 'success')

	return redirect(url_for('route_community_guild', id=id))

@app.route('/community/guild/<int:id>/logo', methods=['GET'])
@login_required
def route_community_guild_logo(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	return render_template('community/guilds/logo.htm', id=id)

@app.route('/community/guild/<int:id>/logo', methods=['POST'])
@login_required
def route_community_guild_logo_post(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	file = request.files.get('logo')
	error = False

	if file:
		name = secure_filename(file.filename)
		if len(name) == 0 or not '.' in name and not name.rsplit('.', 1)[1] in ['png', 'gif', 'jpg', 'jpeg']:
			flash('The file extension is not allowed.', 'error')
			error = True

		if len(file.getvalue()) > 3 * 1024 * 1024:
			flash('The file size exceeds the limit of 3 MB.', 'error')
			error = True

		if file.content_type not in ['image/png', 'image/gif', 'image/jpeg']:
			flash('The file format is not allowed.', 'error')
			error = True

		if not error:
			name = os.path.join(UPLOAD_PATH, '{}.png'.format(id))
			file.save(name)

			try:
				image = Image.open(name)
				image.convert('RGBA')
				image.thumbnail((128, 128), Image.ANTIALIAS)
				image.save(name)
			except Exception as e:
				flash('Failed to upload the file.', 'error')
				os.remove(name)
				error = True
	else:
		flash('Failed to upload the file.', 'error')
		error = True

	if not error:
		flash('The guild logo has been changed. If you still see the old logo, try using CTRL+F5, which should erase the previously cached image.', 'success')

	return redirect(url_for('route_community_guild', id=id))

@app.route('/community/guild/<int:id>/getlogo', methods=['GET'])
def route_community_guild_getlogo(id):
	path = os.path.join(UPLOAD_PATH, '{}.png'.format(id))
	if os.path.isfile(path):
		return send_file(path, 'image/png')

	return send_file(os.path.join(UPLOAD_PATH, 'default.png'), 'image/png')

@app.route('/community/guild/<int:id>/disband', methods=['GET'])
@login_required
def route_community_guild_disband(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	return render_template('community/guilds/disband.htm', id=id)

@app.route('/community/guild/<int:id>/disband', methods=['POST'])
@login_required
def route_community_guild_disband_post(id):
	if not is_guild_leader(id):
		return redirect(url_for('route_community_guild', id=id))

	guild = Guild.query.filter(Guild.id == id).first()
	db.session().delete(guild)
	db.session().commit()

	logo = os.path.join(UPLOAD_PATH, '{}.png'.format(id))
	if os.path.isfile(logo):
		os.remove(logo)

	return redirect(url_for('route_community_guilds'))
