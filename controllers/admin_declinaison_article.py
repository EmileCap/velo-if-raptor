#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, flash
from connexion_db import get_db

admin_declinaison_article = Blueprint('admin_declinaison_article', __name__,
                                      template_folder='templates')


def _options_disponibles(mycursor, id_article, exclude_id=None):
    if exclude_id:
        mycursor.execute(
            "SELECT id_taille, id_couleur FROM declinaison WHERE id_velo = %s AND valide = 1 AND id_declinaison != %s",
            (id_article, exclude_id)
        )
    else:
        mycursor.execute(
            "SELECT id_taille, id_couleur FROM declinaison WHERE id_velo = %s AND valide = 1",
            (id_article,)
        )
    existantes = mycursor.fetchall()

    has_taille_unique = any(d['id_taille'] == 1 for d in existantes)
    has_other_taille = any(d['id_taille'] != 1 for d in existantes)
    has_couleur_unique = any(d['id_couleur'] == 1 for d in existantes)
    has_other_couleur = any(d['id_couleur'] != 1 for d in existantes)

    if has_taille_unique:
        tailles = []
        d_taille_uniq = 1
    elif has_other_taille:
        mycursor.execute("SELECT id_taille, libelle_taille AS libelle FROM taille WHERE id_taille != 1")
        tailles = mycursor.fetchall()
        d_taille_uniq = 0
    else:
        mycursor.execute("SELECT id_taille, libelle_taille AS libelle FROM taille")
        tailles = mycursor.fetchall()
        d_taille_uniq = 0

    if has_couleur_unique:
        couleurs = []
        d_couleur_uniq = 1
    elif has_other_couleur:
        mycursor.execute("SELECT id_couleur, libelle_couleur AS libelle FROM couleur WHERE id_couleur != 1")
        couleurs = mycursor.fetchall()
        d_couleur_uniq = 0
    else:
        mycursor.execute("SELECT id_couleur, libelle_couleur AS libelle FROM couleur")
        couleurs = mycursor.fetchall()
        d_couleur_uniq = 0

    return tailles, couleurs, d_taille_uniq, d_couleur_uniq


@admin_declinaison_article.route('/admin/declinaison_article/add', methods=['GET'])
def add_declinaison_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()

    mycursor.execute(
        "SELECT id_velo AS id_article, nom_velo AS nom, photo_velo AS image, prix_velo AS prix FROM Velo WHERE id_velo = %s",
        (id_article,)
    )
    article = mycursor.fetchone()

    tailles, couleurs, d_taille_uniq, d_couleur_uniq = _options_disponibles(mycursor, id_article)

    return render_template('admin/article/add_declinaison_article.html',
                           article=article,
                           couleurs=couleurs,
                           tailles=tailles,
                           d_taille_uniq=d_taille_uniq,
                           d_couleur_uniq=d_couleur_uniq)


@admin_declinaison_article.route('/admin/declinaison_article/add', methods=['POST'])
def valid_add_declinaison_article():
    mycursor = get_db().cursor()
    id_article = request.form.get('id_article')
    stock = request.form.get('stock', 0)
    id_taille = request.form.get('taille')
    id_couleur = request.form.get('couleur')
    prix_declinaison = request.form.get('prix_declinaison') or None

    mycursor.execute(
        "SELECT id_declinaison FROM declinaison WHERE id_velo = %s AND id_taille = %s AND id_couleur = %s AND valide = 1",
        (id_article, id_taille, id_couleur)
    )
    if mycursor.fetchone():
        flash("Cette combinaison taille/couleur existe déjà.", "alert-warning")
        return redirect('/admin/declinaison_article/add?id_article=' + str(id_article))

    mycursor.execute(
        "INSERT INTO declinaison (id_taille, id_couleur, stock, id_velo, prix_declinaison, valide) VALUES (%s, %s, %s, %s, %s, 1)",
        (id_taille, id_couleur, stock, id_article, prix_declinaison)
    )
    mycursor.execute(
        "UPDATE Velo SET stock_velo = (SELECT COALESCE(SUM(d.stock),0) FROM declinaison d WHERE d.id_velo = Velo.id_velo AND d.valide = 1) WHERE id_velo = %s",
        (id_article,)
    )
    get_db().commit()
    flash("Déclinaison ajoutée.", "alert-success")
    return redirect('/admin/article/edit?id_article=' + str(id_article))


@admin_declinaison_article.route('/admin/declinaison_article/edit', methods=['GET'])
def edit_declinaison_article():
    id_declinaison = request.args.get('id_declinaison_article')
    mycursor = get_db().cursor()

    mycursor.execute("""
        SELECT d.id_declinaison AS id_declinaison_article, d.id_velo AS article_id,
               d.id_taille, d.id_couleur, d.stock, d.prix_declinaison,
               v.nom_velo AS nom, v.photo_velo AS image_article
        FROM declinaison d INNER JOIN Velo v ON v.id_velo = d.id_velo
        WHERE d.id_declinaison = %s
    """, (id_declinaison,))
    declinaison_article = mycursor.fetchone()

    id_article = declinaison_article['article_id']
    tailles, couleurs, d_taille_uniq, d_couleur_uniq = _options_disponibles(mycursor, id_article, exclude_id=int(id_declinaison))

    return render_template('admin/article/edit_declinaison_article.html',
                           tailles=tailles,
                           couleurs=couleurs,
                           declinaison_article=declinaison_article,
                           d_taille_uniq=d_taille_uniq,
                           d_couleur_uniq=d_couleur_uniq)


@admin_declinaison_article.route('/admin/declinaison_article/edit', methods=['POST'])
def valid_edit_declinaison_article():
    mycursor = get_db().cursor()
    id_declinaison = request.form.get('id_declinaison_article', '')
    id_article = request.form.get('id_article', '')
    stock = request.form.get('stock', '')
    id_taille = request.form.get('taille', '')
    id_couleur = request.form.get('couleur', '')
    prix_declinaison = request.form.get('prix_declinaison') or None

    mycursor.execute("SELECT COUNT(*) AS nb FROM ligne_commande WHERE id_declinaison = %s", (id_declinaison,))
    nb_cmd = mycursor.fetchone()['nb']

    if nb_cmd > 0:
        mycursor.execute("UPDATE declinaison SET valide = 0 WHERE id_declinaison = %s", (id_declinaison,))
        mycursor.execute(
            "INSERT INTO declinaison (id_taille, id_couleur, stock, id_velo, prix_declinaison, valide) SELECT %s, %s, %s, id_velo, %s, 1 FROM declinaison WHERE id_declinaison = %s",
            (id_taille, id_couleur, stock, prix_declinaison, id_declinaison)
        )
        flash("Déclinaison déjà commandée : une nouvelle déclinaison a été créée.", "alert-info")
    else:
        mycursor.execute(
            "UPDATE declinaison SET id_taille = %s, id_couleur = %s, stock = %s, prix_declinaison = %s WHERE id_declinaison = %s",
            (id_taille, id_couleur, stock, prix_declinaison, id_declinaison)
        )
        flash("Déclinaison modifiée.", "alert-success")

    mycursor.execute(
        "UPDATE Velo SET stock_velo = (SELECT COALESCE(SUM(d.stock),0) FROM declinaison d WHERE d.id_velo = Velo.id_velo AND d.valide = 1) WHERE id_velo = %s",
        (id_article,)
    )
    get_db().commit()
    return redirect('/admin/article/edit?id_article=' + str(id_article))


@admin_declinaison_article.route('/admin/declinaison_article/delete', methods=['GET'])
def admin_delete_declinaison_article():
    id_declinaison = request.args.get('id_declinaison_article', '')
    id_article = request.args.get('id_article', '')
    mycursor = get_db().cursor()

    mycursor.execute("SELECT COUNT(*) AS nb FROM ligne_commande WHERE id_declinaison = %s", (id_declinaison,))
    nb_cmd = mycursor.fetchone()['nb']

    if nb_cmd > 0:
        mycursor.execute("UPDATE declinaison SET valide = 0, stock = 0 WHERE id_declinaison = %s", (id_declinaison,))
        flash("Déclinaison déjà commandée : archivée (non utilisable).", "alert-info")
    else:
        mycursor.execute("DELETE FROM declinaison WHERE id_declinaison = %s", (id_declinaison,))
        flash("Déclinaison supprimée.", "alert-success")

    mycursor.execute(
        "UPDATE Velo SET stock_velo = (SELECT COALESCE(SUM(d.stock),0) FROM declinaison d WHERE d.id_velo = Velo.id_velo AND d.valide = 1) WHERE id_velo = %s",
        (id_article,)
    )
    get_db().commit()
    return redirect('/admin/article/edit?id_article=' + str(id_article))


@admin_declinaison_article.route('/admin/declinaison_article/stock', methods=['POST'])
def admin_update_stock_declinaison():
    mycursor = get_db().cursor()
    id_declinaison = request.form.get('id_declinaison', '')
    id_article = request.form.get('id_article', '')
    stock = request.form.get('stock', 0)

    mycursor.execute("UPDATE declinaison SET stock = %s WHERE id_declinaison = %s", (stock, id_declinaison))
    mycursor.execute(
        "UPDATE Velo SET stock_velo = (SELECT COALESCE(SUM(d.stock),0) FROM declinaison d WHERE d.id_velo = Velo.id_velo AND d.valide = 1) WHERE id_velo = %s",
        (id_article,)
    )
    get_db().commit()
    flash("Stock mis à jour.", "alert-success")
    return redirect('/admin/article/edit?id_article=' + str(id_article))
