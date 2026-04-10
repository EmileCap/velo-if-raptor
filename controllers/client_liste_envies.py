#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

from connexion_db import get_db

client_liste_envies = Blueprint('client_liste_envies', __name__,
                        template_folder='templates')


@client_liste_envies.route('/client/envie/toggle', methods=['get'])
def toggle_envie():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')

    # vérifier si existe
    sql = """
    SELECT * FROM wishlist
    WHERE utilisateur_id = %s AND id_velo = %s
    """
    mycursor.execute(sql, (id_client, id_article))
    exist = mycursor.fetchone()

    if exist:
        # supprimer
        sql = """
        DELETE FROM wishlist
        WHERE utilisateur_id = %s AND id_velo = %s
        """
        mycursor.execute(sql, (id_client, id_article))
    else:
        # ajouter
        sql = """
        INSERT INTO wishlist (utilisateur_id, id_velo, date_ajout)
        VALUES (%s, %s, NOW())
        """
        mycursor.execute(sql, (id_client, id_article))

    get_db().commit()
    return redirect('/client/envies/show')



@client_liste_envies.route('/client/envies/show', methods=['get'])
def client_liste_envies_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article_detail = request.args.get('id_article_detail_wishlist')

    sql = """
    SELECT v.id_velo AS id_article, v.nom_velo AS nom, v.prix_velo AS prix,
           v.photo_velo AS image, v.stock_velo AS stock, v.id_type,
           w.date_ajout, w.position
    FROM wishlist w
    JOIN Velo v ON v.id_velo = w.id_velo
    WHERE w.utilisateur_id = %s
    ORDER BY w.date_ajout DESC
    """
    mycursor.execute(sql, (id_client,))
    articles_liste_envies = mycursor.fetchall()

    sql = "SELECT COUNT(*) AS nb FROM wishlist WHERE utilisateur_id = %s"
    mycursor.execute(sql, (id_client,))
    nb_liste_envies = mycursor.fetchone()['nb']

    sql = """
    SELECT v.id_velo AS id_article, v.nom_velo AS nom, v.prix_velo AS prix, v.photo_velo AS image
    FROM historique h
    JOIN Velo v ON v.id_velo = h.id_velo
    WHERE h.utilisateur_id = %s
    ORDER BY h.date_consultation DESC
    LIMIT 6
    """
    mycursor.execute(sql, (id_client,))
    articles_historique = mycursor.fetchall()


    sql = "SELECT COUNT(*) AS nb FROM historique WHERE utilisateur_id = %s"
    mycursor.execute(sql, (id_client,))
    nb_liste_historique = mycursor.fetchone()['nb']

    info_wishlist = None
    info_wishlist_categorie = None


    if id_article_detail:
        id_article_detail = int(id_article_detail)

        # autres clients
        sql = """
        SELECT COUNT(*) AS nb_wish_list_other
        FROM wishlist
        WHERE id_velo = %s AND utilisateur_id != %s
        """
        mycursor.execute(sql, (id_article_detail, id_client))
        nb_other = mycursor.fetchone()

        # nom
        sql = "SELECT nom_velo FROM Velo WHERE id_velo = %s"
        mycursor.execute(sql, (id_article_detail,))
        nom = mycursor.fetchone()

        info_wishlist = {
            'nb_wish_list_other': nb_other['nb_wish_list_other'],
            'nom': nom['nom_velo']
        }

        # catégorie
        sql = """
        SELECT COUNT(*) AS nb_wish_list_other_categorie, t.libelle_type
        FROM wishlist w
        JOIN Velo v ON v.id_velo = w.id_velo
        JOIN type t ON t.id_type = v.id_type
        WHERE w.utilisateur_id = %s
        AND v.id_type = (SELECT id_type FROM Velo WHERE id_velo = %s)
        AND w.id_velo != %s
        """
        mycursor.execute(sql, (id_client, id_article_detail, id_article_detail))
        info_wishlist_categorie = mycursor.fetchone()

    return render_template(
        'client/liste_envies/liste_envies_show.html',
        articles_liste_envies=articles_liste_envies,
        articles_historique=articles_historique,
        nb_liste_envies=nb_liste_envies,
        nb_liste_historique=nb_liste_historique,
        info_wishlist=info_wishlist,
        info_wishlist_categorie=info_wishlist_categorie
    )



def client_historique_add(article_id, client_id):
    mycursor = get_db().cursor()

    # insert/update
    sql = """
    INSERT INTO historique (utilisateur_id, id_velo)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE
        nb_consultation = nb_consultation + 1,
        date_consultation = NOW()
    """
    mycursor.execute(sql, (client_id, article_id))

    # limiter à 6
    sql = """
    DELETE FROM historique
    WHERE utilisateur_id = %s
    AND id_velo NOT IN (
        SELECT id_velo FROM (
            SELECT id_velo
            FROM historique
            WHERE utilisateur_id = %s
            ORDER BY date_consultation DESC
            LIMIT 6
        ) tmp
    )
    """
    mycursor.execute(sql, (client_id, client_id))

    # supprimer vieux
    sql = """
    DELETE FROM historique
    WHERE date_consultation < NOW() - INTERVAL 1 MONTH
    """
    mycursor.execute(sql)

    get_db().commit()


@client_liste_envies.route('/client/envies/up', methods=['get'])
@client_liste_envies.route('/client/envies/down', methods=['get'])
@client_liste_envies.route('/client/envies/last', methods=['get'])
@client_liste_envies.route('/client/envies/first', methods=['get'])
@client_liste_envies.route('/client/envies/up', methods=['get'])
def up_envie():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')

    sql = """
    UPDATE wishlist SET date_ajout = NOW()
    WHERE utilisateur_id = %s AND id_velo = %s
    """
    mycursor.execute(sql, (id_client, id_article))
    get_db().commit()

    return redirect('/client/envies/show')
@client_liste_envies.route('/client/envies/down', methods=['get'])
def down_envie():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')

    sql = """
    UPDATE wishlist 
    SET date_ajout = DATE_SUB(NOW(), INTERVAL 1 DAY)
    WHERE utilisateur_id = %s AND id_velo = %s
    """
    mycursor.execute(sql, (id_client, id_article))
    get_db().commit()

    return redirect('/client/envies/show')
