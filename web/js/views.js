
let globalDayChart = null
let globalMonthChart = null
let globalWeekChart = null
let global60mChart = null
let global30mChart = null
let global15mChart = null

function loadChartWithDayData(stockCode) {
  if (globalDayChart) {
    globalChart.dispose(); // Dispose of the previous chart instance if it exists
  }

  let fileData = `./stock_data/${stockCode}/${stockCode}_day.csv`;
  let stockName = stockCode + " .TW" + "(DAY)"
  loadChart(fileData, stockName, "container_day")

  globalDayChart = stockName
}

function loadChartWithWeekData(stockCode) {
  if (globalWeekChart) {
    globalWeekChart.dispose(); // Dispose of the previous chart instance if it exists
  }

  let fileData = `./stock_data/${stockCode}/${stockCode}_week.csv`;
  let stockName = stockCode + " .TW" + "(WEEK)"
  loadChart(fileData, stockName, "container_week")

  globalWeekChart = stockName
}

function loadChartWithMonthData(stockCode) {
  if (globalMonthChart) {
    globalMonthChart.dispose(); // Dispose of the previous chart instance if it exists
  }

  let fileData = `./stock_data/${stockCode}/${stockCode}_month.csv`;
  let stockName = stockCode + " .TW" + "(MONTH)"
  loadChart(fileData, stockName, "container_month")

  globalMonthChart = stockName
}

function loadChartWith60MinuteData(stockCode) {
  if (global60mChart) {
    global60mChart.dispose(); // Dispose of the previous chart instance if it exists
  }

  let fileData = `./stock_data/${stockCode}/${stockCode}_60m.csv`;
  let stockName = stockCode + " .TW" + "(60m)"
  loadChart(fileData, stockName, "container_60m")

  global60mChart = stockName
}

function loadChartWith30MinuteData(stockCode) {
  if (global30mChart) {
    global30mChart.dispose(); // Dispose of the previous chart instance if it exists
  }

  let fileData = `./stock_data/${stockCode}/${stockCode}_30m.csv`;
  let stockName = stockCode + " .TW" + "(30m)"
  loadChart(fileData, stockName, "container_30m")

  global30mChart = stockName
}

function loadChartWith15MinuteData(stockCode) {
  if (global15mChart) {
    global15mChart.dispose(); // Dispose of the previous chart instance if it exists
  }

  let fileData = `./stock_data/${stockCode}/${stockCode}_15m.csv`;
  let stockName = stockCode + " .TW" + "(15m)"
  loadChart(fileData, stockName, "container_15m")

  global15mChart = stockName
}
