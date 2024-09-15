// Function to convert CSV text to 2D array
function csvToArray(csvText) {
  const rows = csvText.trim().split('\n'); // Split by rows
  return rows.map(row => row.split(',')); // Split each row by comma
}

document.addEventListener('DOMContentLoaded', function() {
  // Add event listener for the button
  document.getElementById('stockCodeButton').addEventListener('click', function() {
    console.log("click");

    const stockCode = document.getElementById('stockCodeInput').value;
    if (stockCode) {
      loadChart(stockCode);
    } else {
      alert('Please enter a valid stock code.');
    }
  });
});
