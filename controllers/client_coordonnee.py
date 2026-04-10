#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

from connexion_db import get_db
#test merge

client_coordonnee = Blueprint('client_coordonnee', __name__,
                        template_folder='templates')

# Etu3
@client_coordonnee.route('/client/coordonnee/show')
def client_coordonnee_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    mycursor.execute(
        "SELECT id_utilisateur, login, nom, email FROM utilisateur WHERE id_utilisateur = %s",
        (id_client,)
    )
    utilisateur = mycursor.fetchone()

    mycursor.execute(
        """
        SELECT a.id_adresse, a.nom, a.rue, a.code_postal, a.ville, a.valide, a.favori,
               COUNT(c.id_commande) AS nbr_commandes
        FROM adresse a
        LEFT JOIN commande c ON c.id_adresse_livraison = a.id_adresse
        WHERE a.utilisateur_id = %s
        GROUP BY a.id_adresse, a.nom, a.rue, a.code_postal, a.ville, a.valide, a.favori
        ORDER BY a.favori DESC, a.id_adresse ASC
        """,
        (id_client,)
    )
    adresses = mycursor.fetchall()

    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM adresse WHERE utilisateur_id = %s AND valide = 1",
        (id_client,)
    )
    nb_adresses = mycursor.fetchone()['nb']

    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM adresse WHERE utilisateur_id = %s",
        (id_client,)
    )
    nb_adresses_tot = mycursor.fetchone()['nb']

    return render_template('client/coordonnee/show_coordonnee.html',
                           utilisateur=utilisateur,
                           adresses=adresses,
                           nb_adresses=nb_adresses,
                           nb_adresses_tot=nb_adresses_tot
                           )

@client_coordonnee.route('/client/coordonnee/edit_adresse')
def client_coordonnee_edit_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse = request.args.get('id_adresse')

    mycursor.execute(
        "SELECT * FROM adresse WHERE id_adresse = %s AND utilisateur_id = %s",
        (id_adresse, id_client)
    )
    adresse = mycursor.fetchone()

    if not adresse:
        flash("Adresse introuvable ou accès non autorisé.", "alert-danger")
        return redirect('/client/coordonnee/show')

    mycursor.execute(
        "SELECT id_utilisateur, login, nom FROM utilisateur WHERE id_utilisateur = %s",
        (id_client,)
    )
    utilisateur = mycursor.fetchone()

    return render_template('client/coordonnee/edit_adresse.html',
                           adresse=adresse,
                           utilisateur=utilisateur
                           )

@client_coordonnee.route('/client/coordonnee/edit_adresse', methods=['POST'])
def client_coordonnee_edit_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom = request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville = request.form.get('ville')
    id_adresse = request.form.get('id_adresse')

    mycursor.execute(
        "SELECT * FROM adresse WHERE id_adresse = %s AND utilisateur_id = %s",
        (id_adresse, id_client)
    )
    adresse = mycursor.fetchone()

    if not adresse:
        flash("Adresse introuvable ou accès non autorisé.", "alert-danger")
        return redirect('/client/coordonnee/show')

    if not code_postal.isdigit() or len(code_postal) != 5:
        flash("Le code postal doit être composé de 5 chiffres.", "alert-danger")
        mycursor.execute(
            "SELECT id_utilisateur, login, nom FROM utilisateur WHERE id_utilisateur = %s",
            (id_client,)
        )
        utilisateur = mycursor.fetchone()
        return render_template('client/coordonnee/edit_adresse.html',
                               adresse=adresse, utilisateur=utilisateur
                               )

    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM commande WHERE id_adresse_livraison = %s OR id_adresse_facturation = %s",
        (id_adresse, id_adresse)
    )
    est_utilisee = mycursor.fetchone()['nb'] > 0

    if est_utilisee:
        etait_favori = adresse['favori']
        mycursor.execute(
            "UPDATE adresse SET valide = 0, favori = 0 WHERE id_adresse = %s",
            (id_adresse,)
        )
        mycursor.execute(
            "INSERT INTO adresse(nom, rue, code_postal, ville, valide, favori, utilisateur_id) VALUES (%s, %s, %s, %s, 1, %s, %s)",
            (nom, rue, code_postal, ville, etait_favori, id_client)
        )
    else:
        etait_favori = adresse['favori']
        mycursor.execute(
            "UPDATE adresse SET nom=%s, rue=%s, code_postal=%s, ville=%s WHERE id_adresse = %s AND utilisateur_id = %s",
            (nom, rue, code_postal, ville, id_adresse, id_client)
        )
        if etait_favori:
            pass

    get_db().commit()
    flash("Adresse modifiée avec succès.", "alert-success")
    return redirect('/client/coordonnee/show')


@client_coordonnee.route('/client/coordonnee/delete_adresse', methods=['POST'])
def client_coordonnee_delete_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse = request.form.get('id_adresse')

    mycursor.execute(
        "SELECT * FROM adresse WHERE id_adresse = %s AND utilisateur_id = %s",
        (id_adresse, id_client)
    )
    adresse = mycursor.fetchone()

    if not adresse:
        flash("Adresse introuvable ou accès non autorisé.", "alert-danger")
        return redirect('/client/coordonnee/show')

    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM commande WHERE id_adresse_livraison = %s OR id_adresse_facturation = %s",
        (id_adresse, id_adresse)
    )
    est_utilisee = mycursor.fetchone()['nb'] > 0

    etait_favori = adresse['favori']

    if est_utilisee:
        mycursor.execute(
            "UPDATE adresse SET valide = 0, favori = 0 WHERE id_adresse = %s",
            (id_adresse,)
        )
    else:
        mycursor.execute(
            "DELETE FROM adresse WHERE id_adresse = %s AND utilisateur_id = %s",
            (id_adresse, id_client)
        )

    if etait_favori:
        mycursor.execute(
            """
            SELECT a.id_adresse FROM adresse a
            LEFT JOIN commande c ON c.id_adresse_livraison = a.id_adresse
            WHERE a.utilisateur_id = %s AND a.valide = 1 AND a.id_adresse != %s
            ORDER BY c.date_achat DESC
            LIMIT 1
            """,
            (id_client, id_adresse)
        )
        nouvelle_favori = mycursor.fetchone()
        if nouvelle_favori:
            mycursor.execute(
                "UPDATE adresse SET favori = 1 WHERE id_adresse = %s",
                (nouvelle_favori['id_adresse'],)
            )

    get_db().commit()
    flash("Adresse supprimée.", "alert-success")
    return redirect('/client/coordonnee/show')

@client_coordonnee.route('/client/coordonnee/add_adresse')
def client_coordonnee_add_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    mycursor.execute(
        "SELECT id_utilisateur, login, nom FROM utilisateur WHERE id_utilisateur = %s",
        (id_client,)
    )
    utilisateur = mycursor.fetchone()

    return render_template('client/coordonnee/add_adresse.html',
                           utilisateur=utilisateur,
                           nom='', rue='', code_postal='', ville=''
                           )

@client_coordonnee.route('/client/coordonnee/add_adresse', methods=['POST'])
def client_coordonnee_add_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom = request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville = request.form.get('ville')

    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM adresse WHERE utilisateur_id = %s AND valide = 1",
        (id_client,)
    )
    nb_adresses = mycursor.fetchone()['nb']

    if nb_adresses >= 4:
        flash("Vous avez atteint le maximum de 4 adresses valides.", "alert-warning")
        return redirect('/client/coordonnee/show')

    if not code_postal.isdigit() or len(code_postal) != 5:
        flash("Le code postal doit être composé de 5 chiffres.", "alert-danger")
        mycursor.execute(
            "SELECT id_utilisateur, login, nom FROM utilisateur WHERE id_utilisateur = %s",
            (id_client,)
        )
        utilisateur = mycursor.fetchone()
        return render_template('client/coordonnee/add_adresse.html',
                               utilisateur=utilisateur,
                               nom=nom, rue=rue, code_postal=code_postal, ville=ville
                               )

    mycursor.execute(
        "SELECT COUNT(*) AS nb FROM adresse WHERE utilisateur_id = %s",
        (id_client,)
    )
    est_premiere = mycursor.fetchone()['nb'] == 0

    mycursor.execute(
        "INSERT INTO adresse(nom, rue, code_postal, ville, valide, favori, utilisateur_id) VALUES (%s, %s, %s, %s, 1, %s, %s)",
        (nom, rue, code_postal, ville, 1 if est_premiere else 0, id_client)
    )
    get_db().commit()
    flash("Adresse ajoutée avec succès.", "alert-success")
    return redirect('/client/coordonnee/show')

@client_coordonnee.route('/client/coordonnee/edit', methods=['GET'])
def client_coordonnee_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    mycursor.execute(
        "SELECT id_utilisateur, login, nom, email FROM utilisateur WHERE id_utilisateur = %s",
        (id_client,)
    )
    utilisateur = mycursor.fetchone()

    return render_template('client/coordonnee/edit_coordonnee.html',
                           utilisateur=utilisateur
                           )

@client_coordonnee.route('/client/coordonnee/edit', methods=['POST'])
def client_coordonnee_edit_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom = request.form.get('nom')
    login = request.form.get('login')
    email = request.form.get('email')

    mycursor.execute(
        "SELECT * FROM utilisateur WHERE (login = %s OR email = %s) AND id_utilisateur != %s",
        (login, email, id_client)
    )
    doublon = mycursor.fetchone()

    if doublon:
        flash("Cet email ou ce login est déjà utilisé par un autre compte.", "alert-warning")
        mycursor.execute(
            "SELECT id_utilisateur, login, nom, email FROM utilisateur WHERE id_utilisateur = %s",
            (id_client,)
        )
        utilisateur = mycursor.fetchone()
        return render_template('client/coordonnee/edit_coordonnee.html',
                               utilisateur=utilisateur
                               )

    mycursor.execute(
        "UPDATE utilisateur SET nom = %s, login = %s, email = %s WHERE id_utilisateur = %s",
        (nom, login, email, id_client)
    )
    get_db().commit()

    session['login'] = login
    flash("Profil mis à jour avec succès.", "alert-success")
    return redirect('/client/coordonnee/show')
