/**
 * Agenda Google -> JSON pour le tableau de bord.
 * À copier-coller dans https://script.google.com (voir README, partie « Agenda »).
 *
 * Ce script lit TES agendas Google et renvoie les événements des prochains jours.
 * Il ne renvoie que : titre, début, fin, « journée entière », lieu (optionnel),
 * nom et couleur de l'agenda. Jamais les descriptions ni les invités.
 */

// ----- Réglages -----
var JOURS_PAR_DEFAUT = 7;     // nombre de jours renvoyés (la page peut en demander jusqu'à 31)
var NOMS_AGENDAS = [];        // vide = tous tes agendas visibles. Sinon par ex. ["Perso", "Cours"]
var INCLURE_LIEU = false;     // true pour envoyer aussi le lieu des événements
var MASQUER_REFUSES = true;   // n'affiche pas les invitations que tu as refusées

// Palette des couleurs d'événement de Google Agenda (numéro -> couleur)
var COULEURS_EVENEMENT = {
  '1': '#7986cb', '2': '#33b679', '3': '#8e24aa', '4': '#e67c73', '5': '#f6bf26', '6': '#f4511e',
  '7': '#039be5', '8': '#616161', '9': '#3f51b5', '10': '#0b8043', '11': '#d50000'
};

function doGet(e) {
  var p = (e && e.parameter) || {};
  var jours = Math.min(Math.max(parseInt(p.jours, 10) || JOURS_PAR_DEFAUT, 1), 31);
  var json = JSON.stringify(lireEvenements(jours));
  // Mode JSONP (plan B utilisé par la page si la lecture directe est bloquée)
  if (p.callback && /^[A-Za-z_$][\w$]{0,63}$/.test(p.callback)) {
    return ContentService.createTextOutput(p.callback + '(' + json + ');')
      .setMimeType(ContentService.MimeType.JAVASCRIPT);
  }
  return ContentService.createTextOutput(json).setMimeType(ContentService.MimeType.JSON);
}

function lireEvenements(jours) {
  var cache = CacheService.getScriptCache();
  var cle = 'evenements_' + jours;
  var enCache = cache.get(cle);
  if (enCache) return JSON.parse(enCache);

  var maintenant = new Date();
  var debut = new Date(maintenant.getFullYear(), maintenant.getMonth(), maintenant.getDate());
  var fin = new Date(debut.getTime());
  fin.setDate(fin.getDate() + jours);

  var liste = [];
  CalendarApp.getAllCalendars().forEach(function (agenda) {
    if (NOMS_AGENDAS.length && NOMS_AGENDAS.indexOf(agenda.getName()) < 0) return;
    if (!NOMS_AGENDAS.length && agenda.isHidden()) return;
    agenda.getEvents(debut, fin).forEach(function (ev) {
      if (MASQUER_REFUSES) {
        try { if (ev.getMyStatus() === CalendarApp.GuestStatus.NO) return; } catch (x) {}
      }
      var journee = ev.isAllDayEvent();
      var d = journee ? ev.getAllDayStartDate() : ev.getStartTime();
      var f = journee ? ev.getAllDayEndDate() : ev.getEndTime();
      liste.push({
        titre: ev.getTitle() || '(sans titre)',
        debut: d.getTime(),
        fin: f.getTime(),
        journee: journee,
        lieu: INCLURE_LIEU ? (ev.getLocation() || '') : '',
        agenda: agenda.getName(),
        // Couleur de l'événement s'il en a une, sinon celle de l'agenda
        couleur: COULEURS_EVENEMENT[ev.getColor()] || agenda.getColor()
      });
    });
  });
  liste.sort(function (a, b) { return a.debut - b.debut; });

  var resultat = { ok: true, genere: Date.now(), evenements: liste };
  try { cache.put(cle, JSON.stringify(resultat), 300); } catch (x) {}  // cache 5 min
  return resultat;
}

/** Pour tester dans l'éditeur : sélectionne « tester » puis « Exécuter », et regarde le journal. */
function tester() {
  Logger.log(JSON.stringify(lireEvenements(3), null, 2));
}
