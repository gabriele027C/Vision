# PLAYBOOK VISION — Checklist di disciplina per scenario

> **Natura di questo documento.** Ogni scheda è descrittiva e condizionale: dice cosa
> verificare e cosa ti smentisce, mai cosa succederà. Nessuno scenario ha edge
> statistico dimostrato. La decisione e il rischio restano tuoi: il size arriva
> sempre e solo dal pannello rischio (1% max, check liquidazione).
>
> **Legenda.** OI = open interest. CVD = cumulative volume delta (aggressori).
> ↑/↓/→ = in salita / in discesa / laterale-piatto. TF = timeframe.
> Il lato operativo di Vision è **solo long**: gli scenari ribassisti sono schede
> di protezione e attesa, non di ingresso short.

---

## COME USARE IL PLAYBOOK

1. La watchlist ti dice **dove guardare**. La scheda scenario ti dice **cosa verificare**.
2. Prima di ogni ingresso, esegui la **Checklist universale pre-ingresso** (in fondo)
   PIÙ la scheda dello scenario attivo.
3. Registra sempre lo `scenario_id` nel journal: tra 100 trade sapremo in quali
   scenari la TUA lettura produce expectancy positiva. Quello è l'unico edge
   che stiamo cercando di misurare.

---

# FAMIGLIA A — TREND ATTIVO (prezzo ↑)

## A1 · `trend_nuovi_aggressori` — prezzo↑ + OI↑ + CVD↑

**Lettura.** Il movimento è alimentato da posizioni nuove aperte in acquisto
aggressivo: la partecipazione conferma il trend. È lo scenario strutturalmente
più sano — e proprio per questo il più affollato.

**Monitorare prima di un ingresso**
- [ ] Il pullback in corso tiene sopra EMA20 (o la zona EMA20-50) con CVD che
      rallenta ma **non inverte**: la pausa deve essere assenza di venditori,
      non presenza di distribuzione.
- [ ] Funding non in accelerazione verso l'estremo: se entri quando il funding
      esplode, paghi il carry dei ritardatari e ti esponi al long squeeze.
- [ ] Su 1H/15m: compressione sopra un supporto, non estensione verticale.
      L'ingresso ha senso vicino a una base, mai a metà di una gamba.
- [ ] OI in salita *insieme* al prezzo, non in salita col prezzo fermo
      (quello è scenario B3, leggilo).

**Invalidazione dello scenario.** OI continua a salire ma il prezzo smette di
seguirlo, o CVD inverte sul massimo: possibile assorbimento in distribuzione.
Se hai una posizione, quella combinazione è il tuo campanello.

**Errore tipico.** Inseguire l'estensione per paura di perdere il treno.
In questo scenario il rischio principale non è restare fuori: è salire nel
punto dove chi è entrato prima inizia a scaricare su di te.

---

## A2 · `short_covering` — prezzo↑ + OI↓

**Lettura.** Il prezzo sale perché gli short chiudono, non perché entrano
compratori nuovi: il carburante è finito quando finiscono i ricoperti.
Rally veloce, base fragile.

**Monitorare prima di un ingresso**
- [ ] Attendere che l'OI **smetta di scendere**: solo lì scopri se esiste
      domanda vera oltre alle ricoperture.
- [ ] Se il rally regge a OI stabilizzato e il CVD resta positivo, lo scenario
      può evolvere in A1: rivaluta con quella scheda, non con questa.
- [ ] Confronto spot vs perp se disponibile: uno spot che compra durante il
      covering è più solido di un movimento solo-perp.
- [ ] Livelli sopra la testa: i covering rally muoiono spesso sulla prima
      resistenza strutturale daily.

**Invalidazione dello scenario.** Stallo del prezzo con OI ormai piatto: la
spinta era solo tecnica ed è esaurita.

**Errore tipico.** Scambiare un rally di ricoperture per l'inizio di un trend
e comprarne la parte finale. La velocità del movimento non è qualità del
movimento.

---

## A3 · `trend_senza_aggressori` — prezzo↑ + OI→ + CVD→/↓

**Lettura.** Il prezzo sale ma né posizioni nuove né flusso aggressivo lo
accompagnano: salita in assenza di venditori (vuoto d'offerta), tipica dei
weekend o dei momenti illiquidi. Regge finché non incontra offerta vera.

**Monitorare prima di un ingresso**
- [ ] RVOL della fascia oraria: se la salita avviene con volumi molto sotto
      media, il primo flusso reale in vendita può cancellarla.
- [ ] Come reagisce il prezzo al primo aumento di volume: assorbe o cede?
- [ ] Evitare ingressi in orari morti sulla sola forza apparente del grafico.

**Invalidazione dello scenario.** Primo impatto con volume in vendita che il
prezzo non assorbe.

**Errore tipico.** Leggere la salita "pulita e senza ritracci" come forza.
Senza partecipazione, la pulizia del grafico è fragilità, non qualità.

---

## A4 · `divergenza_aggressori` — prezzo↑ + CVD↓ (OI qualsiasi)

**Lettura.** Il prezzo segna massimi ma gli aggressori netti stanno vendendo:
qualcuno sta usando la salita per uscire (o il movimento è tenuto su dai
limit buyer passivi). Divergenza classica da fine gamba — che però può
durare più del previsto.

**Monitorare prima di un ingresso**
- [ ] Non aprire ingressi nuovi sulla divergenza attiva: attendere che si
      risolva (CVD torna a confermare, o il prezzo ritraccia e riparte da una base).
- [ ] Se sei già in posizione: è il momento di stringere la gestione, non di
      aggiungere.
- [ ] Verifica multi-TF: una divergenza solo su 15m pesa poco; su 4H/D pesa.

**Invalidazione dello scenario.** Il CVD torna a salire coi nuovi massimi:
la divergenza è rientrata.

**Errore tipico.** Due opposti: ignorarla del tutto, o usarla per shortare
(il lato short non è operativo in Vision — e le divergenze nei trend forti
falliscono spesso).

---

# FAMIGLIA B — LATERALE / COMPRESSIONE (prezzo →)

## B1 · `possibile_assorbimento` — prezzo→ + CVD↑

**Lettura.** Vendita aggressiva assente o assorbita: il prezzo non sale
ancora, ma il flusso comprа. Se è accumulo, la conferma arriva SOLO con la
rottura del range e il mancato rientro. Fino ad allora è un'ipotesi.

**Monitorare prima di un ingresso**
- [ ] La reazione alla rottura del range: rompe, ritesta, tiene? Quella è la
      sequenza che trasforma l'ipotesi in fatto.
- [ ] RVOL sulla barra di rottura: una rottura da assorbimento senza volume
      è sospetta (vedi C2).
- [ ] Dove sta il range rispetto alla struttura daily: assorbimento sopra
      supporto maggiore vale più di uno a metà del nulla.
- [ ] OI durante il laterale: OI↑ con prezzo fermo aggiunge tensione (B3).

**Invalidazione dello scenario.** Cedimento del minimo del range con CVD che
inverte: quello che sembrava assorbimento era distribuzione con buyer passivi.

**Errore tipico.** Anticipare la rottura posizionandosi dentro il range "per
avere il prezzo migliore". Dentro il range non c'è ancora nessuna conferma:
c'è solo un'idea che ti piace.

---

## B2 · `possibile_distribuzione` — prezzo→ + CVD↓

**Lettura.** Il prezzo tiene ma il flusso aggressivo vende: qualcuno assorbe
in acquisto passivo, oppure l'offerta sta lentamente vincendo. Speculare a B1,
con lettura ribassista. **Scheda di protezione: nessun ingresso long.**

**Monitorare (per protezione, non per ingresso)**
- [ ] Se hai posizione long aperta sull'asset: il minimo del range è il tuo
      livello di sorveglianza attiva.
- [ ] Se il prezzo rompe al rialzo *nonostante* il CVD negativo, non inseguire:
      pretendi il ritest (probabile trappola, vedi C2).

**Invalidazione dello scenario.** CVD che torna positivo con il prezzo che
accetta la parte alta del range.

**Errore tipico.** Comprare "lo sconto" dentro un laterale dove il flusso
vende, perché il prezzo "ha tenuto finora".

---

## B3 · `molla_carica` — prezzo→ + OI↑ (CVD qualsiasi)

**Lettura.** Posizionamento in crescita su prezzo fermo: le due parti si
stanno caricando una contro l'altra dentro il range. Quando rompe, il lato
sbagliato alimenta il movimento (squeeze). Direzione ignota per definizione.

**Monitorare prima di un ingresso**
- [ ] NESSUN ingresso finché non rompe: questo scenario è un'allerta di
      volatilità imminente, non un'indicazione di direzione.
- [ ] Preparare i livelli: sopra e sotto il range, con l'invalidazione già
      calcolata dal pannello rischio per l'eventuale rottura long.
- [ ] Funding come indizio di sbilanciamento: funding molto positivo con
      prezzo fermo = più carburante per il ribasso, e viceversa.
- [ ] Squeeze Bollinger attivo su D o 4H rafforza la lettura "molla".

**Invalidazione dello scenario.** OI che si sgonfia senza rottura: la
tensione si è scaricata in silenzio.

**Errore tipico.** Scommettere sulla direzione della rottura prima della
rottura. La molla non ha direzione: ha solo energia.

---

## B4 · `squeeze_multi_tf` — compressione D/4H + compressione 1H/15m allineate

**Lettura.** Bassa volatilità annidata su più timeframe: le espansioni
migliori nascono spesso così. Scenario di massima attenzione e minima azione.

**Monitorare prima di un ingresso**
- [ ] Il livello di rottura del TF superiore comanda: le rotture dei TF bassi
      dentro il range daily sono rumore fino a prova contraria.
- [ ] CVD e OI durante la compressione (incrocia con B1/B2/B3 per capire chi
      si sta posizionando).
- [ ] RVOL alla rottura: la fine di uno squeeze multi-TF senza volume è il
      falso segnale per eccellenza.

**Invalidazione dello scenario.** Espansione di volatilità già avvenuta
(range della barra ≥ 2× ATR): lo squeeze è finito, sei in ritardo — cambia
scheda, non inseguire.

**Errore tipico.** Farsi richiamare dall'ingresso sul 15m mentre il daily non ha ancora
deciso. Il TF piccolo dentro un TF grande compresso produce decine di falsi.

---

# FAMIGLIA C — EVENTI DI ROTTURA

## C1 · `rottura_con_partecipazione` — rottura range + CVD↑ + RVOL alto (+OI↑)

**Lettura.** La rottura ha aggressori, volume e posizioni nuove: è la
versione "da manuale". Il che non la rende sicura: la rende leggibile.

**Monitorare prima di un ingresso**
- [ ] Chiusura della barra del TF di riferimento OLTRE il livello (la lezione
      più solida della nostra intera ricerca: il tocco intrabarra non basta,
      la chiusura conta).
- [ ] Se l'ingresso non è sulla rottura: attendere il ritest del livello e la
      sua tenuta. Ritest che tiene > rincorsa.
- [ ] Distanza dall'invalidazione in ATR del TF: se lo stop "giusto" implica
      un rischio troppo ampio, il trade non c'è, per quanto bello lo scenario.
- [ ] Funding e OI post-rottura: OI che sale col prezzo conferma (A1),
      OI piatto = rottura ancora da dimostrare.

**Invalidazione dello scenario.** Rientro nel range entro poche barre del TF
di rottura: rottura fallita — che è un'informazione contraria forte.

**Errore tipico.** Considerare la qualità dello scenario un permesso per
aumentare il size. La qualità della lettura non cambia la matematica del
rischio: 1%, sempre.

---

## C2 · `rottura_senza_aggressori` — rottura range + CVD→ + RVOL basso

**Lettura.** Il prezzo esce dal range ma nessuno lo spinge: rottura tecnica
senza partecipazione, candidata trappola. È il pattern che, senza filtro di
chiusura, distruggeva il nostro Setup B nel backtest.

**Monitorare prima di un ingresso**
- [ ] NON entrare sulla rottura: pretendere chiusura oltre il livello E
      ritest che tiene, in quest'ordine.
- [ ] OI in salita mentre il prezzo rientra nel range = trappola che si
      chiude sui late buyer: massima allerta.
- [ ] Se compaiono volume e CVD dopo la rottura, riclassifica in C1 e usa
      quella checklist.

**Invalidazione dello scenario (in senso favorevole).** Arrivo di
partecipazione reale che converte la rottura: da lì vale C1.

**Errore tipico.** FOMO sulla rottura "perché il livello era importante".
L'importanza del livello senza aggressori è esattamente ciò che rende
profittevole la trappola per chi la tende.

---

## C3 · `rottura_fallita` — rientro nel range dopo la rottura

**Lettura.** Il mercato ha testato la direzione e l'ha rifiutata: i comprati
sulla rottura sono intrappolati. Informazione contraria di prima qualità.

**Monitorare (protezione e pazienza)**
- [ ] Se eri entrato sulla rottura: l'invalidazione è l'invalidazione. Il
      rientro nel range È il fallimento della tesi — uscire non è opinabile.
- [ ] Nessun re-ingresso immediato "perché ormai è scesa": il fallimento di
      una rottura long spesso genera l'escursione opposta (che non tradiamo,
      ma che non vogliamo prenderci in faccia).
- [ ] L'asset resta in watchlist: un range che ha bruciato una rottura è un
      range più leggibile, non meno.

**Errore tipico.** Mediare o "dare un'altra possibilità" al trade fallito.
La rottura fallita non è sfortuna: è il mercato che risponde alla domanda.

---

## C4 · `gap_o_spike_di_apertura` — barra con range ≥ 2×ATR oltre un livello

**Lettura.** Il movimento che aspettavi è avvenuto in una barra sola: il
rapporto rischio/struttura è saltato. Scenario di rinuncia attiva.

**Monitorare**
- [ ] Nessun ingresso in estensione: l'invalidazione strutturale è ormai a
      distanza proibitiva (il pannello rischio te lo mostrerà da solo).
- [ ] Attendere la costruzione di una NUOVA base sopra il livello rotto
      (compressione 1H/15m): quella, se arriva, è un trade; lo spike no.

**Errore tipico.** "Ormai è partita, entro con stop stretto sotto un livello
qualsiasi." Stop tecnico inesistente = trade inesistente.

---

# FAMIGLIA D — PULLBACK NEL TREND

## D1 · `pullback_ordinato` — trend allineato + ritracciamento su EMA20-50, volume in contrazione

**Lettura.** La pausa fisiologica del trend: volumi che si sgonfiano nel
ritracciamento suggeriscono assenza di distribuzione. È il vecchio Setup A,
oggi degradato a descrizione onesta: contesto leggibile, non promessa.

**Monitorare prima di un ingresso**
- [ ] CVD durante il pullback: deve *rallentare*, non invertire con forza.
      Pullback con CVD in crollo = D2.
- [ ] Segnale di ripartenza sul TF operativo (ripresa sopra un massimo
      minore, con RVOL che torna): l'ingresso "al volo nella zona" senza
      segno di ripartenza è anticipazione.
- [ ] Struttura del pullback: ordinato e in contro-pendenza dolce, oppure
      verticale e impulsivo? Il secondo non è un pullback, è un cambio di
      carattere.
- [ ] Funding raffreddato rispetto al picco della gamba precedente: il
      pullback che sgonfia il funding è doppiamente utile.

**Invalidazione dello scenario.** Perdita della zona EMA50 in chiusura del
TF di riferimento, o CVD che inverte stabilmente.

**Errore tipico.** Comprare "il prezzo scontato" al primo tocco della EMA
senza alcun segno di ripartenza, trasformando un pullback in un coltello.

---

## D2 · `pullback_con_flusso_contrario` — ritracciamento + CVD↓ deciso / OI↑ in discesa

**Lettura.** Il ritracciamento ha aggressori in vendita o posizioni nuove
che scommettono contro: non è (ancora) la pausa fisiologica di D1. Può
diventarlo, ma oggi il flusso dice altro.

**Monitorare (attesa, non ingresso)**
- [ ] Dove si ferma: la tenuta della EMA50/base precedente CON esaurimento
      del CVD in vendita è ciò che riabilita D1.
- [ ] OI: se sale mentre il prezzo scende, si stanno accumulando short — la
      loro eventuale ricopertura (A2) sarà il primo rally, da non scambiare
      per ripartenza del trend.

**Invalidazione dello scenario (favorevole).** Esaurimento del flusso in
vendita su un supporto strutturale: passa alla checklist D1.

**Errore tipico.** "È il solito pullback, compro." Il pullback è "solito"
solo a posteriori: mentre accade, il flusso è l'unico testimone attendibile.

---

# FAMIGLIA E — FUNDING E POSIZIONAMENTO

## E1 · `carry_avverso` — funding estremo contro il lato long

**Lettura.** Essere long qui costa carry strutturale e ti mette dalla parte
affollata della barca: il long squeeze punisce esattamente questa folla.
Scheda di solo avvertimento — il badge rosso in watchlist viene da qui.

**Monitorare**
- [ ] Niente da monitorare per un ingresso: c'è da NON entrare finché il
      funding non si normalizza, o da accettare esplicitamente il costo
      annotandolo nel journal (campo funding_at_entry).
- [ ] Se sei già in posizione: il funding estremo prolungato erode l'R del
      trade — ricalcola il target netto.

**Errore tipico.** "Il grafico è bello, il funding non conta." Il funding è
il prezzo del consenso: quando è estremo, stai pagando per avere l'opinione
di tutti.

---

## E2 · `funding_negativo_in_trend_su` — prezzo↑ + funding ≤ 0

**Lettura.** Il mercato sale mentre i perp pagano per stare short: la folla
è contro il movimento, il carry è a favore del long. Delle letture di
posizionamento è la più interessante per il nostro lato operativo.

**Monitorare prima di un ingresso**
- [ ] Vale tutto A1/D1: il funding favorevole non sostituisce la struttura,
      la accompagna.
- [ ] La normalizzazione del funding verso l'alto durante la salita è il
      segnale che il vantaggio di posizionamento si sta consumando.

**Errore tipico.** Trattare il funding negativo come segnale d'ingresso
autonomo. È un vento a favore, non un motore.

---

## E3 · `flip_del_funding` — cambio di segno rapido dopo un periodo estremo

**Lettura.** Il posizionamento si sta riequilibrando, spesso durante o dopo
uno squeeze. Fase di transizione: la lettura precedente è scaduta, la nuova
non è ancora scritta.

**Monitorare**
- [ ] Sospendere le conclusioni per qualche barra 4H: lasciare che OI, CVD e
      struttura ridefiniscano lo scenario, poi riclassificare.

**Errore tipico.** Reagire al flip come fosse un segnale, in una fase che
per definizione è rumorosa.

---

# FAMIGLIA F — CONTESTO RIBASSISTA (schede di sola protezione)

## F1 · `tendenza_ribassista_strutturata` — prezzo sotto EMA200, allineamento ribassista

**Lettura.** Il lato long non ha contesto. Vision non opera short: qui il
lavoro è proteggere capitale e attenzione.

**Checklist**
- [ ] L'asset esce dalla watchlist operativa (resta nel tab contesto).
- [ ] Nessun "bottom fishing" su livelli tondi o su ipervenduto: senza
      struttura di accumulo (B1 che matura su base daily), non c'è scheda.
- [ ] L'unico percorso di ritorno all'operatività: base + assorbimento +
      rottura con partecipazione (B1 → C1), che richiede settimane, non barre.

**Errore tipico.** Comprare la discesa "perché è scesa tanto". Il prezzo
basso non è un livello: è solo un prezzo più basso.

---

## F2 · `capitolazione` — barre giganti in discesa + OI in crollo + volume estremo

**Lettura.** Liquidazioni a cascata: le posizioni vengono chiuse d'ufficio.
Volatilità massima, spread larghi, stop inaffidabili. Zona proibita.

**Checklist**
- [ ] Nessuna operatività durante l'evento: anche i livelli "ovvi" filano
      via per punti percentuali interi.
- [ ] Dopo l'evento: OI azzerato + primo laterale = terreno fertile per B1
      nei giorni successivi. È lì che si torna a guardare, non durante.

**Errore tipico.** Provare a prendere il minimo dentro la cascata con la
leva. È il singolo comportamento che cancella i conti retail.

---

# CHECKLIST UNIVERSALI (valgono SEMPRE, in aggiunta alla scheda scenario)

## U1 · Pre-ingresso — da completare per intero, nessuna eccezione

- [ ] Lo scenario attivo è identificato e ho letto la sua scheda ADESSO
      (non a memoria).
- [ ] Il livello di invalidazione è STRUTTURALE (sotto una base/livello del
      TF di riferimento), non "dove lo stop costa poco".
- [ ] Size dal pannello rischio: rischio ≤ 1%, leva entro il cap,
      `liq_safe` verde. Se il pannello blocca, il trade NON esiste.
- [ ] Costi stimati (fee + funding previsto per la durata attesa) guardati
      in faccia: so quanto del mio R se ne va in attrito.
- [ ] So DOVE esco in profitto o con quale logica (target fisso, trailing,
      a struttura): deciso ORA, non durante.
- [ ] Ho controllato il TF sopra quello operativo: non sto comprando un
      breakout 15m dentro una resistenza daily.
- [ ] Se ho già una posizione correlata aperta (stesso settore/beta BTC),
      il rischio aggregato resta accettabile.
- [ ] Journal precompilato: scenario_id, timeframe, pattern, contesto
      (OI/CVD/funding/RVOL). Se non ho voglia di compilarlo, non ho voglia
      di fare trading serio oggi — ed è un'informazione anche quella.

## U2 · In posizione

- [ ] L'invalidazione non si sposta MAI contro di me. Mai. La gestione
      attiva può solo ridurre il rischio, non aumentarlo.
- [ ] Rileggo lo scenario a ogni chiusura di barra del TF di riferimento:
      se lo scenario che motivava il trade è invalidato, il trade è finito
      anche se lo stop non è stato toccato.
- [ ] Niente aggiunte in perdita. Le aggiunte in profitto solo se previste
      PRIMA dell'ingresso, con rischio totale ricalcolato.
- [ ] Funding check giornaliero sulle posizioni overnight.

## U3 · Post-uscita (2 minuti, sempre)

- [ ] Journal completato: esito, MAE/MFE, e UNA riga onesta — ho seguito la
      checklist o no? (Il journal misura la mia disciplina prima ancora del
      mio edge.)
- [ ] Se ho violato una regola: quale, e cosa la rende attraente da violare.
      La violazione ricorrente è il dato più prezioso del journal.
- [ ] Nessun re-ingresso sullo stesso asset entro la stessa barra del TF
      operativo (anti-revenge, hard rule).

## U4 · Routine giornaliera (10 minuti)

- [ ] Watchlist del mattino: leggo il PERCHÉ di ogni riga (situazione +
      confluenza), non solo i nomi.
- [ ] Regime banner e funding di mercato: contesto della giornata.
- [ ] Massimo 2-3 asset in sorveglianza attiva: oltre, l'attenzione è
      un'illusione.
- [ ] Un giorno a drawdown giornaliero ≥ 2R chiude l'operatività fino a
      domani. La regola vale soprattutto quando non vorresti applicarla.

---

*Ogni scheda termina idealmente con la stessa verità: scenario descrittivo,
nessun edge statistico dimostrato. La decisione e il rischio restano tuoi —
size dal pannello rischio. Il playbook non ti dice quando hai ragione:
ti impedisce di perdere nel modo stupido mentre scopri se ce l'hai.*
