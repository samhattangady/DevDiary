
from flask import Flask, render_template, abort
from pymongo import MongoClient

TITLE = 'DevDiary - samhattangady'
BLOG_LIMIT = {'chars': 300, 'number': 2}

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

def get_blogposts(project=False):
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
    return post

# To format datetime.datetime into October 22, 1993 format
def format_dates(date):
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'June', 'July', 'August', 'September', 'October', 'November', 'December']
    return months[date.month+1] + ' ' + str(date.day) + ', ' + str(date.year)

#####################################################################
# Server stuff
#####################################################################
app = Flask(__name__)
db = MongoClient('localhost', 27017).devdiary

@app.route('/')
def home():
    return render_template('home.html', 
                            projects=get_projects(),
                            title=TITLE,
                            posts=get_blogposts(),
                            limit=BLOG_LIMIT)

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
                            limit=BLOG_LIMIT)

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
# TODO 
# @app.route('/<project>/blog')


if __name__ == '__main__':
    app.run(debug=True)