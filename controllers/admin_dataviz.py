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
    adresses = [{'dep': '25', 'nombre': 1}, {'dep': '83', 'nombre': 1}, {'dep': '90', 'nombre': 3}]
    return render_template('admin/dataviz/dataviz_etat_map.html', adresses=adresses)


@admin_dataviz.route('/admin/dataviz/commentaires')
def show_dataviz_commentaires():
    mycursor = get_db().cursor()

    mycursor.execute("""
        SELECT t.id_type, t.libelle_type,
               COUNT(DISTINCT n.id_utilisateur) AS nb_notes,
               AVG(n.note)                       AS moyenne_notes,
               COUNT(DISTINCT CASE WHEN c.id_commentaire_parent IS NULL
                                   THEN c.id_commentaire END) AS nb_commentaires
        FROM type t
        LEFT JOIN Velo v ON v.id_type = t.id_type
        LEFT JOIN note n ON n.id_velo = v.id_velo
        LEFT JOIN commentaire c ON c.id_velo = v.id_velo
        GROUP BY t.id_type, t.libelle_type
        ORDER BY t.id_type
    """)
    stats_types = mycursor.fetchall()

    id_type_sel = request.args.get('id_type', None)
    stats_articles = []
    libelle_type_sel = None

    if id_type_sel:
        mycursor.execute("""
            SELECT v.id_velo, v.nom_velo,
                   COUNT(DISTINCT n.id_utilisateur) AS nb_notes,
                   AVG(n.note)                       AS moyenne_notes,
                   COUNT(DISTINCT CASE WHEN c.id_commentaire_parent IS NULL
                                       THEN c.id_commentaire END) AS nb_commentaires
            FROM Velo v
            LEFT JOIN note n ON n.id_velo = v.id_velo
            LEFT JOIN commentaire c ON c.id_velo = v.id_velo
            WHERE v.id_type = %s
            GROUP BY v.id_velo, v.nom_velo
            ORDER BY v.nom_velo
        """, (id_type_sel,))
        stats_articles = mycursor.fetchall()

        mycursor.execute("SELECT libelle_type FROM type WHERE id_type = %s", (id_type_sel,))
        row = mycursor.fetchone()
        libelle_type_sel = row['libelle_type'] if row else ''

    labels_types  = [r['libelle_type'] for r in stats_types]
    values_moy    = [round(float(r['moyenne_notes']), 2) if r['moyenne_notes'] else 0 for r in stats_types]
    values_com    = [int(r['nb_commentaires']) for r in stats_types]
    values_notes  = [int(r['nb_notes']) for r in stats_types]

    labels_arts      = [r['nom_velo'] for r in stats_articles]
    values_art_moy   = [round(float(r['moyenne_notes']), 2) if r['moyenne_notes'] else 0 for r in stats_articles]
    values_art_com   = [int(r['nb_commentaires']) for r in stats_articles]
    values_art_notes = [int(r['nb_notes']) for r in stats_articles]

    return render_template('admin/dataviz/dataviz_commentaires.html',
                           stats_types=stats_types,
                           stats_articles=stats_articles,
                           id_type_sel=id_type_sel,
                           libelle_type_sel=libelle_type_sel,
                           labels_types=labels_types,
                           values_moy=values_moy,
                           values_com=values_com,
                           values_notes=values_notes,
                           labels_arts=labels_arts,
                           values_art_moy=values_art_moy,
                           values_art_com=values_art_com,
                           values_art_notes=values_art_notes)
