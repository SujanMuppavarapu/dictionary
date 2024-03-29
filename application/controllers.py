from flask import Flask, request, flash, redirect, url_for
from flask import render_template, session, jsonify
from flask import current_app as app 
from flask_wtf.csrf import CSRFProtect
import os
import requests
from sqlalchemy import desc, func, not_
from application.models import *

@app.route("/")
def index():
    words = Word.query.order_by(desc(Word.created_at)).all()
    return render_template("index.html", words=words)

@app.route("/add", methods=["GET","POST"])
def add():
    if request.method == "GET":
        return render_template("add.html")
    else:
        word = request.form["word"]
        definition = request.form["definition"]
        example = request.form["example"]
        root = request.form["root"]
        new_word = Word(word=word, definition=definition, example=example, root=root)
        db.session.add(new_word)
        db.session.commit()
        return redirect(url_for("index"))

@app.route('/define/<word>', methods=['GET'])
def define_word(word):
    if request.method == 'GET':
        word_data = get_word_definition(word)

        if word_data:
            return render_template('definition.html', word_data=word_data)
        else:
            return "Error fetching definition"

@app.route('/example')
def example_route():
    data = [{"word":"choleric","phonetic":"/kɘˈliɘɹɘk/","phonetics":[{"text":"/kɘˈliɘɹɘk/","audio":""},{"text":"/ˈkɒl(ə)ɹɪk/","audio":""},{"text":"/kəˈlɛɹɪk/","audio":""}],"meanings":[{"partOfSpeech":"noun","definitions":[{"definition":"A person with a choleric temperament.","synonyms":[],"antonyms":[]},{"definition":"A person suffering from cholera (infectious disease).","synonyms":[],"antonyms":[]}],"synonyms":[],"antonyms":[]},{"partOfSpeech":"adjective","definitions":[{"definition":"(according to theories of the four humours or temperaments) Having a temperament characterized by an excess of choler; easily becoming angry.","synonyms":[],"antonyms":[]},{"definition":"Showing or expressing anger.","synonyms":[],"antonyms":[]},{"definition":"Of or relating to cholera (infectious disease).","synonyms":[],"antonyms":[]},{"definition":"Causing an excess of choler.","synonyms":[],"antonyms":[]}],"synonyms":["ill-tempered","irascible","angry","indignant","irate","vexed","wrathful"],"antonyms":[]}],"license":{"name":"CC BY-SA 3.0","url":"https://creativecommons.org/licenses/by-sa/3.0"},"sourceUrls":["https://en.wiktionary.org/wiki/choleric"]}]
    return jsonify(data)

@app.route('/define_word', methods=['POST'])
def define_word_1():
    query = request.form.get('query')
    return redirect(url_for('define_word', word=query))

def get_word_definition(word):
    api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(api_url)

    if response.status_code == 200:
        return response.json()
    else:
        return None
    
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):
    word = Word.query.filter_by(id=id).first()
    if request.method == "GET":
        return render_template("edit.html", word=word)
    else:
        word.word = request.form["word"]
        word.definition = request.form["definition"]
        word.example = request.form["example"]
        word.root = request.form["root"]
        db.session.commit()
        return redirect(url_for("index"))
    
@app.route("/add_word/<word>", methods=["GET"])
def add_word(word):
    k = get_word_definition(word)
    if request.method == "GET":
        if k:
            word = Word(word=k[0]["word"])
            db.session.add(word)
            db.session.commit()
            return redirect(url_for("index"))
        else:
            return "Error fetching definition"
        return url_for("index")

@app.route("/delete/<int:id>", methods=["GET"])
def delete(id):
    word = Word.query.filter_by(id=id).first()
    db.session.delete(word)
    db.session.commit()
    return redirect(url_for("index"))