# -*- coding: utf-8 -*-

__all__ = ()

import datetime

import timeago
from quart import Blueprint
from quart import render_template
from quart import session
from quart import request
from quart import redirect
from quart import url_for
 
from objects import glob
from objects.utils import flash

from constants import regexes
from objects import glob
from objects import utils
from objects.privileges import Privileges
from objects.utils import flash
from objects.utils import flash_with_customizations

admin = Blueprint('admin', __name__)

@admin.route('/edit/<user_id>')
async def edit(user_id):
    """Render the user editing page."""

    user = await glob.db.fetch('SELECT * FROM users WHERE id=%s',[user_id])

    username = user['name']
    country = user['country']

    return await render_template('admin/edit.html', user_id=user_id, username=username, country=country)

@admin.route('/update/<user_id>', methods=['POST'])
async def update_user(user_id):
    """Update the username of a user."""
    if not 'authenticated' in session:
        return await flash('error', 'Please login first.', 'login')

    if not session['user_data']['is_staff']:
        return await flash('error', f'You have insufficient privileges.', 'home')
        
    form = await request.form

    new_name = form.get('username', type=str)
    country = form.get('country', type=str)
    safe_name = utils.get_safe_name(new_name)

    # username change successful
    await glob.db.execute(
        'UPDATE users '
        'SET name = %s, safe_name = %s, country = %s '
        'WHERE id = %s',
        [new_name, safe_name, country, user_id]
    )
    return redirect(url_for('admin.edit', user_id=user_id))


@admin.route('/')
@admin.route('/home')
@admin.route('/dashboard')
async def home():
    """Render the homepage of guweb's admin panel."""
    if not 'authenticated' in session:
        return await flash('error', 'Please login first.', 'login')

    if not session['user_data']['is_staff']:
        return await flash('error', f'You have insufficient privileges.', 'home')

    # fetch data from database
    dash_data = await glob.db.fetch(
        'SELECT COUNT(id) count, '
        '(SELECT name FROM users ORDER BY id DESC LIMIT 1) lastest_user, '
        '(SELECT COUNT(id) FROM users WHERE NOT priv & 1) banned '
        'FROM users'
    )

    recent_users = await glob.db.fetchall('SELECT * FROM users ORDER BY id DESC LIMIT 5')
    recent_scores = await glob.db.fetchall(
        'SELECT scores.*, maps.artist, maps.title, '
        'maps.set_id, maps.creator, maps.version '
        'FROM scores JOIN maps ON scores.map_md5 = maps.md5 '
        'ORDER BY scores.id DESC LIMIT 5'
    )

    return await render_template(
        'admin/home.html', dashdata=dash_data,
        recentusers=recent_users, recentscores=recent_scores,
        datetime=datetime, timeago=timeago
    )
