#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_commande = Blueprint('admin_commande', __name__,
                        template_folder='templates')

@admin_commande.route('/admin')
@admin_commande.route('/admin/commande/index')
def admin_index():
    return render_template('admin/layout_admin.html')


@admin_commande.route('/admin/commande/show', methods=['get','post'])
def admin_commande_show():
    mycursor = get_db().cursor()
    admin_id = session['id_user']
    sql = ''' 
    SELECT 
        commande.id_commande,
        utilisateur.login,
        commande.date_achat,
        COUNT(ligne_commande.article_id) AS nbr_articles,
        SUM(ligne_commande.quantite) AS prix_total,
        etat.libelle_etat AS libelle
    FROM commande
    INNER JOIN utilisateur 
        ON commande.utilisateur_id = utilisateur.id_utilisateur
    INNER JOIN ligne_commande 
        ON commande.id_commande = ligne_commande.commande_id
    INNER JOIN etat 
        ON commande.etat_id = etat.id_etat
    GROUP BY 
        commande.id_commande,
        utilisateur.login,
        commande.date_achat,
        etat.libelle_etat;
    '''

    mycursor.execute(sql)

    commandes= mycursor.fetchall()

    articles_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)
    print(id_commande)
    if id_commande != None:

        sql = '''
    SELECT nom_velo as nom, quantite, prix, SUM(prix*quantite) AS prix_ligne
    FROM commande
    INNER JOIN ligne_commande ON id_commande = commande_id
    INNER JOIN Velo ON article_id = id_velo
    WHERE id_commande = %s
    GROUP BY id_velo, nom_velo, quantite, prix;
    '''
        mycursor.execute(sql, id_commande)
        articles_commande = mycursor.fetchall()
        

        sql = '''    '''
        commande_adresses = []
    return render_template('admin/commandes/show.html'
                           , commandes=commandes
                           , articles_commande=articles_commande
                           , commande_adresses=commande_adresses
                           )


@admin_commande.route('/admin/commande/valider', methods=['get','post'])
def admin_commande_valider():
    mycursor = get_db().cursor()
    commande_id = request.form.get('id_commande', None)
    if commande_id != None:
        print(commande_id)
        sql = '''           '''
        mycursor.execute(sql, commande_id)
        get_db().commit()
    return redirect('/admin/commande/show')
