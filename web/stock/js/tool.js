// Function to convert CSV text to 2D array
function csvToArray(csvText) {
  const rows = csvText.trim().split('\n'); // Split by rows
  return rows.map(row => row.split(',')); // Split each row by comma
}
