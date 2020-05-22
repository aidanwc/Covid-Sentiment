// Our labels along the x-axis
var dates = {{dates}};
var sentiment = {{scores}};


var ctx = document.getElementById("myChart");
var myChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: dates ,
    datasets: [
      { 
        data: sentiment,
        label: "Sentiment",
        borderColor: "#3e95cd",
        fill: false
      },
    ]
  },
  

});