#! /usr/bin/python
# -*- coding:utf-8 -*-
import os.path
from random import random

from flask import Blueprint
from flask import request, render_template, redirect, flash

from connexion_db import get_db

admin_article = Blueprint('admin_article', __name__,
                          template_folder='templates')


@admin_article.route('/admin/article/show')
def show_article():
    mycursor = get_db().cursor()
    sql = """
    SELECT v.nom_velo AS nom, v.id_velo AS id_article, v.prix_velo AS prix,
           v.id_type AS type_article_id, t.libelle_type AS libelle,
           v.photo_velo AS image,
           COALESCE(SUM(d.stock), 0) AS stock,
           COUNT(d.id_declinaison)   AS nb_declinaisons,
           MIN(d.stock)              AS min_stock
    FROM Velo v
    INNER JOIN type t ON v.id_type = t.id_type
    LEFT  JOIN declinaison d ON d.id_velo = v.id_velo AND d.valide = 1
    GROUP BY v.id_velo, v.nom_velo, v.prix_velo, v.id_type, t.libelle_type, v.photo_velo
    ORDER BY v.id_velo
    """
    mycursor.execute(sql)
    articles = mycursor.fetchall()
    return render_template('admin/article/show_article.html', articles=articles)


@admin_article.route('/admin/article/add', methods=['GET'])
def add_article():
    mycursor = get_db().cursor()
    mycursor.execute("SELECT id_type AS id_type_article, libelle_type AS libelle FROM type")
    types_article = mycursor.fetchall()
    return render_template('admin/article/add_article.html', types_article=types_article)


@admin_article.route('/admin/article/add', methods=['POST'])
def valid_add_article():
    mycursor = get_db().cursor()
    nom = request.form.get('nom', '')
    type_article_id = request.form.get('type_article_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description', '')
    image = request.files.get('image', '')

    if image:
        filename = 'img_upload' + str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
    else:
        filename = None

    sql = "INSERT INTO Velo (nom_velo, photo_velo, prix_velo, id_type, description_velo) VALUES (%s, %s, %s, %s, %s)"
    mycursor.execute(sql, (nom, filename, prix, type_article_id, description))
    get_db().commit()

    flash(u'Article ajouté : ' + nom, 'alert-success')
    return redirect('/admin/article/show')


@admin_article.route('/admin/article/delete', methods=['GET'])
def delete_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()

    mycursor.execute("""
        SELECT COUNT(*) AS nb FROM ligne_commande lc
        INNER JOIN declinaison d ON d.id_declinaison = lc.id_declinaison
        WHERE d.id_velo = %s
    """, (id_article,))
    nb_cmd = mycursor.fetchone()

    if nb_cmd['nb'] > 0:
        flash(u'Cet article a été commandé : impossible de le supprimer.', 'alert-warning')
    else:
        mycursor.execute("SELECT photo_velo AS image FROM Velo WHERE id_velo = %s", (id_article,))
        article = mycursor.fetchone()
        image = article['image']

        mycursor.execute("DELETE FROM declinaison WHERE id_velo = %s", (id_article,))
        mycursor.execute("DELETE FROM Velo WHERE id_velo = %s", (id_article,))
        get_db().commit()

        if image is not None and os.path.exists('static/images/' + image):
            os.remove('static/images/' + image)

        flash(u'Article supprimé, id : ' + str(id_article), 'alert-success')

    return redirect('/admin/article/show')


@admin_article.route('/admin/article/edit', methods=['GET'])
def edit_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()

    mycursor.execute("""
        SELECT id_velo AS id_article, nom_velo AS nom, id_type AS type_article_id,
               prix_velo AS prix, photo_velo AS image, stock_velo AS stock,
               description_velo AS description
        FROM Velo WHERE id_velo = %s
    """, (id_article,))
    article = mycursor.fetchone()

    mycursor.execute("SELECT id_type AS id_type_article, libelle_type AS libelle FROM type")
    types_article = mycursor.fetchall()

    mycursor.execute("""
        SELECT d.id_declinaison AS id_declinaison_article, d.id_velo AS article_id,
               d.id_taille, d.id_couleur, d.stock, d.prix_declinaison,
               t.libelle_taille, c.libelle_couleur
        FROM declinaison d
        INNER JOIN taille t  ON t.id_taille  = d.id_taille
        INNER JOIN couleur c ON c.id_couleur = d.id_couleur
        WHERE d.id_velo = %s AND d.valide = 1
        ORDER BY d.id_declinaison
    """, (id_article,))
    declinaisons_article = mycursor.fetchall()

    return render_template('admin/article/edit_article.html',
                           article=article,
                           types_article=types_article,
                           declinaisons_article=declinaisons_article)


@admin_article.route('/admin/article/edit', methods=['POST'])
def valid_edit_article():
    mycursor = get_db().cursor()
    nom = request.form.get('nom')
    id_article = request.form.get('id_article')
    image = request.files.get('image', '')
    type_article_id = request.form.get('type_article_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description')

    mycursor.execute("SELECT photo_velo AS image FROM Velo WHERE id_velo = %s", (id_article,))
    image_nom = mycursor.fetchone()['image']

    if image:
        if image_nom and os.path.exists(os.path.join(os.getcwd() + "/static/images/", image_nom)):
            os.remove(os.path.join(os.getcwd() + "/static/images/", image_nom))
        filename = 'img_upload_' + str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
        image_nom = filename

    mycursor.execute(
        "UPDATE Velo SET nom_velo = %s, photo_velo = %s, prix_velo = %s, id_type = %s, description_velo = %s WHERE id_velo = %s",
        (nom, image_nom, prix, type_article_id, description, id_article)
    )
    get_db().commit()
    flash(u'Article modifié : ' + nom, 'alert-success')
    return redirect('/admin/article/show')


@admin_article.route('/admin/article/avis/<int:id>', methods=['GET'])
def admin_avis(id):
    mycursor = get_db().cursor()
    article = []
    commentaires = {}
    return render_template('admin/article/show_avis.html',
                           article=article,
                           commentaires=commentaires)


@admin_article.route('/admin/comment/delete', methods=['POST'])
def admin_avis_delete():
    mycursor = get_db().cursor()
    article_id = request.form.get('idArticle', None)
    return admin_avis(article_id)
