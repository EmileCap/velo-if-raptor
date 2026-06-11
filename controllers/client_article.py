#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, flash, session

from connexion_db import get_db

client_article = Blueprint('client_article', __name__,
                           template_folder='templates')


@client_article.route('/client/index')
@client_article.route('/client/article/show')
def client_article_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    #on ajoute les notes des vélos et les commentaire aux articles
    sql = """
    SELECT
        v.id_velo    AS id_article,
        v.nom_velo   AS nom,
        v.photo_velo AS image,
        v.id_type    AS id_type,
        t.libelle_type,
        COUNT(DISTINCT d.id_declinaison) AS nb_declinaisons,
        COALESCE(SUM(DISTINCT d.stock), 0) AS stock,
        MIN(COALESCE(d.prix_declinaison, v.prix_velo)) AS prix,
        AVG(n.note) AS moyenne_notes,
        COUNT(DISTINCT n.id_utilisateur) AS nb_notes,
        COUNT(DISTINCT c.id_commentaire) AS nb_commentaires
    FROM Velo v
    INNER JOIN type t ON v.id_type = t.id_type
    LEFT  JOIN declinaison d ON d.id_velo = v.id_velo
    LEFT  JOIN note n ON n.id_velo = v.id_velo
    LEFT  JOIN commentaire c ON c.id_velo = v.id_velo AND c.id_commentaire_parent IS NULL
    WHERE 1=1
    """
    params = []

    filter_word = session.get('filter_word', None)
    if filter_word:
        sql += " AND v.nom_velo LIKE %s"
        params.append(f"%{filter_word}%")

    filter_types = session.get('filter_types', [])
    if filter_types:
        placeholders = ', '.join(['%s'] * len(filter_types))
        sql += f" AND v.id_type IN ({placeholders})"
        params.extend(filter_types)

    filter_prix_min = session.get('filter_prix_min', None)
    if filter_prix_min:
        sql += " AND v.prix_velo >= %s"
        params.append(filter_prix_min)

    filter_prix_max = session.get('filter_prix_max', None)
    if filter_prix_max:
        sql += " AND v.prix_velo <= %s"
        params.append(filter_prix_max)

    sql += " GROUP BY v.id_velo, v.nom_velo, v.photo_velo, v.id_type, t.libelle_type"

    mycursor.execute(sql, params)
    articles = mycursor.fetchall()

    sql2 = "SELECT id_type AS id_type_article, libelle_type FROM type"
    mycursor.execute(sql2)
    types_article = mycursor.fetchall()

    sql_panier = """
        SELECT
            lp.id_declinaison,
            v.id_velo  AS id_article,
            v.nom_velo AS nom,
            COALESCE(d.prix_declinaison, v.prix_velo) AS prix,
            d.stock,
            lp.quantite,
            t2.libelle_taille,
            d.id_taille,
            c.libelle_couleur,
            d.id_couleur
        FROM ligne_panier lp
        INNER JOIN declinaison d ON d.id_declinaison = lp.id_declinaison
        INNER JOIN Velo v        ON v.id_velo = d.id_velo
        INNER JOIN taille t2     ON t2.id_taille = d.id_taille
        INNER JOIN couleur c     ON c.id_couleur = d.id_couleur
        WHERE lp.utilisateur_id = %s
    """
    mycursor.execute(sql_panier, (id_client,))
    articles_panier = mycursor.fetchall()

    sql_total = """
        SELECT COALESCE(SUM(COALESCE(d.prix_declinaison, v.prix_velo) * lp.quantite), 0) AS total
        FROM ligne_panier lp
        INNER JOIN declinaison d ON d.id_declinaison = lp.id_declinaison
        INNER JOIN Velo v        ON v.id_velo = d.id_velo
        WHERE lp.utilisateur_id = %s
    """
    mycursor.execute(sql_total, (id_client,))
    row = mycursor.fetchone()
    prix_total = row['total'] if row and row['total'] else None

    return render_template('client/boutique/panier_article.html',
                           articles=articles,
                           articles_panier=articles_panier,
                           prix_total=prix_total,
                           items_filtre=types_article)
