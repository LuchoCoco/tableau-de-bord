# Tableau de bord pour tablette

Guide pour débutant. Lis les parties dans l'ordre, tu n'as pas besoin de tout comprendre au code.

## 0. Ce que contient le dossier

| Fichier | À quoi il sert | Tu le modifies ? |
|---|---|---|
| `index.html` | La page entière. **L'objet `CONFIG` tout en haut** regroupe tous les réglages. | Oui, seulement `CONFIG` |
| `cards.json` | Tes cartes « À apprendre » (52 pour commencer). | Oui |
| `sources-actus.json` | La liste des flux RSS lus par le robot. | Oui |
| `news.json` | Les actus du jour, **écrit automatiquement** par le robot. | Non |
| `scripts/fetch_news.py` | Le robot qui lit les flux RSS. | Non |
| `.github/workflows/publier.yml` | Dit à GitHub de lancer le robot chaque matin et de publier le site. | Non |
| `google-apps-script/agenda.gs` | À copier-coller dans Google (partie 3). Pas besoin de le mettre sur GitHub. | Non |

> Pourquoi les flux RSS ne sont pas dans `CONFIG` ? Parce que c'est le robot GitHub qui les lit, pas la tablette, et il ne lit pas `index.html`. C'est la seule exception.

---

## 1. Tester sur ton ordinateur

Si tu ouvres `index.html` par un double-clic, le navigateur bloque la lecture de `cards.json` et `news.json` : il faut un mini serveur local. Ouvre l'appli **Terminal** sur ton Mac et tape :

```bash
cd ~/Documents/"Claude Code"/tableau-de-bord
```

```bash
python3 -m http.server 8000
```

Puis ouvre **http://localhost:8000** dans Chrome. Pour arrêter le serveur : `Ctrl + C` dans le Terminal.

Pour simuler la tablette dans Chrome : clic droit > **Inspecter** > icône tablette/téléphone en haut à gauche, puis choisis par exemple 1024 × 600 ou 1280 × 800.

À vérifier, étape par étape :

- **(a) Horloge + météo + design** : l'heure, la date, le lever et le coucher du soleil, la météo de Pontcarré et les prévisions heure par heure. Dans **Réglages > Informations**, la ligne « Météo » doit indiquer « lieu : Pontcarré (Seine-et-Marne) ».
- **(b) Frise + agenda** : tant que l'agenda n'est pas branché, la frise montre des **EXEMPLES** (c'est écrit en haut à droite). Une fois l'agenda branché (partie 3), tes vrais événements apparaissent.
- **(c) Échéances + musique + mode nuit** : ajoute une échéance (onglet Échéances), puis recharge la page : elle doit toujours être là. Dans **Réglages**, « Tester le mode nuit (1 min) ». Si tu testes la nuit (entre 22h30 et 7h), le mode nuit s'affiche tout seul ; touche l'écran pour voir le tableau de bord pendant 1 min.
- **(d) Actus + cartes** : le bloc « Ce matin » montre des titres, la ligne « Ce jour-là » (Wikipédia) apparaît, la carte du jour s'affiche. Touche-la pour voir la réponse. Si tu ne touches à rien pendant 3 min, des cartes défilent toutes seules.

Si un **bandeau rouge** apparaît après une modification de `CONFIG`, il manque presque toujours une virgule ou un guillemet.

---

## 2. Personnaliser

Ouvre `index.html` avec un éditeur de texte (TextEdit en mode « texte brut », ou mieux [VS Code](https://code.visualstudio.com/), gratuit) et modifie **uniquement** le bloc `var CONFIG = { ... }` en haut. Chaque ligne est commentée en français.

Choix que j'ai faits pour toi (tu peux les changer) :
- mode nuit de **22h30 à 7h00** ;
- frise de **7h à 23h** ;
- cartes qui défilent après **3 min** sans toucher l'écran, puis retour automatique à l'accueil après **2 min** sur un autre écran ;
- 4 playlists Spotify d'exemple (Deep Focus, Lofi beats, Peaceful Piano, Top Hits). Remplace-les par les tiennes : dans Spotify, playlist > « ⋯ » > Partager > Copier le lien.

---

## 3. Brancher Google Agenda (Apps Script)

### Créer le script
1. Va sur **https://script.google.com** (connecté à ton compte Google) > **Nouveau projet**.
2. Efface tout le code présent, puis colle tout le contenu de `google-apps-script/agenda.gs`.
3. En haut, renomme le projet (par ex. « Agenda tableau de bord »), puis enregistre (icône disquette).
4. Roue dentée **Paramètres du projet** > « Fuseau horaire » : choisis **(GMT+01:00) Paris**.

### L'autoriser
5. Dans la liste des fonctions en haut, choisis `tester`, puis **Exécuter**.
6. Google demande une autorisation : choisis ton compte. Un écran « Google n'a pas validé cette application » s'affiche, c'est normal puisque c'est TON script : **Paramètres avancés > Accéder à Agenda tableau de bord (non sécurisé) > Autoriser**.
7. En bas, le « Journal d'exécution » doit afficher tes événements des 3 prochains jours.

### Le publier
8. **Déployer > Nouveau déploiement** > roue dentée « Sélectionner le type » > **Application Web**.
   - Exécuter en tant que : **Moi**
   - Qui a accès : **Tout le monde**
9. **Déployer**, puis copie l'**URL de l'application Web** (elle finit par `/exec`).
10. Colle-la dans un nouvel onglet : tu dois voir du texte qui commence par `{"ok":true,"genere":...`.

### La donner à la tablette (sans la rendre publique)
- **Recommandé** : sur la tablette, onglet **Réglages** > colle l'URL > **Enregistrer**. Elle est enregistrée **uniquement sur la tablette**.
- Plus simple pour éviter de taper une longue URL : utilise comme page de démarrage dans Fully Kiosk
  `https://TON-PSEUDO.github.io/tableau-de-bord/#agenda=` suivi de l'URL `/exec`. La page l'enregistre puis l'efface de la barre d'adresse. La partie après `#` n'est jamais envoyée à GitHub.
- Ne la mets dans `CONFIG.agenda.url` **que si ton dépôt est privé** (voir partie 4).

> ⚠️ **Confidentialité, à lire.** Toute personne qui possède cette URL peut lire les titres, horaires et noms d'agenda de tes événements des prochains jours, sans mot de passe. L'URL est longue et impossible à deviner, mais elle ne doit pas être publiée. Le script n'envoie ni descriptions ni invités, et pas les lieux (`INCLURE_LIEU = false`). En cas de fuite : **Déployer > Gérer les déploiements > Archiver**, puis crée un nouveau déploiement (nouvelle URL).

> Si tu modifies le script plus tard : **Déployer > Gérer les déploiements > ✏️ > Version : Nouvelle version**. L'URL reste la même.

**Blocage du navigateur (CORS)** : la réponse d'Apps Script est normalement lisible depuis une page web. Je n'ai pas pu le vérifier avec ton vrai compte, donc la page a un **plan B automatique** (JSONP : le script répond sous une forme que le navigateur ne bloque jamais). Si les deux échouent, Réglages > Informations > ligne « Agenda » affiche la raison.

---

## 4. Mettre en ligne sur GitHub Pages

### Ce qui devient public : lis avant de commencer
Avec un compte GitHub **gratuit**, GitHub Pages ne fonctionne qu'avec un dépôt **public**. Concrètement, **tout le monde peut voir** :
- tout le code, ton `CONFIG` (ville : Pontcarré, liens de tes playlists Spotify, horaires du mode nuit) ;
- tes cartes (`cards.json`), tes sources d'actus et l'historique de chaque modification ;
- ton pseudo GitHub, visible dans l'adresse du site.

**Ne sont pas publiés** : tes échéances (stockées sur la tablette), l'URL de ton agenda si tu la mets dans Réglages, et le contenu de ton agenda.

Un dépôt **privé** avec Pages demande un abonnement payant (GitHub Pro). Si tu ne veux pas que ta ville apparaisse, remplace-la par une ville voisine plus grande dans `CONFIG.ville`.

### Étapes
1. **Compte** : crée un compte sur https://github.com (gratuit). Choisis un pseudo qui ne révèle pas ton nom si tu préfères.
2. **Dépôt** : bouton **+** en haut à droite > **New repository**. Nom : `tableau-de-bord`. Public. Ne coche rien d'autre. **Create repository**.
3. **Envoyer les fichiers** : sur la page du dépôt, lien **uploading an existing file**. Glisse `index.html`, `cards.json`, `news.json`, `sources-actus.json`, `README.md` et le dossier `scripts`. Clique sur **Commit changes**.
4. **Le robot** : le Finder cache le dossier `.github`, donc on le crée à la main. **Add file > Create new file**. Dans le nom, tape exactement `.github/workflows/publier.yml` (les `/` créent les dossiers). Colle tout le contenu du fichier `publier.yml`, puis **Commit changes**.
   - Pour voir ce fichier sur ton Mac : dans le Finder, `Cmd + Shift + .` affiche les fichiers cachés.
   - Une croix rouge peut apparaître dans l'onglet Actions juste après : c'est normal tant que l'étape 5 n'est pas faite.
5. **Activer Pages** : **Settings > Pages >** sous « Build and deployment », Source : **GitHub Actions**.
6. **Premier lancement** : onglet **Actions** > « Actus et publication » > **Run workflow**. Attends la coche verte (1 à 2 min).
7. Ton site est en ligne à : **https://TON-PSEUDO.github.io/tableau-de-bord/**

Ensuite, le robot tourne **tout seul chaque matin vers 5h30** (6h30 en été), et à chaque fois que tu modifies un fichier sur GitHub. Tu peux modifier `CONFIG` directement sur GitHub : ouvre `index.html` > icône crayon > modifie > **Commit changes**. La tablette récupère la nouvelle version à 4h du matin, ou tout de suite avec Réglages > Recharger la page.

### Les actus
- Pour activer les thèmes **IA & tech** ou **Marketing & business** (prêts, testés, mais désactivés car tu as choisi l'actu générale), passe `"actif": false` à `"actif": true` dans `sources-actus.json`.
- Toutes les adresses de flux ont été testées le 12/11/2026. Le robot ne garde que le **titre, la source, le lien et l'heure**.
- « Gros événements internationaux » : le robot ne sait pas juger de l'importance d'une info. Il affiche simplement les titres les plus récents de la colonne International à côté de ceux de France.
- Pour une 2e mise à jour à midi, enlève le `#` devant la 2e ligne `cron` dans `publier.yml`.

### Wikipédia : résultat de mes tests
- « **Ce jour-là** » : **fonctionne** depuis le navigateur, sans blocage. C'est intégré, la page le lit directement sans passer par le robot.
- « **Article du jour** » : la version française du flux « featured » **ne le fournit pas** (le champ est vide, contrairement à la version anglaise). Je ne l'ai donc pas intégré.
- « Les plus lus » : fonctionne, mais le contenu est très aléatoire. Pas intégré.

---

## 5. Ajouter tes propres cartes

Ouvre `cards.json`. C'est une liste entre `[` et `]` ; chaque carte est un bloc `{ ... }` et les blocs sont **séparés par des virgules**. Modèle à copier-coller juste avant le `]` final :

```json
  ,{
    "theme": "Marketing",
    "question": "Ta question ?",
    "reponse": "Ta réponse.",
    "exemple": "Un exemple (facultatif, tu peux laisser \"\")."
  }
```

Règles :
- la **virgule** avant `{` est obligatoire, mais pas après la dernière carte ;
- pas de guillemet droit `"` à l'intérieur d'un texte (utilise « » ou ’) ;
- `theme` peut être ce que tu veux (« Marketing », « IA », « Anglais »…). Chaque thème devient un bouton de filtre dans l'écran Cartes.

Vérifie le fichier sur https://jsonlint.com avant de l'envoyer. Si le fichier est cassé, la page affiche un bandeau rouge et garde les anciennes cartes. La carte du jour suit un paquet mélangé sans répétition ; les nouvelles cartes s'ajoutent à la fin du paquet en cours.

---

## 6. Installer Fully Kiosk Browser sur la tablette

1. **Mets à jour le moteur web** (important sur Android 5 à 7) : Play Store > cherche **Android System WebView** (et **Chrome** sur Android 7) > Mettre à jour.
2. Installe **Fully Kiosk Browser** depuis le Play Store. Si la version du Play Store ne s'installe pas sur ta version d'Android, le site officiel fully-kiosk.com propose des versions plus anciennes.
3. Ouvre Fully, puis ses réglages (glisse depuis le bord gauche > Settings). Les noms exacts des menus changent selon les versions, et la plupart des menus ont une **loupe de recherche** :
   - **Web Content Settings > Start URL** : ton adresse GitHub Pages (éventuellement avec `#agenda=...`, voir partie 3).
   - **Toolbars & Appearance** (ou « Fullscreen ») : active le **plein écran** et masque la barre d'adresse.
   - **Device Management > Keep Screen On** : activé.
   - **Device Management > Launch on Boot** : activé, pour que Fully redémarre avec la tablette.
   - **Web Auto Reload > Auto Reload after Page Error** : 60 secondes environ. Cela couvre une coupure d'internet au démarrage.
   - **Écran éteint la nuit** : option « Schedule Wakeup / Sleep » dans Fully, qui fait partie des fonctions **PLUS (payantes)**. En version gratuite, la page passe seulement en thème très sombre.
   - **Luminosité automatique la nuit** : nécessite **Advanced Web Settings > Enable JavaScript Interface**, aussi une fonction **PLUS**. Sans elle, la page s'assombrit mais le rétroéclairage reste allumé.
   - N'active **pas** le « Kiosk Mode » (verrouillage) au début, ou alors avec un code PIN que tu notes, pour ne pas te retrouver bloqué.
4. Teste un bouton **Musique**. Si Spotify ne s'ouvre pas, va dans Réglages et essaie « Lien spotify: » puis « Lien web ». Si besoin, cherche dans les réglages de Fully une option liée aux « intent » ou aux « other apps ».
5. Dans **Réglages > Informations**, note la ligne « Moteur web : Chrome XX ». Si elle indique moins de 50, dis-le-moi.

> 🔋 **Batterie** : une vieille tablette branchée en permanence peut voir sa batterie **gonfler**. Vérifie de temps en temps que l'écran ou la coque ne se soulève pas. Si ta tablette propose une option « protéger la batterie » (limite de charge à 85 %), active-la.

---

## 7. Ce qui n'a pas pu être testé, et ce qui risque de poser problème

Testé sur ordinateur (Chrome, écrans de 1024 × 600 et 1280 × 800) : horloge, météo réelle de Pontcarré, frise avec des données au format de l'agenda, actus, « Ce jour-là », cartes, révision automatique, échéances, mode nuit, réglages, aucune erreur dans la console. Le robot d'actus a tourné sur mon ordinateur : 8 sources sur 8 OK.

**Pas testé sur la vraie tablette :**
1. **Vieux moteur web** : le code est écrit en JavaScript ancien (ES5, sans `fetch`, sans variables CSS, sans grille CSS). Il devrait marcher avec un WebView récent ; avec un WebView jamais mis à jour (Chrome 37 à 40), c'est probable mais pas garanti. En cas de problème, un message s'affiche au lieu d'un écran blanc.
2. **Agenda Apps Script** : pas testé avec ton compte. Le plan B (JSONP) est en place.
3. **Ouverture de Spotify** depuis Fully Kiosk : c'est le point le plus **fragile**. Ça dépend de Fully et de ta version de Spotify, d'où les 3 méthodes dans Réglages. Les vieilles versions d'Android ne sont parfois plus prises en charge par l'appli Spotify elle-même.
4. **Luminosité et extinction de l'écran la nuit** : demandent Fully PLUS (payant). Sans lui, il y a seulement un thème sombre, et un écran LCD allumé reste éclairé.
5. **Taille du texte** : la mise en page s'adapte à l'écran, mais sur un 7 pouces le texte des actus sera petit. Tout se règle dans `index.html` : cherche `html { font-size: 2.3vmin; }` et augmente un peu.
6. **Clavier à l'écran** sur l'écran Échéances : il peut tasser la page pendant la saisie. Ce n'est pas grave.
7. **Robot GitHub** : les tâches planifiées peuvent avoir du retard, et GitHub **désactive les tâches planifiées après 60 jours sans activité** sur le dépôt. Le robot enregistre `news.json` chaque jour, ce qui devrait compter comme de l'activité. Si un jour les actus restent marquées ⚠ (plus de 36 h), va dans Actions et clique « Enable workflow ».
8. **Flux RSS** : un média peut changer l'adresse de son flux. La source concernée disparaît alors, et l'erreur est notée dans `news.json` (champ `erreurs`).

## 8. Dépannage rapide
- **Écran blanc ou bandeau rouge** : Réglages > Informations > « Erreurs ».
- **« hors ligne »** en haut de l'horloge : la météo n'a pas pu être mise à jour. Les dernières données restent affichées.
- **L'agenda montre des EXEMPLES** : l'URL n'est pas enregistrée sur cet appareil (partie 3).
- **Le robot échoue** (croix rouge dans Actions) : clique dessus pour lire l'erreur. Vérifie Settings > Pages > Source = GitHub Actions.
