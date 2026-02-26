#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_article = Blueprint('client_article', __name__,
                        template_folder='templates')

@client_article.route('/client/index')
@client_article.route('/client/article/show')              # remplace /client
def client_article_show():                                 # remplace client_index
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = """
    SELECT id_velo AS id_article,
        nom_velo AS nom,
        prix_velo AS prix,
        photo_velo AS photo,
        stock_velo AS stock,
        photo_velo AS image
    FROM Velo
    """
    condition_and = ""
    # utilisation du filtre
    sql3=''' prise en compte des commentaires et des notes dans le SQL    '''
    mycursor.execute(sql)
    articles = mycursor.fetchall()

    sql2 = ''' 
    SELECT Id_type as id_type_article, libelle_type FROM type '''
    mycursor.execute(sql2)
    # pour le filtre
    types_article = mycursor.fetchall()


    # Charger le panier du client connecté
    sql_panier = '''
        SELECT v.id_velo AS id_article,
               v.nom_velo AS nom,
               v.prix_velo AS prix,
               v.stock_velo AS stock,
               lp.quantite
        FROM ligne_panier lp
        JOIN Velo v ON v.id_velo = lp.article_id
        WHERE lp.utilisateur_id = %s
    '''
    mycursor.execute(sql_panier, (id_client,))
    articles_panier = mycursor.fetchall()

    if len(articles_panier) >= 1:
        prix_total = sum(item['prix'] * item['quantite'] for item in articles_panier)
    else:
        prix_total = None
    return render_template('client/boutique/panier_article.html'
                           , articles=articles
                           , articles_panier=articles_panier
                           , prix_total=prix_total
                           , items_filtre=types_article
                           )


#test merge