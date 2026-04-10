#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template

from connexion_db import get_db

admin_dataviz = Blueprint('admin_dataviz', __name__,
                          template_folder='templates')


@admin_dataviz.route('/admin/dataviz/etat1')
def show_type_article_stock():
    mycursor = get_db().cursor()

    mycursor.execute("""
        SELECT c.libelle_couleur AS libelle,
               SUM(d.stock) AS nb_stock,
               SUM(d.stock * COALESCE(d.prix_declinaison, v.prix_velo)) AS cout_stock
        FROM declinaison d
        INNER JOIN couleur c ON c.id_couleur = d.id_couleur
        INNER JOIN Velo v    ON v.id_velo    = d.id_velo
        WHERE d.valide = 1
        GROUP BY c.id_couleur, c.libelle_couleur
        ORDER BY cout_stock DESC
    """)
    stats_couleur = mycursor.fetchall()

    mycursor.execute("""
        SELECT t.libelle_taille AS libelle,
               SUM(d.stock) AS nb_stock,
               SUM(d.stock * COALESCE(d.prix_declinaison, v.prix_velo)) AS cout_stock
        FROM declinaison d
        INNER JOIN taille t ON t.id_taille = d.id_taille
        INNER JOIN Velo v   ON v.id_velo   = d.id_velo
        WHERE d.valide = 1
        GROUP BY t.id_taille, t.libelle_taille
        ORDER BY t.id_taille ASC
    """)
    stats_taille = mycursor.fetchall()

    mycursor.execute("""
        SELECT v.nom_velo AS nom, v.id_velo,
               COUNT(d.id_declinaison) AS nb_declinaisons,
               COALESCE(SUM(d.stock), 0) AS stock_total,
               SUM(d.stock * COALESCE(d.prix_declinaison, v.prix_velo)) AS cout_stock,
               MIN(d.stock) AS min_stock
        FROM Velo v
        LEFT JOIN declinaison d ON d.id_velo = v.id_velo AND d.valide = 1
        GROUP BY v.id_velo, v.nom_velo
        ORDER BY cout_stock DESC
    """)
    articles = mycursor.fetchall()

    labels_couleur = [r['libelle'] for r in stats_couleur]
    values_nb_couleur = [int(r['nb_stock']) for r in stats_couleur]
    values_cout_couleur = [int(r['cout_stock']) for r in stats_couleur]

    labels_taille = [r['libelle'] for r in stats_taille]
    values_nb_taille = [int(r['nb_stock']) for r in stats_taille]
    values_cout_taille = [int(r['cout_stock']) for r in stats_taille]

    return render_template('admin/dataviz/dataviz_etat_1.html',
                           stats_couleur=stats_couleur,
                           labels_couleur=labels_couleur,
                           values_nb_couleur=values_nb_couleur,
                           values_cout_couleur=values_cout_couleur,
                           stats_taille=stats_taille,
                           labels_taille=labels_taille,
                           values_nb_taille=values_nb_taille,
                           values_cout_taille=values_cout_taille,
                           articles=articles)


@admin_dataviz.route('/admin/dataviz/etat2')
def show_dataviz_map():
    mycursor = get_db().cursor()

    mycursor.execute("""
        SELECT LEFT(a.code_postal, 2) AS departement,
               COUNT(c.id_commande) AS nb_ventes,
               SUM(lc.prix * lc.quantite) AS chiffre_affaires
        FROM commande c
        INNER JOIN adresse a ON a.id_adresse = c.id_adresse_livraison
        INNER JOIN ligne_commande lc ON lc.commande_id = c.id_commande
        GROUP BY LEFT(a.code_postal, 2)
        ORDER BY nb_ventes DESC
    """)
    stats_dep = mycursor.fetchall()

    labels = [r['departement'] for r in stats_dep]
    values_ventes = [int(r['nb_ventes']) for r in stats_dep]
    values_ca = [int(r['chiffre_affaires']) if r['chiffre_affaires'] else 0 for r in stats_dep]

    return render_template('admin/dataviz/dataviz_etat_map.html',
                           stats_dep=stats_dep,
                           labels=labels,
                           values_ventes=values_ventes,
                           values_ca=values_ca
                           )
