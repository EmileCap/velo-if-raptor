DROP TABLE IF EXISTS Type;
DROP TABLE IF EXISTS Velo;

CREATE TABLE Type(
    idType INT AUTO_INCREMENT PRIMARY KEY,
    libelleType VARCHAR(50)
);

CREATE TABLE Velo
(
    idVelo INT AUTO_INCREMENT PRIMARY KEY,
    libelleVelo VARCHAR(50),
    idType INT,
    prixVelo INT,
    tailleVelo INT,
    couleurVelo INT,
    FOREIGN KEY (idType) REFERENCES Type(idType)
);

INSERT INTO Type (libelleType) VALUES ('Downhill');
INSERT INTO Type (libelleType) VALUES ('Road');
INSERT INTO Type (libelleType) VALUES ('BMX');
INSERT INTO Type (libelleType) VALUES ('Trial');


