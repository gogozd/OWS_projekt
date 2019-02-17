**Oblikovanje web stranica - Projekt sakati Twitter - Gordan Volarevic**

Za realizaciju projekta sam uz prezentacije i vjezbe koristio nekoliko tutorijala na temu
izrade drustvenih mreza.

Za bazu podataka sam koristio SQLite za koji sam vidio da vec dolazi sa Pythonom i izgledao
mi je kao najjednostavniji za ovakvu vrstu zadatka. Iako je baza jednostavna tabela sa podacima,
malo sam se izgubio u HTML kodu kod povezivanja i ostvarivanja veza izmedju razlicitih usera i njihovih
postova, odnosno podataka koji pripadaju userima, tako da sam taj dio manje vise odradio na
temelju copy, paste-a.

U manje vise svim tutorialima se koristio peewee kao ORM (Object-relational mapping), tj. alat za 
konvertiranje podataka izmedju inace nekompatibilnih tipova. Klase za forme, korisnike i postove
su relativno lagane za sloziti.

CSS template sam preuzeo sa teamtreehouse stranice i nisam ga ni mijenjao. Uz CSS su dosli i
JavaScript fileovi koje isto tako nisam dirao.

Jedna cudna situacija koju sam primjetio je da mi aplikacija nije htjela raditi dok mi je main bio ovako
postavljen, tj. nisam mogao inicijalizirati bazu podataka:
```
if __name__ == '__main__':

    app.run()
    models.initialize()
    try:
        models.User.create_user(username='gogo', email='gogo@gmail.com', password='gogo', admin=True)
```

Izgubio sam puno vremena misleci da je problem u samom fileu, jer sam dobivao file "social.db"
koji nije imao ni jednu tabelu u sebi. Proradilo je tek kad sam stavio ovako:
```
if __name__ == '__main__':

    app.run()
models.initialize()
try:
    models.User.create_user(username='gogo', email='gogo@gmail.com', password='gogo', admin=True)
```

Testovi mi ne rade kako trebaju, nisu mi ni jasni u radu sa bazama podataka. Po netu vidim
da se cesto koristio test_database iz playhouse.test_utils koji vise ne postoji u novoj verziji
peewee-ja, tako da nisam nasao nacin da izvedem test za bazu podataka koju napravim u radnoj memoriji.

Autentifikacija se odvija preko provjeravanja lozinkonog hash-a pomocu bcrypt ekstenzije. Za login se
koristi LoginManager ekstenzija.

Svaki user koji se registrira moze koristiti svoj avatar ako na istom mailu ima avatar na Gravataru,
ukoliko nema, dobit ce generiranu sliku kao avatar. Useri koji se registriraju imaju pravo slati poruke
na glavni stream svih poruka, takodjer mogu birati koje usere ce pratiti i tako mogu dobiti stream
poruka samo od odabranih usera.

Datetime mi ne radi kako treba, vjerojatno racuna vrijeme od 1.1.1970., bar kad pokrenem na localhostu,
ali nema veze.

Forme koje su koristene su wtforms i s njima nije bilo nikakvih problema prilikom koristenja.

Logiranje je poprilicno jednostavno, a za errore je uveden 404.html na koji upucuju poznate pogreske.