function convertToCSVRows(inputCSV) {
  // Split the input CSV into lines
  const lines = inputCSV.trim().split('\n');

  // Extract header and data rows
  const header = lines[0].split(',');
  const dataRows = [];

  // Process each data row
  for (let i = 1; i < lines.length; i++) {
    const formattedRow = formatCSVRow(lines[i]);
    if (formattedRow) {
      dataRows.push(formattedRow);
    }
  }

  // Combine header and data rows
  return `日期,開盤價,最高價,最低價,收盤價\n${dataRows.join('\n')}`;
}

function parseCSVRow(row) {
    // Use a regular expression to match fields
    const regex = /,(?=(?:[^"]*"[^"]*")*[^"]*$)/g;
    return row
        .slice(1, -1)  // Remove the outer quotes
        .split(regex) // Split based on commas not within quotes
        .map(field => field.replace(/(^"|"$)/g, '')); // Remove any extra quotes around the fields
}

function parseNumberWithComma(formattedNumber) {
  // Remove commas from the formatted number
  var plainNumber = formattedNumber.replace(/,/g, '');
  // Convert the result to a number
  return Number(plainNumber);
}

function parseFloatNumber(num) {
  return parseFloat(num).toFixed(4);
}

function formatCSVRow(row) {
  // Split the row into columns
  // Remove quotation marks and split the row into columns
  const columns = parseCSVRow(row)

  if (columns.length < 7) return null; // Handle rows with insufficient columns

  // Convert the date from 'YY/MM/DD' to 'YYYY-MM-DD'
  const dateParts = columns[0].replace(/"/g, '').split('/');
  const year = dateParts[0];
  const month = dateParts[1].padStart(2, '0');
  const day = dateParts[2].padStart(2, '0');
  const formattedDate = `${year}-${month}-${day}`;

  // Extract and format the required columns
  const openPrice = parseFloatNumber(columns[3]);
  const highPrice = parseFloatNumber(columns[4]);
  const lowPrice = parseFloatNumber(columns[5]);
  const closePrice = parseFloatNumber(columns[6]);
  const volume = parseNumberWithComma(columns[1]);

  // Construct the formatted row fot chart drawing
  return `${formattedDate},${openPrice},${highPrice},${lowPrice},${closePrice},${volume}`;
}

// Example usage
// const inputCSV = `日期,成交股數,成交金額,開盤價,最高價,最低價,收盤價,漲跌價差,成交筆數
// "113/01/02","45,408","1,456,446","32.25","32.30","32.00","32.10","-0.20","41",
// "113/01/03","45,074","1,441,839","32.05","32.10","31.90","31.95","-0.15","41",`;

// const outputCSV = convertToCSVRows(inputCSV);
// console.log(outputCSV);


// function removeCSVHeader(inputCSV) {
//   // Split the input CSV into lines
//   const lines = inputCSV.trim().split('\n');

//   // remove the first line (header)
//   lines.shift();

//   // Join the remaining lines back into a single CSV string
//   return lines.join('\n');
// }