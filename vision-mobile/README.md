# Vision TVS — Mobile (Expo / React Native)

App mobile standalone per la strategia **TVS**: stesso motore di `src/backend`
(portato in TypeScript), dati da Binance e Yahoo Finance, SQLite locale,
scanner automatico e schermate Dashboard, Watchlist, Diagnostics, Planner,
Journal e Settings.

## Requisiti

- Node.js 18+
- [Expo Go](https://expo.dev/go) (SDK 54) per sviluppo, oppure APK buildato con EAS

## Avvio (sviluppo)

```bash
npm install
npm run start:clear
```

Scansiona il QR code con Expo Go (telefono e PC sulla stessa rete Wi‑Fi).
URL manuale tipico: `exp://<IP-LAN>:8081`.

## Build APK (standalone)

```bash
eas build --platform android --profile preview
```

Configurazione in `eas.json`. Package Android: `com.vision.tvs`.

## Licenza

Copyright © 2025-2026 Gabriele. **Tutti i diritti riservati.**

Questo software è rilasciato con **licenza duale** per il codice Vision:

| Uso | Condizioni |
|-----|------------|
| **Personale / non commerciale** | Gratuito per studio, ricerca privata e uso personale (nessun guadagno derivato dal software). Vietata redistribuzione e uso aziendale senza accordo. |
| **Commerciale** | Richiede **licenza commerciale scritta** (aziende, SaaS, rivendita, white-label, uso interno in organizzazioni a scopo di lucro). |

- Testo Vision: [`LICENSE`](./LICENSE) e [`../LICENSE`](../LICENSE) (root)
- **Licenza MIT (Expo template):** [`LICENSE-MIT`](./LICENSE-MIT) — mantenuta come in origine (Copyright 650 Industries, Inc.)

**Licenza commerciale Vision:** gabriele02744@gmail.com — oggetto: *Vision — Commercial License Request*.

Le altre dipendenze npm (Expo, React Native, ecc.) restano soggette alle rispettive licenze open source.
