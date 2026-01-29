DROP TABLE IF EXISTS ligne_panier;
DROP TABLE IF EXISTS ligne_commande;
DROP TABLE IF EXISTS commande;
DROP TABLE IF EXISTS Velo;
DROP TABLE IF EXISTS utilisateur;
DROP TABLE IF EXISTS panier;
DROP TABLE IF EXISTS etat;
DROP TABLE IF EXISTS taille;
DROP TABLE IF EXISTS type;

CREATE TABLE utilisateur (
    id_utilisateur INT PRIMARY KEY AUTO_INCREMENT,
    login VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    est_actif BOOLEAN NOT NULL DEFAULT TRUE,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE type(
   Id_type INT AUTO_INCREMENT,
   libelle_type VARCHAR(50),
   PRIMARY KEY(Id_type)
);

CREATE TABLE taille(
   Id_taille INT AUTO_INCREMENT,
   libelle_taille VARCHAR(50),
   PRIMARY KEY(Id_taille)
);

CREATE TABLE panier(
   Id_panier INT AUTO_INCREMENT,
   taille_panier VARCHAR(50),
   prix_panier VARCHAR(50),
   PRIMARY KEY(Id_panier)
);

CREATE TABLE etat(
   Id_etat INT AUTO_INCREMENT,
   libelle_etat VARCHAR(50),
   PRIMARY KEY(Id_etat)
);

CREATE TABLE Velo(
   Id_Velo INT AUTO_INCREMENT,
   nom_velo VARCHAR(50),
   prix_velo INT,
   description_velo VARCHAR(50),
   photo_velo VARCHAR(50),
   stock_velo INT,
   matiere_velo VARCHAR(50),
   couleure_velo VARCHAR(50),
   marque_velo VARCHAR(50),
   fournisseur_velo VARCHAR(50),
   Id_taille INT NOT NULL,
   Id_type INT NOT NULL,
   PRIMARY KEY(Id_Velo),
   FOREIGN KEY(Id_taille) REFERENCES taille(Id_taille),
   FOREIGN KEY(Id_type) REFERENCES type(Id_type)
);

CREATE TABLE utilisateur(
   Id_utilisateur INT AUTO_INCREMENT,
   login_utilisateur VARCHAR(50),
   password_utilisateur VARCHAR(50),
   role_utilisateur VARCHAR(50),
   est_actif_utilisateur BOOLEAN,
   nom_utilisateur VARCHAR(50),
   email_utilisateur VARCHAR(50),
   Id_panier INT NOT NULL,
   PRIMARY KEY(Id_utilisateur),
   FOREIGN KEY(Id_panier) REFERENCES panier(Id_panier)
);

CREATE TABLE commande(
   Id_commande INT AUTO_INCREMENT,
   date_commande DATE,
   prix_commande VARCHAR(50),
   Id_etat INT NOT NULL,
   Id_panier INT NOT NULL,
   Id_utilisateur INT NOT NULL,
   PRIMARY KEY(Id_commande),
   UNIQUE(Id_panier),
   FOREIGN KEY(Id_etat) REFERENCES etat(Id_etat),
   FOREIGN KEY(Id_panier) REFERENCES panier(Id_panier),
   FOREIGN KEY(Id_utilisateur) REFERENCES utilisateur(Id_utilisateur)
);

CREATE TABLE ligne_commande(
   Id_Velo INT,
   Id_commande INT,
   quantite VARCHAR(50),
   PRIMARY KEY(Id_Velo, Id_commande),
   FOREIGN KEY(Id_Velo) REFERENCES Velo(Id_Velo),
   FOREIGN KEY(Id_commande) REFERENCES commande(Id_commande)
);

CREATE TABLE ligne_panier(
   Id_Velo INT,
   Id_panier INT,
   quantite INT,
   PRIMARY KEY(Id_Velo, Id_panier),
   FOREIGN KEY(Id_Velo) REFERENCES Velo(Id_Velo),
   FOREIGN KEY(Id_panier) REFERENCES panier(Id_panier)
);

INSERT INTO utilisateur(id_utilisateur,login,email,password,role,nom,est_actif) VALUES
(1,'admin','admin@admin.fr',
    'pbkdf2:sha256:1000000$eQDrpqICHZ9eaRTn$446552ca50b5b3c248db2dde6deac950711c03c5d4863fe2bd9cef31d5f11988',
    'ROLE_admin','admin','1'),
(2,'client','client@client.fr',
    'pbkdf2:sha256:1000000$jTcSUnFLWqDqGBJz$bf570532ed29dc8e3836245f37553be6bfea24d19dfb13145d33ab667c09b349',
    'ROLE_client','client','1'),
(3,'client2','client2@client2.fr',
    'pbkdf2:sha256:1000000$qDAkJlUehmaARP1S$39044e949f63765b785007523adcde3d2ad9c2283d71e3ce5ffe58cbf8d86080',
    'ROLE_client','client2','1');

    -- Types
INSERT INTO type(libelle_type) VALUES
('Route'), ('Gravel'), ('VTT'), ('Urbain'), ('Electrique'), ('Cadre'), ('Accessoire'), ('Piece');

-- Tailles
INSERT INTO taille(libelle_taille) VALUES
('XS'), ('S'), ('M'), ('L'), ('XL'), ('XXL');

-- Etats
INSERT INTO etat(libelle_etat) VALUES
('Neuf'), ('Très bon état'), ('Bon état'), ('Etat moyen'), ('A réparer');

-- Vélo
INSERT INTO Velo(nom_velo, prix_velo, description_velo, photo_velo, stock_velo, matiere_velo, couleure_velo, marque_velo, fournisseur_velo, Id_taille, Id_type) VALUES
('Trek Domane SL6', 2300, 'Vélo de route haut de gamme carbone', 'trek_domane_sl6.jpg', 5, 'Carbone', 'Noir', 'Trek', 'CycleWorld', 3, 1),
('Specialized Diverge Comp', 2100, 'Gravel polyvalent avec pneus 40mm', 'specialized_diverge_comp.jpg', 7, 'Aluminium', 'Rouge', 'Specialized', 'BikePro', 4, 2),
('Cannondale Trail 5', 900, 'VTT tout suspendu entrée de gamme', 'cannondale_trail5.jpg', 10, 'Aluminium', 'Vert', 'Cannondale', 'OutdoorShop', 4, 3),
('Giant ToughRoad SLR', 1300, 'Gravel ready pour aventures longues distances', 'giant_toughroad_slr.jpg', 3, 'Carbone', 'Bleu', 'Giant', 'CycleZone', 2, 2),
('Cube Kathmandu Hybrid', 2500, 'VTC électrique polyvalent', 'cube_kathmandu_hybrid.jpg', 4, 'Aluminium', 'Gris', 'Cube', 'EbikeWorld', 4, 5),
('Specialized Turbo Vado', 2800, 'Vélo urbain électrique rapide', 'specialized_turbo_vado.jpg', 2, 'Aluminium', 'Blanc', 'Specialized', 'UrbanBike', 3, 5);
