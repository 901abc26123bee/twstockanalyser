// reference: https://api.anychart.com/anychart.core.stock.Plot#category-specific-settings

// const fileData = './csv/teslaDailyData.csv'
const fileData = './csv/STOCK_DAY_4540_202409.csv'
const risingColor = '#DA5E5E'
const fallingColor = '#559966'
const yellowColor = '#C9CC3F'
const orangeColor = '#FFA500'

const stockName = '4540'

anychart.onDocumentReady(function () {
  anychart.data.loadCsvFile(
    fileData,
    function (rawCsvData) {
      var csvData = convertToCSVRows(rawCsvData)

      // Create data table on loaded data
      var dataTable = anychart.data.table();
      dataTable.addData(csvData);

      // Map loaded data for the candlestick series
      var mapping = dataTable.mapAs({
        open: 1,
        high: 2,
        low: 3,
        close: 4
      });
      var volumeMapping = dataTable.mapAs({ volume: 5 });


      // Create stock chart
      var chart = anychart.stock();
      // Create first plot on the chart
      var plot = chart.plot(0);
      // Set grid settings
      plot.yGrid(true).xGrid(true).yMinorGrid(true).xMinorGrid(true);

      // Customize the rising and falling colors
      customizeCandlestickSeries(chart, plot, mapping);
      generateMACD(chart, mapping);
      generateKD(chart, mapping);
      defaultSelectPart(chart, csvData);
      generateVolume(chart, volumeMapping)

      // Set the title of the chart
      chart.title(stockName);
      // Set container id for the chart
      chart.container('container');
      // Initiate chart drawing
      chart.draw();
    }
  );
});


function customizeCandlestickSeries(chart, plot, mapping) {
  // Create and configure candlestick series
  var series = plot.candlestick(mapping).name(stockName);
  // Customize the rising and falling colors
  series.risingFill(risingColor);   // Color for rising candles
  series.fallingFill(fallingColor);    // Color for falling candles
  // Set the stroke (outline) color for rising and falling candles
  series.risingStroke(risingColor);   // Outline color for rising candles
  series.fallingStroke(fallingColor); // Outline color for falling candles

  // Create scroller series with mapped data
  chart.scroller().candlestick(mapping);
}

function defaultSelectPart(chart, csvData) {
  // Convert the CSV data to an array
  const dataArray = csvToArray(csvData);

  // Find the latest date in the data
  var latestDate = dataArray[dataArray.length - 1][0]; // Assuming the dates are sorted
  var startDate = dataArray[dataArray.length - 60][0];
  // Set chart selected date/time range
  chart.selectRange(startDate, latestDate);

  // Create and initialize range picker
  var rangePicker = anychart.ui.rangePicker();
  rangePicker.render(chart);

  // Create and initialize range selector
  var rangeSelector = anychart.ui.rangeSelector();
  rangeSelector.render(chart);
}

// https://playground.anychart.com/api/core/stock/_samples/anychart.core.stock.Plot.macd
function generateMACD(chart, mapping) {
  // second plot to show macd values
  var indicatorPlot = chart.plot(1);

  // Creates MACD indicator.
  var macdIndicator = indicatorPlot.macd(mapping, 12, 26, 9, 'line', 'line', 'column');
  var signal = macdIndicator.signalSeries();
  signal.stroke(yellowColor);
  var histogram = macdIndicator.macdSeries();
  histogram.stroke(orangeColor);

  // map the values
  macdIndicator.histogramSeries('column');
  macdIndicator
    .histogramSeries()
    .normal()
    .fill(risingColor)
    .stroke(risingColor);
  macdIndicator
    .histogramSeries()
    .normal()
    .negativeFill(fallingColor)
    .negativeStroke(fallingColor);

  // set second plot's height
  indicatorPlot.height('15%');
}

function generateKD(chart, mapping) {
  // Create a new plot for the KD indicator
  var rsvIndicator = chart.plot(2); // Use index 1 or another available index for the new plot

  // Create the KD indicator series
  var kd = rsvIndicator.stochastic(mapping, 20, 9, 9, 'ema', 'ema', 'line', 'line');
  var k = kd.kSeries()
  k.stroke(risingColor)
  var d = kd.dSeries()
  d.stroke(fallingColor)

  rsvIndicator.height('15%');
}

function generateVolume(chart,volumeMapping) {
  // create and setup volume plot
  var volumePlot = chart.plot(3);
  volumePlot.height('15%');
  volumePlot
    .yAxis()
    .labels()
    .format('{%Value}{scale:(1000000)(1000)|(kk)(k)}');

  // create and setup volume+MA indicator
  var volumeMaIndicator = volumePlot.volumeMa(
    volumeMapping,
    5,
    'sma',
    'column',
    'splineArea'
  );
  var maSeries = volumeMaIndicator.maSeries();
  maSeries.stroke('red');
  maSeries.fill('red .2');
  volumeMaIndicator.volumeSeries('column');
}

// // https://www.anychart.com/products/anystock/gallery/Stock_Drawing_Annotations/Annotated_Candlestick_Chart_and_EMA.php
// function generateAllEMA(chart, mapping) {
//   // Add EMAs with periods 5, 10, 20, 40, 60

// }

// function addEMA(chart, dataTable, period) {
//   var emaPlot = chart.plot(3);
//   var ema = emaPlot.ema(
//     dataTable.mapAs({
//       value: 4
//     })
//   );
//   ema.series().stroke('1.5 #455a64');
// }