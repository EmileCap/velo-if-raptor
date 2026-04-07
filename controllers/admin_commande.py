#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, flash, session

from connexion_db import get_db

admin_commande = Blueprint('admin_commande', __name__,
                           template_folder='templates')


@admin_commande.route('/admin')
@admin_commande.route('/admin/commande/index')
def admin_index():
    return render_template('admin/layout_admin.html')


@admin_commande.route('/admin/commande/show', methods=['GET', 'POST'])
def admin_commande_show():
    mycursor = get_db().cursor()

    sql = """
    SELECT c.id_commande, u.login, c.date_achat, c.etat_id, e.libelle_etat AS libelle,
           COUNT(lc.id_declinaison)       AS nbr_articles,
           SUM(lc.prix * lc.quantite)     AS prix_total
    FROM commande c
    INNER JOIN utilisateur u      ON u.id_utilisateur = c.utilisateur_id
    INNER JOIN ligne_commande lc  ON lc.commande_id = c.id_commande
    INNER JOIN etat e             ON e.id_etat = c.etat_id
    GROUP BY c.id_commande, u.login, c.date_achat, c.etat_id, e.libelle_etat
    ORDER BY c.etat_id ASC, c.date_achat DESC
    """
    mycursor.execute(sql)
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
        WHERE lc.commande_id = %s
        """
        mycursor.execute(sql_detail, (id_commande,))
        articles_commande = mycursor.fetchall()

    return render_template('admin/commandes/show.html',
                           commandes=commandes,
                           articles_commande=articles_commande,
                           commande_adresses=None)


@admin_commande.route('/admin/commande/valider', methods=['GET', 'POST'])
def admin_commande_valider():
    mycursor = get_db().cursor()
    commande_id = request.form.get('id_commande', None)
    if commande_id is not None:
        mycursor.execute("UPDATE commande SET etat_id = 2 WHERE id_commande = %s", (commande_id,))
        get_db().commit()
        flash("Commande expédiée.", "alert-success")
    return redirect('/admin/commande/show')
