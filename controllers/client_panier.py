#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, flash, session

from connexion_db import get_db

client_panier = Blueprint('client_panier', __name__,
                          template_folder='templates')


@client_panier.route('/client/panier/declinaison', methods=['GET'])
def client_panier_declinaison():
    mycursor = get_db().cursor()
    id_article = request.args.get('id_article')

    sql_nb = """
        SELECT COUNT(*) AS nb FROM declinaison
        WHERE id_velo = %s AND valide = 1
    """
    mycursor.execute(sql_nb, (id_article,))
    nb = mycursor.fetchone()['nb']

    if nb == 1:
        sql_id = "SELECT id_declinaison FROM declinaison WHERE id_velo = %s AND valide = 1"
        mycursor.execute(sql_id, (id_article,))
        decl = mycursor.fetchone()
        return redirect('/client/panier/add?id_declinaison=' + str(decl['id_declinaison']) + '&quantite=1')

    sql_article = """
        SELECT v.id_velo AS id_article, v.nom_velo AS nom, v.photo_velo AS image,
               MIN(COALESCE(d.prix_declinaison, v.prix_velo)) AS prix
        FROM Velo v
        LEFT JOIN declinaison d ON d.id_velo = v.id_velo AND d.valide = 1
        WHERE v.id_velo = %s
        GROUP BY v.id_velo, v.nom_velo, v.photo_velo
    """
    mycursor.execute(sql_article, (id_article,))
    article = mycursor.fetchone()

    sql_decl = """
        SELECT d.id_declinaison, d.stock,
               COALESCE(d.prix_declinaison, v.prix_velo) AS prix,
               t.id_taille, t.libelle_taille,
               c.id_couleur, c.libelle_couleur, c.code_couleur
        FROM declinaison d
        INNER JOIN Velo v    ON v.id_velo = d.id_velo
        INNER JOIN taille t  ON t.id_taille = d.id_taille
        INNER JOIN couleur c ON c.id_couleur = d.id_couleur
        WHERE d.id_velo = %s AND d.valide = 1
        ORDER BY d.id_declinaison
    """
    mycursor.execute(sql_decl, (id_article,))
    declinaisons = mycursor.fetchall()

    return render_template('client/boutique/declinaison_article.html',
                           article=article,
                           declinaisons=declinaisons)


@client_panier.route('/client/panier/add', methods=['GET', 'POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    if request.method == 'POST':
        id_declinaison = request.form.get('id_declinaison')
        quantite = int(request.form.get('quantite', 1))
    else:
        id_declinaison = request.args.get('id_declinaison')
        quantite = int(request.args.get('quantite', 1))

    if not id_declinaison:
        flash("Déclinaison manquante.", "alert-danger")
        return redirect('/client/article/show')

    sql_stock = "SELECT stock, id_velo FROM declinaison WHERE id_declinaison = %s AND valide = 1"
    mycursor.execute(sql_stock, (id_declinaison,))
    decl = mycursor.fetchone()

    if decl is None or decl['stock'] < quantite:
        flash("Stock insuffisant pour cette déclinaison.", "alert-danger")
        return redirect('/client/article/show')

    id_velo = decl['id_velo']

    sql_check = """
        SELECT quantite FROM ligne_panier
        WHERE utilisateur_id = %s AND id_declinaison = %s
    """
    mycursor.execute(sql_check, (id_client, id_declinaison))
    ligne = mycursor.fetchone()

    if ligne:
        mycursor.execute(
            "UPDATE ligne_panier SET quantite = quantite + %s WHERE utilisateur_id = %s AND id_declinaison = %s",
            (quantite, id_client, id_declinaison)
        )
    else:
        mycursor.execute(
            "INSERT INTO ligne_panier (utilisateur_id, id_declinaison, quantite, date_ajout) VALUES (%s, %s, %s, CURDATE())",
            (id_client, id_declinaison, quantite)
        )

    mycursor.execute(
        "UPDATE declinaison SET stock = stock - %s WHERE id_declinaison = %s",
        (quantite, id_declinaison)
    )
    mycursor.execute(
        "UPDATE Velo SET stock_velo = (SELECT COALESCE(SUM(d.stock),0) FROM declinaison d WHERE d.id_velo = Velo.id_velo AND d.valide = 1) WHERE id_velo = %s",
        (id_velo,)
    )

    get_db().commit()
    flash("Article ajouté au panier.", "alert-success")
    return redirect('/client/article/show')


@client_panier.route('/client/panier/delete', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_declinaison = request.form.get('id_declinaison', '')

    sql = """
        SELECT lp.quantite, d.id_velo FROM ligne_panier lp
        INNER JOIN declinaison d ON d.id_declinaison = lp.id_declinaison
        WHERE lp.utilisateur_id = %s AND lp.id_declinaison = %s
    """
    mycursor.execute(sql, (id_client, id_declinaison))
    ligne = mycursor.fetchone()

    if ligne is None:
        return redirect('/client/article/show')

    id_velo = ligne['id_velo']

    if ligne['quantite'] > 1:
        mycursor.execute(
            "UPDATE ligne_panier SET quantite = quantite - 1 WHERE utilisateur_id = %s AND id_declinaison = %s",
            (id_client, id_declinaison)
        )
    else:
        mycursor.execute(
            "DELETE FROM ligne_panier WHERE utilisateur_id = %s AND id_declinaison = %s",
            (id_client, id_declinaison)
        )

    mycursor.execute("UPDATE declinaison SET stock = stock + 1 WHERE id_declinaison = %s", (id_declinaison,))
    mycursor.execute(
        "UPDATE Velo SET stock_velo = (SELECT COALESCE(SUM(d.stock),0) FROM declinaison d WHERE d.id_velo = Velo.id_velo AND d.valide = 1) WHERE id_velo = %s",
        (id_velo,)
    )
    get_db().commit()
    return redirect('/client/article/show')


@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_declinaison = request.form.get('id_declinaison', '')

    sql = """
        SELECT lp.quantite, d.id_velo FROM ligne_panier lp
        INNER JOIN declinaison d ON d.id_declinaison = lp.id_declinaison
        WHERE lp.utilisateur_id = %s AND lp.id_declinaison = %s
    """
    mycursor.execute(sql, (id_client, id_declinaison))
    ligne = mycursor.fetchone()

    if ligne:
        id_velo = ligne['id_velo']
        mycursor.execute(
            "DELETE FROM ligne_panier WHERE utilisateur_id = %s AND id_declinaison = %s",
            (id_client, id_declinaison)
        )
        mycursor.execute(
            "UPDATE declinaison SET stock = stock + %s WHERE id_declinaison = %s",
            (ligne['quantite'], id_declinaison)
        )
        mycursor.execute(
            "UPDATE Velo SET stock_velo = (SELECT COALESCE(SUM(d.stock),0) FROM declinaison d WHERE d.id_velo = Velo.id_velo AND d.valide = 1) WHERE id_velo = %s",
            (id_velo,)
        )
        get_db().commit()

    return redirect('/client/article/show')


@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = """
        SELECT lp.id_declinaison, lp.quantite, d.id_velo
        FROM ligne_panier lp
        INNER JOIN declinaison d ON d.id_declinaison = lp.id_declinaison
        WHERE lp.utilisateur_id = %s
    """
    mycursor.execute(sql, (id_client,))
    items = mycursor.fetchall()

    for item in items:
        mycursor.execute(
            "DELETE FROM ligne_panier WHERE utilisateur_id = %s AND id_declinaison = %s",
            (id_client, item['id_declinaison'])
        )
        mycursor.execute(
            "UPDATE declinaison SET stock = stock + %s WHERE id_declinaison = %s",
            (item['quantite'], item['id_declinaison'])
        )
        mycursor.execute(
            "UPDATE Velo SET stock_velo = (SELECT COALESCE(SUM(d.stock),0) FROM declinaison d WHERE d.id_velo = Velo.id_velo AND d.valide = 1) WHERE id_velo = %s",
            (item['id_velo'],)
        )

    get_db().commit()
    return redirect('/client/article/show')


@client_panier.route('/client/panier/filtre', methods=['POST'])
def client_panier_filtre():
    session['filter_word'] = request.form.get('filter_word', None)
    session['filter_prix_min'] = request.form.get('filter_prix_min', None)
    session['filter_prix_max'] = request.form.get('filter_prix_max', None)
    session['filter_types'] = request.form.getlist('filter_types')
    return redirect('/client/article/show')


@client_panier.route('/client/panier/filtre/suppr', methods=['POST'])
def client_panier_filtre_suppr():
    session.pop('filter_word', None)
    session.pop('filter_prix_min', None)
    session.pop('filter_prix_max', None)
    session.pop('filter_types', None)
    return redirect('/client/article/show')
