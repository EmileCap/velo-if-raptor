#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, abort, flash, session
from connexion_db import get_db

admin_commentaire = Blueprint('admin_commentaire', __name__,
                        template_folder='templates')


@admin_commentaire.route('/admin/article/commentaires', methods=['GET'])
def admin_article_details():
    mycursor = get_db().cursor()
    id_article = request.args.get('id_article', None)

    # Commentaires ordonnés : non-validés d'abord , puis validés 
    # Les réponses admin suivent leur commentaire parent (fond vert)
    sql = '''
        SELECT c.id_commentaire, c.commentaire, c.date_publication,
               c.valider, c.id_utilisateur, c.id_commentaire_parent,
               u.login AS nom,
               COALESCE(p.date_publication, c.date_publication) AS root_date,
               COALESCE(p.valider, c.valider)                   AS root_valider,
               CASE WHEN c.id_commentaire_parent IS NULL THEN 0 ELSE 1 END AS is_reply
        FROM commentaire c
        INNER JOIN utilisateur u ON u.id_utilisateur = c.id_utilisateur
        LEFT  JOIN commentaire p ON p.id_commentaire = c.id_commentaire_parent
        WHERE c.id_velo = %s
        ORDER BY root_valider ASC,
                 root_date DESC,
                 is_reply ASC
    '''
    mycursor.execute(sql, (id_article,))
    commentaires = mycursor.fetchall()

    # Infos article + note moyenne
    sql = '''
        SELECT v.id_velo AS id_article, v.nom_velo AS nom,
               AVG(n.note) AS moyenne_notes,
               COUNT(n.id_utilisateur) AS nb_notes
        FROM Velo v
        LEFT JOIN note n ON n.id_velo = v.id_velo
        WHERE v.id_velo = %s
        GROUP BY v.id_velo, v.nom_velo
    '''
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()
    if article is None:
        abort(404, "Article introuvable")

    # Compteurs commentaires
    sql = '''
        SELECT
            COUNT(CASE WHEN id_commentaire_parent IS NULL THEN 1 END)         AS nb_commentaires_total,
            COUNT(CASE WHEN valider = 1 AND id_commentaire_parent IS NULL THEN 1 END) AS nb_commentaires_valider
        FROM commentaire
        WHERE id_velo = %s
    '''
    mycursor.execute(sql, (id_article,))
    nb_commentaires = mycursor.fetchone()

    return render_template('admin/article/show_article_commentaires.html',
                           commentaires=commentaires,
                           article=article,
                           nb_commentaires=nb_commentaires)

#les routes pour les admins
@admin_commentaire.route('/admin/article/commentaires/delete', methods=['POST'])
def admin_comment_delete():
    mycursor = get_db().cursor()
    id_commentaire = request.form.get('id_commentaire', None)
    id_article = request.form.get('id_article', None)

    sql = 'DELETE FROM commentaire WHERE id_commentaire_parent = %s'
    mycursor.execute(sql, (id_commentaire,))

    sql = 'DELETE FROM commentaire WHERE id_commentaire = %s'
    mycursor.execute(sql, (id_commentaire,))
    get_db().commit()
    return redirect('/admin/article/commentaires?id_article=' + id_article)


@admin_commentaire.route('/admin/article/commentaires/repondre', methods=['POST', 'GET'])
def admin_comment_add():
    if request.method == 'GET':
        id_commentaire = request.args.get('id_commentaire', None)
        id_article = request.args.get('id_article', None)
        return render_template('admin/article/add_commentaire.html',
                               id_commentaire=id_commentaire,
                               id_article=id_article)

    mycursor = get_db().cursor()
    id_admin = session['id_user'] 
    id_article = request.form.get('id_article', None)
    id_commentaire_parent = request.form.get('id_commentaire_parent', None)
    commentaire = request.form.get('commentaire', None)

    sql = '''
        INSERT INTO commentaire (commentaire, date_publication, valider, id_velo, id_utilisateur, id_commentaire_parent)
        SELECT %s, NOW(), 1, id_velo, %s, %s
        FROM commentaire WHERE id_commentaire = %s
    '''
    mycursor.execute(sql, (commentaire, id_admin, id_commentaire_parent, id_commentaire_parent))
    get_db().commit()
    return redirect('/admin/article/commentaires?id_article=' + id_article)


@admin_commentaire.route('/admin/article/commentaires/valider', methods=['GET'])
def admin_comment_valider():
    id_article = request.args.get('id_article', None)
    mycursor = get_db().cursor()

    sql = '''UPDATE commentaire SET valider = 1 WHERE id_velo = %s AND id_commentaire_parent IS NULL'''
    mycursor.execute(sql, (id_article,))
    get_db().commit()
    flash(u'Tous les commentaires ont été validés (lus)', 'alert-success')
    return redirect('/admin/article/commentaires?id_article=' + id_article)
