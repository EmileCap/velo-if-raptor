DROP TABLE IF EXISTS ligne_panier;
DROP TABLE IF EXISTS ligne_commande;
DROP TABLE IF EXISTS commande;
DROP TABLE IF EXISTS adresse;
DROP TABLE IF EXISTS declinaison;
DROP TABLE IF EXISTS Velo;
DROP TABLE IF EXISTS couleur;
DROP TABLE IF EXISTS etat;
DROP TABLE IF EXISTS utilisateur;
DROP TABLE IF EXISTS taille;
DROP TABLE IF EXISTS type;

CREATE TABLE utilisateur (
    id_utilisateur INT PRIMARY KEY AUTO_INCREMENT,
    login VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    nom VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL
);

-- Etu3
CREATE TABLE adresse (
    id_adresse INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(100) NOT NULL,
    rue VARCHAR(150) NOT NULL,
    code_postal VARCHAR(5) NOT NULL,
    ville VARCHAR(100) NOT NULL,
    valide TINYINT(1) NOT NULL DEFAULT 1,
    favori TINYINT(1) NOT NULL DEFAULT 0,
    utilisateur_id INT NOT NULL,
    FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur)
);

CREATE TABLE etat(
   id_etat INT PRIMARY KEY AUTO_INCREMENT,
   libelle_etat VARCHAR(50) NOT NULL
);

CREATE TABLE taille(
    id_taille INT PRIMARY KEY AUTO_INCREMENT,
    libelle_taille VARCHAR(50) NOT NULL
);

CREATE TABLE couleur(
    id_couleur INT PRIMARY KEY AUTO_INCREMENT,
    libelle_couleur VARCHAR(50) NOT NULL,
    code_couleur VARCHAR(20) DEFAULT '#000000'
);

CREATE TABLE type(
    id_type INT PRIMARY KEY AUTO_INCREMENT,
    libelle_type VARCHAR(50) NOT NULL
);

CREATE TABLE Velo(
   id_velo INT PRIMARY KEY AUTO_INCREMENT,
   nom_velo VARCHAR(50) NOT NULL,
   prix_velo INT NOT NULL,
   description_velo VARCHAR(255),
   photo_velo VARCHAR(100),
   stock_velo INT DEFAULT 0,
   matiere_velo VARCHAR(50),
   couleure_velo VARCHAR(50),
   marque_velo VARCHAR(50),
   fournisseur_velo VARCHAR(50),
   id_type INT NOT NULL,
   FOREIGN KEY(id_type) REFERENCES type(id_type)
);

CREATE TABLE commande(
   id_commande INT PRIMARY KEY AUTO_INCREMENT,
   date_achat DATE NOT NULL,
   utilisateur_id INT NOT NULL,
   etat_id INT NOT NULL,
   id_adresse_livraison INT DEFAULT NULL,
   id_adresse_facturation INT DEFAULT NULL,
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
   FOREIGN KEY(etat_id) REFERENCES etat(id_etat),
   -- Etu3
   FOREIGN KEY(id_adresse_livraison) REFERENCES adresse(id_adresse),
   FOREIGN KEY(id_adresse_facturation) REFERENCES adresse(id_adresse)
);

CREATE TABLE declinaison (
    id_declinaison INT AUTO_INCREMENT PRIMARY KEY,
    id_taille INT NOT NULL,
    id_couleur INT NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    id_velo INT NOT NULL,
    prix_declinaison INT DEFAULT NULL,
    valide TINYINT(1) NOT NULL DEFAULT 1,
    FOREIGN KEY(id_taille) REFERENCES taille(id_taille),
    FOREIGN KEY(id_couleur) REFERENCES couleur(id_couleur),
    FOREIGN KEY(id_velo) REFERENCES Velo(id_velo)
);

CREATE TABLE ligne_commande(
   commande_id INT NOT NULL,
   id_declinaison INT NOT NULL,
   prix INT NOT NULL,
   quantite INT NOT NULL,
   PRIMARY KEY(commande_id, id_declinaison),
   FOREIGN KEY(commande_id) REFERENCES commande(id_commande),
   FOREIGN KEY(id_declinaison) REFERENCES declinaison(id_declinaison)
);

CREATE TABLE ligne_panier(
   utilisateur_id INT NOT NULL,
   id_declinaison INT NOT NULL,
   quantite INT NOT NULL,
   date_ajout DATE NOT NULL,
   PRIMARY KEY(utilisateur_id, id_declinaison),
   FOREIGN KEY(utilisateur_id) REFERENCES utilisateur(id_utilisateur),
   FOREIGN KEY(id_declinaison) REFERENCES declinaison(id_declinaison)
);

INSERT INTO utilisateur(id_utilisateur, login, email, nom, password, role) VALUES
(1,'admin','admin@admin.fr','Admin','pbkdf2:sha256:1000000$eQDrpqICHZ9eaRTn$446552ca50b5b3c248db2dde6deac950711c03c5d4863fe2bd9cef31d5f11988','ROLE_admin'),
(2,'client','client@client.fr','Client','pbkdf2:sha256:1000000$jTcSUnFLWqDqGBJz$bf570532ed29dc8e3836245f37553be6bfea24d19dfb13145d33ab667c09b349','ROLE_client'),
(3,'client2','client2@client2.fr','Client2','pbkdf2:sha256:1000000$qDAkJlUehmaARP1S$39044e949f63765b785007523adcde3d2ad9c2283d71e3ce5ffe58cbf8d86080','ROLE_client');

-- Etu3
INSERT INTO adresse(nom, rue, code_postal, ville, valide, favori, utilisateur_id) VALUES
('Client Dupont', '12 rue des Lilas', '25000', 'Besançon', 1, 1, 2),
('Client Dupont', '5 avenue de la Gare', '75001', 'Paris', 1, 0, 2),
('Client2 Martin', '8 rue du Port', '69001', 'Lyon', 1, 1, 3);

INSERT INTO etat(id_etat, libelle_etat) VALUES
(1,'En cours'),(2,'Expedie'),(3,'Terminee');

INSERT INTO taille(id_taille, libelle_taille) VALUES
(1,'Unique'),(2,'XS'),(3,'S'),(4,'M'),(5,'L'),(6,'XL'),(7,'XXL');

INSERT INTO couleur(id_couleur, libelle_couleur, code_couleur) VALUES
(1,'Unique','#888888'),(2,'Noir','#111111'),(3,'Rouge','#e00000'),
(4,'Vert','#2d8a2d'),(5,'Bleu','#1a5fcb'),(6,'Gris','#888888'),
(7,'Blanc','#f5f5f5'),(8,'Orange','#e87800');

INSERT INTO type(id_type, libelle_type) VALUES
(1,'Route'),(2,'Gravel'),(3,'VTT'),(4,'Urbain'),(5,'Electrique'),(6,'Cadre'),(7,'Accessoire'),(8,'Piece');

INSERT INTO Velo(id_velo, nom_velo, prix_velo, description_velo, photo_velo, stock_velo, matiere_velo, couleure_velo, marque_velo, fournisseur_velo, id_type) VALUES
(1,'Trek Domane SL6',2300,'Velo de route haut de gamme carbone','Trek-domane-sl6-gen4-2024.png',0,'Carbone','Noir','Trek','CycleWorld',1),
(2,'Specialized Diverge Comp',2100,'Gravel polyvalent avec pneus 40mm','Specialized Diverge Comp.png',0,'Aluminium','Rouge','Specialized','BikePro',2),
(3,'Cannondale Trail 5',900,'VTT tout suspendu entree de gamme','Cannondale Trail 5.png',0,'Aluminium','Vert','Cannondale','OutdoorShop',3),
(4,'Giant ToughRoad SLR',1300,'Gravel ready pour aventures longues distances','Giant ToughRoad SLR.png',0,'Carbone','Bleu','Giant','CycleZone',2),
(5,'Cube Kathmandu Hybrid',2500,'VTC electrique polyvalent','Cube Kathmandu Hybrid.png',0,'Aluminium','Gris','Cube','EbikeWorld',5),
(6,'Specialized Turbo Vado',2800,'Velo urbain electrique rapide','Specialized Turbo Vado.png',0,'Aluminium','Blanc','Specialized','UrbanBike',5),
(7,'BMC Teammachine SLR01',4500,'Velo de route ultra performant carbone','BMC Teammachine SLR01.png',0,'Carbone','Gris','BMC','EliteCycles',1),
(8,'Canyon Grail CF SL 7',2800,'Gravel carbone avec double cockpit','Canyon Grail CF SL 7.png',0,'Carbone','Bleu','Canyon','GravelGear',2),
(9,'Scott Scale 940',1500,'Hardtail VTT rapide et leger','Scott Scale 940.png',0,'Carbone','Noir','Scott','MountainLife',3),
(10,'Merida Silex 200',1600,'Gravel moderne pour longues distances','Merida Silex 200.png',0,'Aluminium','Rouge','Merida','BikePlanet',2),
(11,'Specialized Rockhopper Comp',1100,'VTT polyvalent trail','Specialized Rockhopper Comp.png',0,'Aluminium','Vert','Specialized','TrailZone',3),
(12,'Trek FX Sport 4',1000,'VTC performant pour ville et loisirs','Trek FX Sport 4.png',0,'Aluminium','Noir','Trek','UrbanCycling',4),
(13,'Giant Contend AR 3',1300,'Route endurance avec pneus larges','Giant Contend AR 3.png',0,'Aluminium','Bleu','Giant','CyclePlus',1),
(14,'Orbea Wild FS M20',3200,'VTT tout suspendu haut de gamme','Orbea Wild FS M20.png',0,'Carbone','Orange','Orbea','ProGear',3),
(15,'VanMoof S3',2200,'Velo electrique urbain connecte','VanMoof S3.png',0,'Aluminium','Blanc','VanMoof','SmartBike',5),
(16,'Ribble Endurance AL Disc',1400,'Route endurance avec freins a disque','Ribble Endurance AL Disc.png',0,'Aluminium','Rouge','Ribble','EuroCycles',1);

INSERT INTO declinaison(id_taille, id_couleur, stock, id_velo, prix_declinaison, valide) VALUES
(4,2,3,1,NULL,1),(5,2,2,1,NULL,1),(4,3,2,1,2400,1),
(4,3,4,2,NULL,1),(5,3,3,2,2200,1),
(1,4,5,3,NULL,1),(1,5,5,3,NULL,1),
(1,1,3,4,NULL,1),
(5,1,2,5,NULL,1),(6,1,2,5,2600,1),
(1,7,1,6,NULL,1),(1,2,1,6,NULL,1),
(3,1,1,7,NULL,1),(4,1,1,7,NULL,1),(5,1,1,7,NULL,1),
(4,5,3,8,NULL,1),(5,5,2,8,NULL,1),
(4,1,3,9,NULL,1),(5,1,3,9,NULL,1),
(1,3,2,10,NULL,1),(1,4,2,10,NULL,1),
(4,4,4,11,NULL,1),(5,4,4,11,NULL,1),
(1,1,7,12,NULL,1),
(4,1,3,13,NULL,1),(5,1,2,13,NULL,1),
(4,8,1,14,NULL,1),(5,8,1,14,NULL,1),
(1,7,2,15,NULL,1),(1,2,2,15,NULL,1),
(4,3,3,16,NULL,1),(5,3,3,16,NULL,1);

UPDATE Velo SET stock_velo = (
    SELECT COALESCE(SUM(d.stock),0) FROM declinaison d
    WHERE d.id_velo = Velo.id_velo AND d.valide = 1
);

INSERT INTO commande(id_commande, date_achat, utilisateur_id, etat_id) VALUES
(1,'2026-02-05',2,1),(2,'2026-02-01',3,3);

INSERT INTO ligne_commande(commande_id, id_declinaison, prix, quantite) VALUES
(1,1,2300,2),(1,4,2100,1),(2,6,900,1);

UPDATE declinaison SET stock = stock - 2 WHERE id_declinaison = 1;
UPDATE declinaison SET stock = stock - 1 WHERE id_declinaison = 4;
UPDATE declinaison SET stock = stock - 1 WHERE id_declinaison = 6;

UPDATE Velo SET stock_velo = (
    SELECT COALESCE(SUM(d.stock),0) FROM declinaison d
    WHERE d.id_velo = Velo.id_velo AND d.valide = 1
);
