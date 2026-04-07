#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, flash, session
from datetime import datetime
from connexion_db import get_db

client_commande = Blueprint('client_commande', __name__,
                            template_folder='templates')


@client_commande.route('/client/commande/valide', methods=['POST'])
def client_commande_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = """
        SELECT lp.id_declinaison, v.nom_velo AS nom, v.photo_velo,
               COALESCE(d.prix_declinaison, v.prix_velo) AS prix,
               lp.quantite,
               t.libelle_taille, d.id_taille,
               c.libelle_couleur, d.id_couleur
        FROM ligne_panier lp
        INNER JOIN declinaison d ON d.id_declinaison = lp.id_declinaison
        INNER JOIN Velo v        ON v.id_velo = d.id_velo
        INNER JOIN taille t      ON t.id_taille = d.id_taille
        INNER JOIN couleur c     ON c.id_couleur = d.id_couleur
        WHERE lp.utilisateur_id = %s
    """
    mycursor.execute(sql, (id_client,))
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
    prix_total = row['total'] if row else None

    return render_template('client/boutique/panier_validation_adresses.html',
                           articles_panier=articles_panier,
                           prix_total=prix_total,
                           validation=1)


@client_commande.route('/client/commande/add', methods=['POST'])
def client_commande_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = """
        SELECT lp.id_declinaison, lp.quantite,
               COALESCE(d.prix_declinaison, v.prix_velo) AS prix
        FROM ligne_panier lp
        INNER JOIN declinaison d ON d.id_declinaison = lp.id_declinaison
        INNER JOIN Velo v        ON v.id_velo = d.id_velo
        WHERE lp.utilisateur_id = %s
    """
    mycursor.execute(sql, (id_client,))
    items = mycursor.fetchall()

    if not items:
        flash("Votre panier est vide.", "alert-warning")
        return redirect('/client/article/show')

    date_achat = datetime.now().strftime('%Y-%m-%d')
    mycursor.execute(
        "INSERT INTO commande (date_achat, utilisateur_id, etat_id) VALUES (%s, %s, 1)",
        (date_achat, id_client)
    )
    mycursor.execute("SELECT LAST_INSERT_ID() AS last_id")
    id_commande = mycursor.fetchone()['last_id']

    for item in items:
        mycursor.execute(
            "DELETE FROM ligne_panier WHERE utilisateur_id = %s AND id_declinaison = %s",
            (id_client, item['id_declinaison'])
        )
        mycursor.execute(
            "INSERT INTO ligne_commande (commande_id, id_declinaison, prix, quantite) VALUES (%s, %s, %s, %s)",
            (id_commande, item['id_declinaison'], item['prix'], item['quantite'])
        )

    get_db().commit()
    flash("Commande passée avec succès !", "alert-success")
    return redirect('/client/article/show')


@client_commande.route('/client/commande/show', methods=['GET', 'POST'])
def client_commande_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = """
        SELECT c.id_commande, c.date_achat, c.etat_id, e.libelle_etat AS libelle,
               COUNT(lc.id_declinaison)          AS nbr_articles,
               SUM(lc.prix * lc.quantite)         AS prix_total
        FROM commande c
        INNER JOIN etat e            ON e.id_etat = c.etat_id
        INNER JOIN ligne_commande lc ON lc.commande_id = c.id_commande
        WHERE c.utilisateur_id = %s
        GROUP BY c.id_commande, c.date_achat, c.etat_id, e.libelle_etat
        ORDER BY c.etat_id ASC, c.date_achat DESC
    """
    mycursor.execute(sql, (id_client,))
    commandes = mycursor.fetchall()

    articles_commande = None
    id_commande = request.args.get('id_commande', None)

    if id_commande is not None:
        sql_detail = """
            SELECT v.nom_velo AS nom, lc.quantite, lc.prix,
                   lc.prix * lc.quantite AS prix_ligne,
                   d.id_taille, t.libelle_taille,
                   d.id_couleur, c2.libelle_couleur,
                   (SELECT COUNT(*) FROM declinaison d2
                    WHERE d2.id_velo = v.id_velo AND d2.valide = 1) AS nb_declinaisons
            FROM ligne_commande lc
            INNER JOIN declinaison d  ON d.id_declinaison = lc.id_declinaison
            INNER JOIN Velo v         ON v.id_velo = d.id_velo
            INNER JOIN taille t       ON t.id_taille = d.id_taille
            INNER JOIN couleur c2     ON c2.id_couleur = d.id_couleur
            INNER JOIN commande co    ON co.id_commande = lc.commande_id
            WHERE lc.commande_id = %s AND co.utilisateur_id = %s
        """
        mycursor.execute(sql_detail, (id_commande, id_client))
        articles_commande = mycursor.fetchall()

    return render_template('client/commandes/show.html',
                           commandes=commandes,
                           articles_commande=articles_commande,
                           commande_adresses=None)
