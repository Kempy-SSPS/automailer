# Automailer
Jednoduchá toolka na automatizaci odesílání potvrzovacích emailů.

## Dokumentace

### Při vytváření formuláře
- V průběhu sbírání přihlášek se **NESMÍ** měnit pořadí otázek ve fromuláři
- Otázka na vybírání události a termínu musí být typu `Radio`
- Každá možnost v `Radio` otázce musí mít unikátní název, který je zapsaný v `config/events.json`


### Propojení s Google Forms
- Do `config/credentials.json` stáhnout json soubor Google service účtu z [Google cloud console](https://console.cloud.google.com)
- Po vytvoření formuláře, zapnout exportování do Google Sheets tabulky
- Pojmenovat list `sheet`
- V UI Google Sheets nasdílet tabulku uživateli `client_email` v souboru `config/credentials.json`
- Do dotenvu zadat `SPREADSHEET_ID` a `RANGE_NAME`

### Před spuštěním
- Do `config/events.json` zadat všechny události a jejich maximální kapacitu, datum a typ

### Spuštění
- Pokud máte dostatečně novou verzi dockeru, stačí `docker compose up -d --build`