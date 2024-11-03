const ENDPOINT_URL = 'ENDPOINT';

function onFormSubmit(e) {
  UrlFetchApp.fetch(ENDPOINT_URL, {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({}),
  });
}

function setupTrigger() {
  const form = FormApp.openById('YOUR_FORM_ID');
  ScriptApp.newTrigger('onFormSubmit')
    .forForm(form)
    .onFormSubmit()
    .create();
}
