import math
import calendar
import datetime
import configparser

from flask import Flask, render_template, abort, jsonify
from pymongo import MongoClient

config = configparser.ConfigParser()
config.read('config.ini')

TITLE = 'DevDiary - samhattangady'
BLOG_LIMIT = {'chars': 300, 'number': 2}
# Did some prototyping in Inkscape. 690*80, 12.5 sq days, 4 rows, 5 months looks good
CALENDAR_SHOW_MONTHS = 5
NUMBER_OF_ROWS = 4
# Picked from Material Design. Purple->Light Blue 100
COLOURS = ['#E1BEE7', '#D1C4E9', '#C5CAE9', '#BBDEFB', '#B3E5FC']
MISSED_DAY_COLOUR = '#CFD8DC'

#####################################################################
# Helper Functions
#####################################################################
def get_projects():
    projects = {'live': [], 'completed': []}
    for project in db.projects.find():
        if project['completion']:
            projects['completed'].append(project)
        else:
            projects['live'].append(project)
    return projects

def get_project_details(project):
    details = db.projects.find_one({'_id':project.lower()})
    details['start'] = format_dates(details['start'])
    if details['completion']:
        details['completion'] = format_dates(details['completion'])
    else:
        details['completion'] = 'Present'
    details['updates'].sort(key = lambda x: x['date'], reverse=True)
    for update in details['updates']:
        update['date'] = format_dates(update['date'])
    return details

def get_blogposts(project=None):
    if project:
        posts = [post for post in db.blogs.find({'tags': {'$in': [project]}})]
    else:
        posts = [post for post in db.blogs.find()]
    posts.sort(key=lambda x: x['date'], reverse=True)
    for post in posts:
        post['date'] = format_dates(post['date'])
    return posts

def get_post(post_id):
    post = db.blogs.find_one({'_id': post_id})
    post['date'] = format_dates(post['date'])
    post['text'] = post['text'].split('\n')
    return post

# Function returns JSON to be used by canvas object to render calendar heatmap
def get_calendar(project=None):
    if project:
        # blogs = [post['date'] for post in db.blogs.find({'tags': {'$in': [project]}})]
        dates = [update['date'] for update in db.projects.find_one({'_id': project.lower()})['updates']]
        start = db.projects.find_one({'_id': project.lower()})['start']
        end = db.projects.find_one({'_id': project.lower()})['completion']
    else:
        # blogs = [post['date'] for post in db.blogs.find()]
        dates = [update['date'] for project in db.projects.find() for update in project['updates']]
        start = [project['start'] for project in db.projects.find()]
        start = min(start)  # To get the starting date of first project
        end = None
    # blogs.sort()
    dates.sort()

    # Code to get first day of previous n months, where n=CALENDAR_SHOW_MONTHS
    # We use this to populate final return item
    month = end if end else datetime.datetime.today()
    month = datetime.datetime(month.year, month.month, month.day)
    months = []
    for _ in range(CALENDAR_SHOW_MONTHS):
        month = month.replace(day=1)
        months.append(month)
        month = month - datetime.timedelta(days=1)
    months.reverse()

    # Set all days on calendar to 0
    max_days = math.ceil(31/NUMBER_OF_ROWS) * NUMBER_OF_ROWS
    cal = {month: [0]*max_days for month in months}

    # Set all valid days after start to -1 (signifying no update on that day)
    for month in months:
        days_in_month = calendar.monthrange(month.year, month.month)[1]
        if (start-month).days < 0:  # month is after start
            for day in range(days_in_month):
                cal[month][day] = -1
        elif start.replace(day=1) == month:  # start is in given month
            for day in range(start.day-1, days_in_month):
                cal[month][day] = -1

    # Set all days after end/present day back to 0
    # TODO. Should be grouped with previous block, but eh.
    # Note that since months are taken from present/end, we 
    # only need to do this for the last month
    last = end if end else datetime.datetime.today()
    for day in range(last.day-1, max_days):
        cal[months[-1]][day] = 0

    # Set all days with updates to 1
    for date in dates:
        if (date-months[0]).days >= 0:  # date lies in calendar range
            cal[date.replace(day=1)][date.day-1] = 1

    final = {'months': [month.strftime('%B \'%y') for month in months], 
             'days': [cal[month] for month in months],
             'rows': NUMBER_OF_ROWS,
             'colours': COLOURS,
             'missed_day': MISSED_DAY_COLOUR}
    return final

# To format datetime.datetime into October 22, 1993 format
def format_dates(date):
    return date.strftime('%B %d, %Y') 

#####################################################################
# Server stuff
#####################################################################
mongo = str(config.get('database', 'mongohost'))
app = Flask(__name__)
db = MongoClient(mongo).get_default_database()

@app.route('/')
def home():
    return render_template('home.html', 
                            projects=get_projects(),
                            title=TITLE,
                            posts=get_blogposts(),
                            limit=BLOG_LIMIT,
                            calendar=get_calendar())

@app.route('/<project>')
def load_page(project):
    projects = [p['_id'].lower() for p in db.projects.find()]
    if project.lower() not in projects:
        abort(404)
    return render_template('project_page.html', 
                            project=project,
                            details=get_project_details(project),
                            title=project+' - '+TITLE,
                            posts=get_blogposts(project),
                            limit=BLOG_LIMIT,
                            calendar=get_calendar(project))

@app.route('/blog')
def blog():
    return render_template('blog_page.html', 
                            title='Blog - '+TITLE, 
                            posts=get_blogposts(),
                            limit={'chars': BLOG_LIMIT['chars'],
                                   'number': None})

@app.route('/blog/<post_id>')
def blog_post(post_id):
    post = get_post(post_id)
    return render_template('blog_post.html',
                            title=post['title']+' - '+TITLE,
                            post=post)

@app.route('/<project>/blog')
def project_blogs(project):
    return render_template('blog_page.html', 
                            title='Blog - '+TITLE, 
                            posts=get_blogposts(project),
                            limit={'chars': BLOG_LIMIT['chars'],
                                   'number': None})


if __name__ == '__main__':
    app.run(debug=True)