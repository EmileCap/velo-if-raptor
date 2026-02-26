#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_panier = Blueprint('client_panier', __name__,
                        template_folder='templates')


@client_panier.route('/client/panier/add', methods=['POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')
    quantite = int(request.form.get('quantite', 1))

    # Vérifier que le stock est suffisant
    sql_stock = 'SELECT stock_velo FROM Velo WHERE id_velo = %s'
    mycursor.execute(sql_stock, (id_article,))
    velo = mycursor.fetchone()

    if velo is None or velo['stock_velo'] < quantite:
        flash("Stock insuffisant pour cet article.", "danger")
        return redirect('/client/article/show')

    # Vérifier si l'article est déjà dans le panier du client
    sql_check = '''
        SELECT quantite FROM ligne_panier
        WHERE utilisateur_id = %s AND article_id = %s
    '''
    mycursor.execute(sql_check, (id_client, id_article))
    ligne = mycursor.fetchone()

    if ligne:
        # Mettre à jour la quantité existante
        sql_update = '''
            UPDATE ligne_panier
            SET quantite = quantite + %s
            WHERE utilisateur_id = %s AND article_id = %s
        '''
        mycursor.execute(sql_update, (quantite, id_client, id_article))
    else:
        # Insérer une nouvelle ligne dans le panier
        sql_insert = '''
            INSERT INTO ligne_panier (utilisateur_id, article_id, quantite, date_ajout)
            VALUES (%s, %s, %s, CURDATE())
        '''
        mycursor.execute(sql_insert, (id_client, id_article, quantite))

    # Décrémenter le stock
    sql_stock_update = 'UPDATE Velo SET stock_velo = stock_velo - %s WHERE id_velo = %s'
    mycursor.execute(sql_stock_update, (quantite, id_article))

    get_db().commit()
    flash("Article ajouté au panier.", "success")
    return redirect('/client/article/show')


@client_panier.route('/client/panier/delete', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article', '')

    # Récupérer la ligne du panier
    sql = '''
        SELECT quantite FROM ligne_panier
        WHERE utilisateur_id = %s AND article_id = %s
    '''
    mycursor.execute(sql, (id_client, id_article))
    article_panier = mycursor.fetchone()

    if article_panier is None:
        return redirect('/client/article/show')

    if article_panier['quantite'] > 1:
        sql_update = '''
            UPDATE ligne_panier SET quantite = quantite - 1
            WHERE utilisateur_id = %s AND article_id = %s
        '''
        mycursor.execute(sql_update, (id_client, id_article))
    else:
        sql_delete = '''
            DELETE FROM ligne_panier
            WHERE utilisateur_id = %s AND article_id = %s
        '''
        mycursor.execute(sql_delete, (id_client, id_article))

    # Remettre 1 unité en stock
    mycursor.execute('UPDATE Velo SET stock_velo = stock_velo + 1 WHERE id_velo = %s', (id_article,))
    get_db().commit()
    return redirect('/client/article/show')


@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    client_id = session['id_user']

    sql = 'SELECT article_id, quantite FROM ligne_panier WHERE utilisateur_id = %s'
    mycursor.execute(sql, (client_id,))
    items_panier = mycursor.fetchall()

    for item in items_panier:
        mycursor.execute(
            'DELETE FROM ligne_panier WHERE utilisateur_id = %s AND article_id = %s',
            (client_id, item['article_id'])
        )
        mycursor.execute(
            'UPDATE Velo SET stock_velo = stock_velo + %s WHERE id_velo = %s',
            (item['quantite'], item['article_id'])
        )

    get_db().commit()
    return redirect('/client/article/show')


@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article', '')

    sql_select = 'SELECT quantite FROM ligne_panier WHERE utilisateur_id = %s AND article_id = %s'
    mycursor.execute(sql_select, (id_client, id_article))
    ligne = mycursor.fetchone()

    if ligne:
        mycursor.execute(
            'DELETE FROM ligne_panier WHERE utilisateur_id = %s AND article_id = %s',
            (id_client, id_article)
        )
        mycursor.execute(
            'UPDATE Velo SET stock_velo = stock_velo + %s WHERE id_velo = %s',
            (ligne['quantite'], id_article)
        )

    get_db().commit()
    return redirect('/client/article/show')


@client_panier.route('/client/panier/filtre', methods=['POST'])
def client_panier_filtre():
    session['filter_word']     = request.form.get('filter_word', None)
    session['filter_prix_min'] = request.form.get('filter_prix_min', None)
    session['filter_prix_max'] = request.form.get('filter_prix_max', None)
    session['filter_types']    = request.form.getlist('filter_types')
    # test des variables puis
    # mise en session des variables
    return redirect('/client/article/show')


@client_panier.route('/client/panier/filtre/suppr', methods=['POST'])
def client_panier_filtre_suppr():
    session.pop('filter_word', None)
    session.pop('filter_prix_min', None)
    session.pop('filter_prix_max', None)
    session.pop('filter_types', None)
    print("suppr filtre")
    return redirect('/client/article/show')