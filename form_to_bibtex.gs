function onFormSubmit(e) {
  // Google script file to convert submitted forms to BibTeX and send them via mail
  //
  // Replace event information with dummy to test and debug
  /*
  e = e || {
    namedValues: {
      'Publikationstyp': ['Journal'],
      'Autoren': ['John Doe'],
      'Papertitel': ['Test Paper'],
      'Name Journal': ['Test Journal'],
      'Name Konferenz': ['Test Conference'],
      'Ort': ['Karlsruhe'],
      'Jahr': ['2023'],
      'Volume': ['1'],
      'Number': ['1'],
      'pages': ['1--10'],
      'DOI': ['10.0000/test.2023.0001'],
    },
  };*/
  var responses = e.namedValues;
  
  // Map form fields to BibTeX fields
  var bibType = responses['Publikationstyp'][0];
  var author = responses['Autoren'][0];
  var title = responses['Papertitel'][0];
  var journal = responses['Name Journal'][0];
  var booktitle = responses['Name Konferenz'][0];
  var address = responses['Ort'][0];
  var year = responses['Jahr'][0];
  var volume = responses['Volume'][0];
  var number = responses['Number'][0];
  var pages = responses['pages'][0];
  var doi = responses['DOI'][0];

  // Create a BibTeX entry
  var bibEntry = '@' + bibType + '{' + author.replace(/ /g, '') + year + ',\n';
  bibEntry += '  author = {' + author + '},\n';
  bibEntry += '  title = {' + title + '},\n';

  if (bibType === 'article') {
    bibEntry += '  journal = {' + journal + '},\n';
  } else if (bibType === 'inproceedings') {
    bibEntry += '  booktitle = {' + booktitle + '},\n';
    bibEntry += '  address = {' + address + '},\n';
  }

  bibEntry += '  year = {' + year + '},\n';
  bibEntry += '  volume = {' + volume + '},\n';
  bibEntry += '  number = {' + number + '},\n';
  bibEntry += '  pages = {' + pages + '},\n';
  bibEntry += '  doi = {' + doi + '},\n';
  bibEntry += '}\n';

  var fromAddress = 'pfaff@kit.edu';
  var emailAddress = 'sascha.faber@kit.edu';
  var ccAddress = 'pfaff@kit.edu';
  var subject = 'Neuer BibTeX Eintrag: ' + title;
  var message = 'Hier der neue BibTeX Eintrag:\n\n' + bibEntry;

  sendEmailWithAlias(emailAddress, fromAddress, ccAddress, subject, message);
}

function sendEmailWithAlias(to, from, cc, subject, body) {
  var rawEmail = [
    'From: ', from, '\r\n',
    'To: ', to, '\r\n',
    'Cc: ', cc, '\r\n',
    'Subject: =?utf-8?B?', Utilities.base64Encode(subject, Utilities.Charset.UTF_8), '?=', '\r\n',
    'MIME-Version: 1.0\r\n',
    'Content-Type: text/plain; charset=UTF-8\r\n\r\n',
    body,
  ].join('');

  Gmail.Users.Messages.send({
    raw: Utilities.base64EncodeWebSafe(rawEmail)
  }, 'me');
}

function setup() {
  var sheet = SpreadsheetApp.getActive();
  ScriptApp.newTrigger('onFormSubmit')
    .forSpreadsheet(sheet)
    .onFormSubmit()
    .create();
}
