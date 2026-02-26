-- ==============================================
-- Suppression des tables si elles existent
-- ==============================================
DROP TABLE IF EXISTS ligne_panier;
DROP TABLE IF EXISTS ligne_commande;
DROP TABLE IF EXISTS commande;
DROP TABLE IF EXISTS Velo;
DROP TABLE IF EXISTS declinaison;
DROP TABLE IF EXISTS etat;
DROP TABLE IF EXISTS utilisateur;
DROP TABLE IF EXISTS taille;
DROP TABLE IF EXISTS type;

-- ==============================================
-- 1. Table Utilisateur
-- ==============================================
CREATE TABLE utilisateur (
    id_utilisateur INT PRIMARY KEY AUTO_INCREMENT,
    login VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    nom VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL
);

-- ==============================================
-- 2. Table Etat
-- ==============================================
CREATE TABLE etat(
   id_etat INT PRIMARY KEY AUTO_INCREMENT,
   libelle_etat VARCHAR(50) NOT NULL
);

-- ==============================================
-- 3. Table Taille
-- ==============================================
CREATE TABLE taille(
    id_taille INT PRIMARY KEY AUTO_INCREMENT,
    libelle_taille VARCHAR(50) NOT NULL
);

-- ==============================================
-- 4. Table Type
-- ==============================================
CREATE TABLE type(
    id_type INT PRIMARY KEY AUTO_INCREMENT,
    libelle_type VARCHAR(50) NOT NULL
);

-- ==============================================
-- 5. Table Velo (Articles)
-- ==============================================
CREATE TABLE Velo(
   id_velo INT PRIMARY KEY AUTO_INCREMENT,
   nom_velo VARCHAR(50) NOT NULL,
   prix_velo INT NOT NULL,
   description_velo VARCHAR(255),
   photo_velo VARCHAR(100),
   stock_velo INT,
   matiere_velo VARCHAR(50),
   couleure_velo VARCHAR(50),
   marque_velo VARCHAR(50),
   fournisseur_velo VARCHAR(50),
   id_type INT NOT NULL,
   FOREIGN KEY(id_type) REFERENCES type(id_type)
);

-- ==============================================
-- 6. Table Commande
-- ==============================================
CREATE TABLE commande(
   id_commande INT PRIMARY KEY AUTO_INCREMENT,
   date_achat DATE NOT NULL,
   utilisateur_id INT NOT NULL,
   etat_id INT NOT NULL,
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
   FOREIGN KEY(etat_id) REFERENCES etat(id_etat)
);

-- ==============================================
-- 7. Table Ligne Commande
-- ==============================================
CREATE TABLE ligne_commande(
   commande_id INT NOT NULL,
   article_id INT NOT NULL,
   prix INT NOT NULL,
   quantite INT NOT NULL,
   PRIMARY KEY(commande_id, article_id),
   FOREIGN KEY(commande_id) REFERENCES commande(id_commande),
   FOREIGN KEY(article_id) REFERENCES Velo(id_velo)
);

-- ==============================================
-- 8. Table Ligne Panier
-- ==============================================
CREATE TABLE ligne_panier(
   utilisateur_id INT NOT NULL,
   article_id INT NOT NULL,
   quantite INT NOT NULL,
   date_ajout DATE NOT NULL,
   PRIMARY KEY(utilisateur_id, article_id),
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
   FOREIGN KEY(article_id) REFERENCES Velo(id_velo)
);

-- ==============================================
-- 9. Table Declinaison
-- ==============================================
CREATE TABLE declinaison (
    id_declinaison INT AUTO_INCREMENT PRIMARY KEY,
    id_taille INT,
    couleur VARCHAR(50),
    stock INT NOT NULL,
    id_velo INT NOT NULL,
    d_taille_uniq VARCHAR(50),
    d_couleur_uniq VARCHAR(50),
    FOREIGN KEY(id_taille) REFERENCES taille(id_taille),
    FOREIGN KEY(id_velo) REFERENCES Velo(id_velo)
);

-- ==============================================
-- INSERTS
-- ==============================================

-- Utilisateurs
INSERT INTO utilisateur(id_utilisateur, login, email, nom, password, role) VALUES
(1,'admin','admin@admin.fr','Admin','pbkdf2:sha256:1000000$eQDrpqICHZ9eaRTn$446552ca50b5b3c248db2dde6deac950711c03c5d4863fe2bd9cef31d5f11988','ROLE_admin'),
(2,'client','client@client.fr','Client','pbkdf2:sha256:1000000$jTcSUnFLWqDqGBJz$bf570532ed29dc8e3836245f37553be6bfea24d19dfb13145d33ab667c09b349','ROLE_client'),
(3,'client2','client2@client2.fr','Client2','pbkdf2:sha256:1000000$qDAkJlUehmaARP1S$39044e949f63765b785007523adcde3d2ad9c2283d71e3ce5ffe58cbf8d86080','ROLE_client');

-- Etats
INSERT INTO etat(id_etat, libelle_etat) VALUES
(1,'Terminée'),
(2,'En cours'),
(3,'Expédié');

-- Tailles
INSERT INTO taille(id_taille, libelle_taille) VALUES
(1,'XS'),(2,'S'),(3,'M'),(4,'L'),(5,'XL'),(6,'XXL');

-- Types
INSERT INTO type(id_type, libelle_type) VALUES
(1,'Route'),(2,'Gravel'),(3,'VTT'),(4,'Urbain'),(5,'Electrique'),(6,'Cadre'),(7,'Accessoire'),(8,'Piece');

-- Vélos
INSERT INTO Velo(id_velo, nom_velo, prix_velo, description_velo, photo_velo, stock_velo, matiere_velo, couleure_velo, marque_velo, fournisseur_velo, id_type) VALUES
(1,'Trek Domane SL6',2300,'Vélo de route haut de gamme carbone','Trek-domane-sl6-gen4-2024.png',5,'Carbone','Noir','Trek','CycleWorld',1),
(2,'Specialized Diverge Comp',2100,'Gravel polyvalent avec pneus 40mm','Specialized Diverge Comp.png',7,'Aluminium','Rouge','Specialized','BikePro',2),
(3,'Cannondale Trail 5',900,'VTT tout suspendu entrée de gamme','Cannondale Trail 5.png',10,'Aluminium','Vert','Cannondale','OutdoorShop',3),
(4,'Giant ToughRoad SLR',1300,'Gravel ready pour aventures longues distances','Giant ToughRoad SLR.png',3,'Carbone','Bleu','Giant','CycleZone',2),
(5,'Cube Kathmandu Hybrid',2500,'VTC électrique polyvalent','Cube Kathmandu Hybrid.png',4,'Aluminium','Gris','Cube','EbikeWorld',5),
(6,'Specialized Turbo Vado',2800,'Vélo urbain électrique rapide','Specialized Turbo Vado.png',2,'Aluminium','Blanc','Specialized','UrbanBike',5),
(7,'BMC Teammachine SLR01',4500,'Vélo de route ultra performant carbone','BMC Teammachine SLR01.png',3,'Carbone','Gris','BMC','EliteCycles',1),
(8,'Canyon Grail CF SL 7',2800,'Gravel carbone avec double cockpit','Canyon Grail CF SL 7.png',5,'Carbone','Bleu','Canyon','GravelGear',2),
(9,'Scott Scale 940',1500,'Hardtail VTT rapide et léger','Scott Scale 940.png',6,'Carbone','Noir','Scott','MountainLife',3),
(10,'Merida Silex 200',1600,'Gravel moderne pour longues distances','Merida Silex 200.png',4,'Aluminium','Rouge','Merida','BikePlanet',2),
(11,'Specialized Rockhopper Comp',1100,'VTT polyvalent trail','Specialized Rockhopper Comp.png',8,'Aluminium','Vert','Specialized','TrailZone',3),
(12,'Trek FX Sport 4',1000,'VTC performant pour ville et loisirs','Trek FX Sport 4.png',7,'Aluminium','Noir','Trek','UrbanCycling',4),
(13,'Giant Contend AR 3',1300,'Route endurance avec pneus larges','Giant Contend AR 3.png',5,'Aluminium','Bleu','Giant','CyclePlus',1),
(14,'Orbea Wild FS M20',3200,'VTT tout suspendu haut de gamme','Orbea Wild FS M20.png',2,'Carbone','Orange','Orbea','ProGear',3),
(15,'VanMoof S3',2200,'Vélo électrique urbain connecté','VanMoof S3.png',4,'Aluminium','Blanc','VanMoof','SmartBike',5),
(16,'Ribble Endurance AL Disc',1400,'Route endurance avec freins à disque','Ribble Endurance AL Disc.png',6,'Aluminium','Rouge','Ribble','EuroCycles',1);

-- Déclinaisons (utiliser id_taille)
INSERT INTO declinaison (id_taille, couleur, stock, id_velo, d_taille_uniq, d_couleur_uniq) VALUES
(3, 'Noir', 5, 1, 'M', 'Noir'),
(3, 'Rouge', 7, 2, 'M', 'Rouge'),
(4, 'Vert', 10, 3, 'L', 'Vert'),
(3, 'Bleu', 3, 4, 'M', 'Bleu'),
(4, 'Gris', 4, 5, 'L', 'Gris'),
(3, 'Blanc', 2, 6, 'M', 'Blanc'),
(3, 'Gris', 3, 7, 'M', 'Gris'),
(4, 'Bleu', 5, 8, 'L', 'Bleu'),
(4, 'Noir', 6, 9, 'L', 'Noir'),
(3, 'Rouge', 4, 10, 'M', 'Rouge'),
(4, 'Vert', 8, 11, 'L', 'Vert'),
(3, 'Noir', 7, 12, 'M', 'Noir'),
(3, 'Bleu', 5, 13, 'M', 'Bleu'),
(4, 'Orange', 2, 14, 'L', 'Orange'),
(3, 'Blanc', 4, 15, 'M', 'Blanc'),
(3, 'Rouge', 6, 16, 'M', 'Rouge');

-- Commandes
INSERT INTO commande(id_commande, date_achat, utilisateur_id, etat_id) VALUES
(1,'2026-02-05',2,2),
(2,'2026-02-01',3,1);

-- Lignes de commande
INSERT INTO ligne_commande(commande_id, article_id, prix, quantite) VALUES
(1,1,2300,2),
(1,2,2100,1),
(2,3,900,1);

-- Lignes de panier
INSERT INTO ligne_panier(utilisateur_id, article_id, quantite, date_ajout) VALUES
(2,1,2,'2026-02-03'),
(2,2,1,'2026-02-03'),
(3,3,1,'2026-02-02');