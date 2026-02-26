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

    sql = """SELECT id_velo AS id_article, nom_velo AS nom,
                    prix_velo AS prix, photo_velo AS image,
                    stock_velo AS stock
            FROM Velo WHERE 1=1"""
    params = []

    filter_word = session.get('filter_word', None)
    if filter_word:
        sql += " AND nom_velo LIKE %s"
        params.append(f"%{filter_word}%")

    filter_types = session.get('filter_types', [])
    if filter_types:
        placeholders = ', '.join(['%s'] * len(filter_types))
        sql += f" AND id_type IN ({placeholders})"
        params.extend(filter_types)

    filter_prix_min = session.get('filter_prix_min', None)
    if filter_prix_min:
        sql += " AND prix_velo >= %s"
        params.append(filter_prix_min)

    filter_prix_max = session.get('filter_prix_max', None)
    if filter_prix_max:
        sql += " AND prix_velo <= %s"
        params.append(filter_prix_max)

    mycursor.execute(sql, params)
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