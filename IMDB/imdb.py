import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
import re
import sqlite3

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url='http://www.imdb.com/chart/top'
html = urllib.request.urlopen(url, context=ctx).read()
soup = BeautifulSoup(html, "html.parser")

mov=list()
ctr=0
tags= soup('a')
for tag in tags:
    ctr+=1
    if ctr<=59:
        continue
    if ctr%2!=0:
        continue
    mov.append(tag.text)
    if ctr>=558:
        break

release=list()
tags=soup('span',{"class":"secondaryInfo"})
for tag in tags:
    release.append(tag.text)

dir=list()
ctr=0
tags= soup('a')
for tag in tags:
    y=tag.get('title', None)
    if y==None:
        continue
    else:
        ctr+=1
        x=y.split()
        fname=x[0]
        lname=x[1]
        name=fname+" "+lname
        dir.append(name)
        if ctr==250:
            break

stars=list()
tags=soup('strong')
for tag in tags:
    stars.append(tag.text)

conn = sqlite3.connect('imdb.sqlite')
cur = conn.cursor()

# Do some setup
cur.executescript('''
DROP TABLE IF EXISTS Movie;
DROP TABLE IF EXISTS Year;
DROP TABLE IF EXISTS Director;
DROP TABLE IF EXISTS Stars;

CREATE TABLE Movie (
    id  INTEGER NOT NULL PRIMARY KEY
        AUTOINCREMENT UNIQUE,
    movie TEXT  UNIQUE,
    dir_id  INTEGER,
    year_id  INTEGER,
    stars_id INTEGER
);

CREATE TABLE Year (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    yr    INTEGER UNIQUE
);

CREATE TABLE Director (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT UNIQUE
);

CREATE TABLE Stars (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    stars    INTEGER UNIQUE
);
''')

i=0
while i<250:
    movie=mov[i]
    director=dir[i]
    year=release[i]
    star=stars[i]
    i+=1
    print(movie)
    cur.execute('''INSERT OR IGNORE INTO Year (yr)
        VALUES ( ? )''', ( year, ) )
    cur.execute('SELECT id FROM Year WHERE yr = ? ', (year, ))
    year_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Director (name)
        VALUES ( ? )''', (director, ) )
    cur.execute('SELECT id FROM Director WHERE name = ? ', (director, ))
    dir_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Stars (stars)
        VALUES ( ? )''', ( star, ) )
    cur.execute('SELECT id FROM Stars WHERE stars = ? ', (star, ))
    stars_id = cur.fetchone()[0]

    cur.execute('''INSERT OR REPLACE INTO Movie
        (movie, dir_id, year_id, stars_id)
        VALUES ( ?, ?, ?, ?)''',
        ( movie, dir_id, year_id, stars_id) )

conn.commit()
