/**
 * Google Apps Script - Rehearsal Room Booking Backend
 *
 * SETUP INSTRUCTIONS:
 * 1. Go to https://sheets.google.com and create a new spreadsheet
 * 2. Name it "Rehearsal Room Bookings"
 * 3. In the first row (header), add these columns:
 *    A: Date | B: Time | C: Duration | D: Name | E: Email | F: Phone | G: Notes | H: Timestamp | I: Amount
 * 4. Go to Extensions > Apps Script
 * 5. Delete the default code and paste this entire file
 * 6. Click Deploy > New deployment
 * 7. Select type: Web app
 * 8. Set "Execute as": Me
 * 9. Set "Who has access": Anyone
 * 10. Click Deploy and copy the URL
 * 11. Paste the URL into booking.html where it says: const API_URL = '';
 */

const SHEET_NAME = 'Sheet1';

function formatDateStr(val) {
  if (val instanceof Date) {
    var y = val.getFullYear();
    var m = ('0' + (val.getMonth() + 1)).slice(-2);
    var d = ('0' + val.getDate()).slice(-2);
    return y + '-' + m + '-' + d;
  }
  return String(val);
}

function formatTimeStr(val) {
  if (val instanceof Date) {
    var h = ('0' + val.getHours()).slice(-2);
    var m = ('0' + val.getMinutes()).slice(-2);
    return h + ':' + m;
  }
  var s = String(val);
  // Handle "14:00:00" -> "14:00"
  if (s.length > 5) s = s.substring(0, 5);
  // Handle "2:00 PM" style
  return s;
}

function doGet(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  var data = sheet.getDataRange().getValues();

  var startDate = (e && e.parameter && e.parameter.start) || '';
  var endDate = (e && e.parameter && e.parameter.end) || '';

  var bookings = [];
  for (var i = 1; i < data.length; i++) {
    var row = data[i];
    if (!row[0]) continue;

    var dateStr = formatDateStr(row[0]);
    var timeStr = formatTimeStr(row[1]);

    // Filter by date range if provided
    if (startDate && dateStr < startDate) continue;
    if (endDate && dateStr > endDate) continue;

    bookings.push({
      date: dateStr,
      time: timeStr,
      duration: String(row[2]),
      name: String(row[3]),
      email: String(row[4]),
      phone: String(row[5]),
      notes: String(row[6])
    });
  }

  return ContentService
    .createTextOutput(JSON.stringify({ bookings: bookings }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);

    // Check for overlapping bookings
    var existing = sheet.getDataRange().getValues();
    var newStart = timeToMinutes(data.time);
    var newEnd = newStart + parseFloat(data.duration) * 60;

    for (var i = 1; i < existing.length; i++) {
      var rowDate = formatDateStr(existing[i][0]);
      if (rowDate !== data.date) continue;

      var rowTime = formatTimeStr(existing[i][1]);
      var rowDuration = parseFloat(existing[i][2]) || 2;
      var existStart = timeToMinutes(rowTime);
      var existEnd = existStart + rowDuration * 60;

      if (newStart < existEnd && newEnd > existStart) {
        return ContentService
          .createTextOutput(JSON.stringify({ success: false, error: 'This slot overlaps with an existing booking.' }))
          .setMimeType(ContentService.MimeType.JSON);
      }
    }

    // Add the booking
    var timestamp = new Date().toISOString();
    var rate = 20;
    var amount = parseFloat(data.duration) * rate;
    sheet.appendRow([
      data.date,
      data.time,
      data.duration,
      data.name,
      data.email,
      data.phone || '',
      data.notes || '',
      timestamp,
      amount
    ]);

    // Send confirmation email
    try {
      MailApp.sendEmail({
        to: data.email,
        subject: 'Booking Confirmed - Lefthand Drive Rehearsal Room',
        body: 'Hi ' + data.name + ',\n\n' +
              'Your rehearsal room booking has been confirmed:\n\n' +
              'Date: ' + data.date + '\n' +
              'Time: ' + data.time + '\n' +
              'Duration: ' + data.duration + ' hours\n\n' +
              'See you there!\n' +
              'Lefthand Drive'
      });
    } catch (mailErr) {
      console.log('Email send failed:', mailErr);
    }

    return ContentService
      .createTextOutput(JSON.stringify({ success: true }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ success: false, error: err.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function timeToMinutes(timeStr) {
  var parts = String(timeStr).split(':');
  return parseInt(parts[0]) * 60 + parseInt(parts[1] || 0);
}
