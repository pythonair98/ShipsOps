/**
 * Dashboard Charts Initialization
 */

// Initialize Contract Status Chart
function initContractStatusChart(pending, finance, billed) {
  console.log("Initializing Contract Status Chart with data:", {pending, finance, billed});
  
  // Make sure we have the canvas element
  var ctx = document.getElementById('contractStatusChart');
  if (!ctx) {
    console.error("Contract Status Chart canvas not found");
    return;
  }
  
  // Check if we have valid data
  if (pending === undefined || finance === undefined || billed === undefined) {
    console.error("Contract Status Chart missing data");
    pending = pending || 0;
    finance = finance || 0;
    billed = billed || 0;
  }
  
  // Create the pie chart
  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['Pending', 'Finance', 'Billed'],
      datasets: [{
        data: [pending, finance, billed],
        backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc'],
        hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf'],
        hoverBorderColor: "rgba(234, 236, 244, 1)",
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      tooltips: {
        backgroundColor: "rgb(255,255,255)",
        bodyFontColor: "#858796",
        borderColor: '#dddfeb',
        borderWidth: 1,
        xPadding: 15,
        yPadding: 15,
        displayColors: false,
        caretPadding: 10,
      },
      legend: {
        display: true,
        position: 'bottom'
      },
      cutoutPercentage: 0,
    }
  });
  console.log("Contract Status Chart initialized successfully");
}

// Initialize Revenue Trends Chart
function initRevenueChart(months, revenues, contracts) {
  console.log("Initializing Revenue Chart with data:", {months, revenues, contracts});
  
  // Make sure we have the canvas element
  var ctx = document.getElementById('revenueChart');
  if (!ctx) {
    console.error("Revenue Chart canvas not found");
    return;
  }
  
  // Check if we have valid data
  if (!months || !months.length || !revenues || !contracts) {
    console.error("Revenue Chart missing data");
    return;
  }
  
  // Create the line chart
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: months,
      datasets: [
        {
          label: "Revenue (USD)",
          lineTension: 0.3,
          backgroundColor: "rgba(78, 115, 223, 0.05)",
          borderColor: "rgba(78, 115, 223, 1)",
          pointRadius: 3,
          pointBackgroundColor: "rgba(78, 115, 223, 1)",
          pointBorderColor: "rgba(78, 115, 223, 1)",
          pointHoverRadius: 3,
          pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
          pointHoverBorderColor: "rgba(78, 115, 223, 1)",
          pointHitRadius: 10,
          pointBorderWidth: 2,
          data: revenues,
          yAxisID: 'y-axis-1',
        },
        {
          label: "Contracts",
          lineTension: 0.3,
          backgroundColor: "rgba(28, 200, 138, 0.05)",
          borderColor: "rgba(28, 200, 138, 1)",
          pointRadius: 3,
          pointBackgroundColor: "rgba(28, 200, 138, 1)",
          pointBorderColor: "rgba(28, 200, 138, 1)",
          pointHoverRadius: 3,
          pointHoverBackgroundColor: "rgba(28, 200, 138, 1)",
          pointHoverBorderColor: "rgba(28, 200, 138, 1)",
          pointHitRadius: 10,
          pointBorderWidth: 2,
          data: contracts,
          yAxisID: 'y-axis-2',
        }
      ],
    },
    options: {
      maintainAspectRatio: false,
      layout: {
        padding: {
          left: 10,
          right: 25,
          top: 25,
          bottom: 0
        }
      },
      scales: {
        xAxes: [{
          time: {
            unit: 'month'
          },
          gridLines: {
            display: false,
            drawBorder: false
          },
          ticks: {
            maxTicksLimit: 6
          }
        }],
        yAxes: [
          {
            id: 'y-axis-1',
            position: 'left',
            ticks: {
              maxTicksLimit: 5,
              padding: 10,
              callback: function(value, index, values) {
                return '$' + value;
              }
            },
            gridLines: {
              color: "rgb(234, 236, 244)",
              zeroLineColor: "rgb(234, 236, 244)",
              drawBorder: false,
              borderDash: [2],
              zeroLineBorderDash: [2]
            }
          },
          {
            id: 'y-axis-2',
            position: 'right',
            ticks: {
              maxTicksLimit: 5,
              padding: 10
            },
            gridLines: {
              drawBorder: false,
              display: false
            }
          }
        ]
      },
      legend: {
        display: true,
        position: 'top'
      },
      tooltips: {
        backgroundColor: "rgb(255,255,255)",
        bodyFontColor: "#858796",
        titleMarginBottom: 10,
        titleFontColor: '#6e707e',
        titleFontSize: 14,
        borderColor: '#dddfeb',
        borderWidth: 1,
        xPadding: 15,
        yPadding: 15,
        displayColors: false,
        intersect: false,
        mode: 'index',
        caretPadding: 10
      }
    }
  });
  console.log("Revenue Chart initialized successfully");
} 