// Dashboard chart initialization
function initContractStatusChart(pendingCount, financeCount, billedCount) {
  // Get the chart canvas
  const chartCanvas = document.getElementById('contractStatusChart');
  
  // Only create chart if canvas exists
  if (chartCanvas) {
    // Create the chart
    new Chart(chartCanvas, {
      type: 'pie',
      data: {
        labels: ['Pending', 'Finance', 'Billed'],
        datasets: [{
          data: [pendingCount, financeCount, billedCount],
          backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc'],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    });
  }
} 