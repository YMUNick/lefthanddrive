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

function doGet(e) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  const data = sheet.getDataRange().getValues();
  const headers = data[0];

  const startDate = e.parameter.start || '';
  const endDate = e.parameter.end || '';

  const bookings = [];
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const date = row[0];
    if (!date) continue;

    // Filter by date range if provided
    if (startDate && date < startDate) continue;
    if (endDate && date > endDate) continue;

    bookings.push({
      date: row[0],
      time: row[1],
      duration: row[2],
      name: row[3],
      email: row[4],
      phone: row[5],
      notes: row[6]
    });
  }

  return ContentService
    .createTextOutput(JSON.stringify({ bookings: bookings }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);

    // Check for double booking
    const existing = sheet.getDataRange().getValues();
    for (let i = 1; i < existing.length; i++) {
      if (existing[i][0] === data.date && existing[i][1] === data.time) {
        return ContentService
          .createTextOutput(JSON.stringify({ success: false, error: 'This slot is already booked.' }))
          .setMimeType(ContentService.MimeType.JSON);
      }
    }

    // Add the booking
    const timestamp = new Date().toISOString();
    const rate = 20;
    const amount = parseInt(data.duration) * rate;
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
      // Email sending is optional, don't fail the booking
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
