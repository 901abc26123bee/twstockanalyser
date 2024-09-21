const risingColor = '#DA5E5E'
const fallingColor = '#559966'
const yellowColor = '#C9CC3F'
const orangeColor = '#FFA500'
const backGroundColor = '#343434'
// const backGroundColor = '#ffffff'

function loadChart(fileData, stockName, container) {
  anychart.onDocumentReady(function () {
    anychart.data.loadCsvFile(
      fileData,
      function (rawCsvData) {
        csvData = rawCsvData
        console.log(csvData.length)
  
        // create data table on loaded data
        var dataTable = anychart.data.table();
        dataTable.addData(csvData);
  
        // Map loaded data for the candlestick series
        var mapping = dataTable.mapAs({
          open: 1,
          high: 2,
          low: 3,
          close: 4,
        });
        var closeMapping = dataTable.mapAs({ value: 4 });
        var volumeMapping = dataTable.mapAs({ volume: 5 });
  
        // Create stock chart
        var chart = anychart.stock();
        globalChart = chart;

        // Create first plot on the chart
        var plot = chart.plot(0);
        // Set grid settings
        plot.yGrid(true).xGrid(true);
  
        // Customize the rising and falling colors
        plotCandlestickSeries(chart, plot, mapping, stockName);
        plotMASeries(plot, closeMapping)
        plotBBands(plot, mapping)
        defaultSelectRange(chart, csvData);
        plotMACD(chart, mapping);
        plotKD(chart, mapping);
        plotVolume(chart, volumeMapping)
  
        // Set the title of the chart
        chart.title(stockName);
        // Set container id for the chart
        chart.container(container);
        // Customize the background color
        chart.background().fill(backGroundColor);
        // Initiate chart drawing
        chart.draw();
      }
    );
  });  
}


function plotCandlestickSeries(chart, plot, mapping, stockName) {
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

function plotBBands(plot, mapping) {
  // create Bollinger Bands indicator with splines
  var bbands = plot.bbands(mapping, 16, 2, "spline", "spline", "spline");

  // color the series
  bbands.upperSeries().stroke('#ffd54f');
  bbands.middleSeries().stroke('#FFA500');
  bbands.lowerSeries().stroke('#ffd54f');
  bbands.rangeSeries().fill('#ffd54f 0.05');
}

function plotMASeries(plot, closeMapping) {
  var sma5 = plot.sma(closeMapping, 5).series();
  sma5.name('SMA(5)').stroke('#0288d1'); // Deep Orange
  var sma10 = plot.sma(closeMapping, 10).series();
  sma10.name('SMA(10)').stroke('#8e24aa'); // Orange
  var sma40 = plot.sma(closeMapping, 40).series();
  sma40.name('SMA(40)').stroke('#388e3c'); // Green
  var sma60 = plot.sma(closeMapping, 60).series();
  sma60.name('SMA(60)').stroke('#bf360c'); // Blue
  var sma138 = plot.sma(closeMapping, 138).series();
  sma138.name('SMA(138)').stroke('#ff6d80'); // Purple
}

function defaultSelectRange(chart, csvData) {
  // Convert the CSV data to an array
  let dataArray = csvToArray(csvData);

  // Find the latest date in the data
  var latestDate = dataArray[dataArray.length - 1][0]; // Assuming the dates are sorted
  // set to 60 to avoid TypeError: Cannot read properties of undefined (reading '0')
  var startDate
  if (dataArray.length <= 60) {
    var startDate = dataArray[1][0];
  }
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
function plotMACD(chart, mapping) {
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

function plotKD(chart, mapping) {
  // Create a new plot for the KD indicator
  var rsvIndicator = chart.plot(2); // Use index 1 or another available index for the new plot

  // Create the KD indicator series
  var kd = rsvIndicator.stochastic(mapping, 20, 9, 9, 'ema', 'ema', 'line', 'line');
  var k = kd.kSeries()
  k.stroke(risingColor)
  var d = kd.dSeries()
  d.stroke(fallingColor)

  rsvIndicator.yGrid(true).xGrid(true);
  rsvIndicator.height('15%');
}

function plotVolume(chart, volumeMapping) {
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
