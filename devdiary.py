#!/home/samhattangady/anaconda3/bin/python

import os
import argparse
import datetime
import configparser

from pymongo import MongoClient

config = configparser.ConfigParser()
config.read('config.ini')
mongohost = str(config.get('database', 'mongohost'))
db = MongoClient(mongohost).get_default_database()

def get_live_projects():
    return [project for project in db.projects.find({'completion': False}, {'name': 1})]

def add_update(project, text, date):
    db.projects.update_one({'_id': project['_id']}, {'$push': {'updates': {'date': date, 'text': text}}})
    return

def add_blogpost(project, title, date, text):
    last = [post for post in db.blogs.find({'tags' : {'$in': [project['name']]}}, {'_id': 1})][-1]['_id']
    new = project['_id'] + str(int(last[len(project['_id']):])+1)
    db.blogs.insert_one({
            '_id': new,
            'date': date,
            'title': title,
            'text': text,
            'tags': [project['name']]
        })
    return


def complete_project(project, date):
    db.projects.update_one({'_id': project['_id']}, {'completion': date})
    return

def new_project(name, description, date, link):
    project = {
        'name': name,
        'start': date,
        'description': description,
        'link': link,
        '_id': name.replace(' ','').lower(),
        'updates': [],
        'completion': False
    }
    db.projects.insert_one(project)
    return

def get_project():
    live_projects = get_live_projects()
    print('Select which project to update:')
    for i, project in enumerate(live_projects):
        print('[{}]: {}'.format(i, project['name']))
    selected = int(input('Enter your selection:\t'))
    return live_projects[selected]

def get_date():
    date_in = input('Select date of update. \n[0]: Today\n[1]: Yesterday\n[2]: Other\n')
    if date_in == '0':
        date = datetime.datetime.today()
        date = datetime.datetime(date.year, date.month, date.day)
    elif date_in == '1':
        date = datetime.datetime.today()
        date = datetime.datetime(date.year, date.month, date.day)
        date = date - datetime.timedelta(days=1)
    elif date_in == '2':
        year = int(input('Year:'))
        month = int(input('Month:'))
        day = int(input('Day:'))
        date = datetime.datetime(year, month, day)
    return date

def main():
    parser = argparse.ArgumentParser(description='CLI to update DevDiary website')
    parser.add_argument('-u', '--update', help='To add an update to a live project', action="store_true")
    parser.add_argument('-n', '--new', help='To start a new project', action="store_true")
    parser.add_argument('-c', '--complete', help='To complete a live project', action="store_true")
    parser.add_argument('-b', '--blogpost_path', help='To add a blogpost. Enter the path to file with the post')
    args = parser.parse_args()

    if args.update:
        project = get_project()
        text = input('Enter text of update:\n')
        date = get_date()
        add_update(project, text, date)
        print('Update added succesfully!')

    if args.new:
        name = input('Input project name:\n')
        description = input('Input project description:\n')
        link = input('Input project link:\n')
        date = get_date()
        new_project(name, description, date, link)
        print('New project created succesfully!')

    if args.complete:
        complete_project(get_project(), get_date())
        print('Congrats on completing your project!')

    if args.blogpost_path:
        post = open(args.blogpost_path, 'r').read()
        print(post)
        title = input('Input title of post:\n')
        add_blogpost(get_project(), title, get_date(), post)
        print('Blog updated succesfully!')


if __name__ == '__main__':
    main()
