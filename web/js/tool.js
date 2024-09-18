// Function to convert CSV text to 2D array
function csvToArray(csvText) {
  let rows = csvText.trim().split('\n'); // Split by rows
  return rows.map(row => row.split(',')); // Split each row by comma
}

document.addEventListener('DOMContentLoaded', function() {
  // Add event listener for the button
  document.getElementById('stockCodeButton').addEventListener('click', function() {
    console.log("click");

    const stockCode = document.getElementById('stockCodeInput').value;
    if (stockCode) {
      loadChartWithMonthData(stockCode);
      loadChartWithWeekData(stockCode);
      loadChartWithDayData(stockCode);
      loadChartWith60MinuteData(stockCode);
      loadChartWith30MinuteData(stockCode);
      loadChartWith15MinuteData(stockCode);
    } else {
      alert('Please enter a valid stock code.');
    }
  });
});
