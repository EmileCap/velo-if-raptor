#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, abort, flash, session
from connexion_db import get_db
from controllers.client_liste_envies import client_historique_add

client_commentaire = Blueprint('client_commentaire', __name__,
                        template_folder='templates')


@client_commentaire.route('/client/article/details', methods=['GET'])
def client_article_details():
    mycursor = get_db().cursor()
    id_article = request.args.get('id_article', None)
    id_client = session['id_user']

    # on affiche le velo avec sa note son nombre de note et ses commentaires 
    sql = '''
        SELECT v.id_velo AS id_article, v.nom_velo AS nom, v.prix_velo AS prix,
               v.description_velo AS description, v.photo_velo AS image,
               t.libelle_type,
               AVG(n.note) AS moyenne_notes,
               COUNT(n.id_utilisateur) AS nb_notes
        FROM Velo v
        INNER JOIN type t ON t.id_type = v.id_type
        LEFT JOIN note n ON n.id_velo = v.id_velo
        WHERE v.id_velo = %s
        GROUP BY v.id_velo, v.nom_velo, v.prix_velo,
                 v.description_velo, v.photo_velo, t.libelle_type
    '''
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()
    if article is None:
        abort(404, "Article introuvable")

    # on vérifie si il a bien acheté le produit qu'il essaye de commenter 
    sql = '''
        SELECT COUNT(*) AS nb
        FROM commande c
        INNER JOIN ligne_commande lc ON lc.commande_id = c.id_commande
        INNER JOIN declinaison d ON d.id_declinaison = lc.id_declinaison
        WHERE c.utilisateur_id = %s AND d.id_velo = %s
    '''
    mycursor.execute(sql, (id_client, id_article))
    commandes_articles = mycursor.fetchone()

    # commentaire ordonné avec la date, si un admin y a répondu  etc
    sql = '''
        SELECT c.id_commentaire, c.commentaire, c.date_publication,
               c.valider, c.id_utilisateur, c.id_commentaire_parent,
               u.login AS nom,
               COALESCE(p.date_publication, c.date_publication) AS root_date,
               CASE WHEN c.id_commentaire_parent IS NULL THEN 0 ELSE 1 END AS is_reply
        FROM commentaire c
        INNER JOIN utilisateur u ON u.id_utilisateur = c.id_utilisateur
        LEFT  JOIN commentaire p ON p.id_commentaire = c.id_commentaire_parent
        WHERE c.id_velo = %s
        ORDER BY root_date DESC, is_reply ASC
    '''
    mycursor.execute(sql, (id_article,))
    commentaires = mycursor.fetchall()

    # Note du client pour cet article
    sql = 'SELECT note FROM note WHERE id_utilisateur = %s AND id_velo = %s'
    mycursor.execute(sql, (id_client, id_article))
    note_row = mycursor.fetchone()
    note = note_row['note'] if note_row else None

    # Statistiques en une seule requête SQL
    sql = '''
        SELECT
            COUNT(CASE WHEN c.id_utilisateur = %s AND c.id_commentaire_parent IS NULL THEN 1 END)
                AS nb_commentaires_user,
            COUNT(CASE WHEN c.id_commentaire_parent IS NULL THEN 1 END)
                AS nb_commentaires_total,
            COUNT(CASE WHEN c.valider = 1 AND c.id_commentaire_parent IS NULL THEN 1 END)
                AS nb_commentaires_valides,
            COUNT(CASE WHEN c.id_utilisateur = %s AND c.valider = 1
                       AND c.id_commentaire_parent IS NULL THEN 1 END)
                AS nb_commentaires_user_valides
        FROM commentaire c
        WHERE c.id_velo = %s
    '''
    mycursor.execute(sql, (id_client, id_client, id_article))
    nb_commentaires = mycursor.fetchone()

    return render_template('client/article_info/article_details.html',
                           article=article,
                           commentaires=commentaires,
                           commandes_articles=commandes_articles,
                           note=note,
                           nb_commentaires=nb_commentaires)

#toute les routes python pour que ça fonctionne bien
@client_commentaire.route('/client/commentaire/add', methods=['POST'])
def client_comment_add():
    mycursor = get_db().cursor()
    commentaire = request.form.get('commentaire', '').strip()
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)

    if len(commentaire) == 0:
        flash(u'Commentaire non pris en compte', 'alert-warning')
        return redirect('/client/article/details?id_article=' + id_article)
    if len(commentaire) < 3:
        flash(u'Commentaire trop court (minimum 3 caractères)', 'alert-warning')
        return redirect('/client/article/details?id_article=' + id_article)

    # Vérification quota (3 max) côté serveur via SQL
    sql = '''SELECT COUNT(*) AS nb FROM commentaire
             WHERE id_utilisateur = %s AND id_velo = %s AND id_commentaire_parent IS NULL'''
    mycursor.execute(sql, (id_client, id_article))
    quota = mycursor.fetchone()
    if quota['nb'] >= 3:
        flash(u'⚠️ QUOTA ATTEINT : vous avez déjà posté 3 commentaires sur cet article (maximum autorisé).', 'alert-danger')
        return redirect('/client/article/details?id_article=' + id_article)

    sql = 'INSERT INTO commentaire (commentaire, id_utilisateur, id_velo) VALUES (%s, %s, %s)'
    mycursor.execute(sql, (commentaire, id_client, id_article))
    get_db().commit()
    flash(u'Commentaire ajouté avec succès', 'alert-success')
    return redirect('/client/article/details?id_article=' + id_article)


@client_commentaire.route('/client/commentaire/delete', methods=['POST'])
def client_comment_detete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)
    id_commentaire = request.form.get('id_commentaire', None)

    sql = '''DELETE FROM commentaire
             WHERE id_commentaire = %s AND id_utilisateur = %s AND id_velo = %s
               AND id_commentaire_parent IS NULL'''
    mycursor.execute(sql, (id_commentaire, id_client, id_article))
    get_db().commit()
    return redirect('/client/article/details?id_article=' + id_article)


@client_commentaire.route('/client/note/add', methods=['POST'])
def client_note_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    note = request.form.get('note', None)
    id_article = request.form.get('id_article', None)
    sql = 'INSERT INTO note (note, id_utilisateur, id_velo) VALUES (%s, %s, %s)'
    mycursor.execute(sql, (note, id_client, id_article))
    get_db().commit()
    return redirect('/client/article/details?id_article=' + id_article)


@client_commentaire.route('/client/note/edit', methods=['POST'])
def client_note_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    note = request.form.get('note', None)
    id_article = request.form.get('id_article', None)
    sql = 'UPDATE note SET note = %s WHERE id_utilisateur = %s AND id_velo = %s'
    mycursor.execute(sql, (note, id_client, id_article))
    get_db().commit()
    return redirect('/client/article/details?id_article=' + id_article)


@client_commentaire.route('/client/note/delete', methods=['POST'])
def client_note_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)
    sql = 'DELETE FROM note WHERE id_utilisateur = %s AND id_velo = %s'
    mycursor.execute(sql, (id_client, id_article))
    get_db().commit()
    return redirect('/client/article/details?id_article=' + id_article)
