#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from datetime import datetime
from connexion_db import get_db

client_commande = Blueprint('client_commande', __name__,
                        template_folder='templates')


# validation de la commande : partie 2 -- vue pour choisir les adresses (livraison et facturation)
@client_commande.route('/client/commande/valide', methods=['POST'])
def client_commande_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Sélection des articles du panier de lutilisateur connecté
    sql = '''
        SELECT lp.article_id, lp.quantite, v.nom_velo, v.prix_velo AS prix, v.photo_velo
        FROM ligne_panier lp
        JOIN Velo v ON lp.article_id = v.id_velo
        WHERE lp.utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_client,))
    articles_panier = mycursor.fetchall()

    if len(articles_panier) >= 1:
        # requete du calcul du prix total du panier du client
        sql = '''
            SELECT SUM(v.prix_velo * lp.quantite) AS total
            FROM ligne_panier lp
            JOIN Velo v ON lp.article_id = v.id_velo
            WHERE lp.utilisateur_id = %s
        '''
        mycursor.execute(sql, (id_client,))
        row = mycursor.fetchone()
        prix_total = row['total'] if row else 0
    else:
        prix_total = None

    return render_template('client/boutique/panier_validation_adresses.html',
                           articles_panier=articles_panier,
                           prix_total=prix_total,
                           validation=1)


@client_commande.route('/client/commande/add', methods=['POST'])
def client_commande_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Sélection du contenu du panier de l'utilisateur
    sql = '''
        SELECT lp.article_id, lp.quantite, v.prix_velo
        FROM ligne_panier lp
        JOIN Velo v ON lp.article_id = v.id_velo
        WHERE lp.utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_client,))
    items_ligne_panier = mycursor.fetchall()

    if items_ligne_panier is None or len(items_ligne_panier) < 1:
        flash(u'Pas d\'articles dans le panier', 'alert-warning')
        return redirect('/client/article/show')

    # Création de la commande
    date_achat = datetime.now().strftime('%Y-%m-%d')
    sql = '''
        INSERT INTO commande (date_achat, utilisateur_id, etat_id)
        VALUES (%s, %s, %s)
    '''
    # etat_id = 2 => "En cours"
    mycursor.execute(sql, (date_achat, id_client, 2))

    # Récupération du dernier id_commande inséré
    sql = '''SELECT last_insert_id() as last_insert_id'''
    mycursor.execute(sql)
    row = mycursor.fetchone()
    last_id_commande = row['last_insert_id']

    for item in items_ligne_panier:
        # Suppression de la ligne de panier
        sql = '''
            DELETE FROM ligne_panier
            WHERE utilisateur_id = %s AND article_id = %s
        '''
        mycursor.execute(sql, (id_client, item['article_id']))

        # Ajout d'une ligne de commande
        sql = '''
            INSERT INTO ligne_commande (commande_id, article_id, prix, quantite)
            VALUES (%s, %s, %s, %s)
        '''
        mycursor.execute(sql, (last_id_commande, item['article_id'], item['prix_velo'], item['quantite']))

    get_db().commit()
    flash(u'Commande ajoutée', 'alert-success')
    return redirect('/client/article/show')


@client_commande.route('/client/commande/show', methods=['GET', 'POST'])
def client_commande_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = '''
        SELECT c.id_commande, c.date_achat, e.libelle_etat, e.id_etat,
               (SELECT SUM(lc.prix * lc.quantite)
                FROM ligne_commande lc
                WHERE lc.commande_id = c.id_commande) AS prix_total
        FROM commande c
        JOIN etat e ON c.etat_id = e.id_etat
        WHERE c.utilisateur_id = %s
        ORDER BY e.id_etat ASC, c.date_achat DESC
    '''
    mycursor.execute(sql, (id_client,))
    commandes = mycursor.fetchall()

    articles_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)

    if id_commande is not None:
        print(id_commande)

        sql = '''
            SELECT lc.article_id, lc.prix, lc.quantite,
                   v.nom_velo, v.photo_velo,
                   (lc.prix * lc.quantite) AS sous_total
            FROM ligne_commande lc
            JOIN Velo v ON lc.article_id = v.id_velo
            WHERE lc.commande_id = %s
        '''
        mycursor.execute(sql, (id_commande,))
        articles_commande = mycursor.fetchall()

        commande_adresses = None

    return render_template('client/commandes/show.html',
                           commandes=commandes,
                           articles_commande=articles_commande,
                           commande_adresses=commande_adresses)
