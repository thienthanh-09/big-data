$(function () {
    handleChangeMode();
    handleTimeFilter();
    drawChart();
    handleCSV();
    handlePDF();
});

function handlePDF(){
    window.jsPDF = window.jspdf.jsPDF;
    $('#download-pdf-btn').click(function (){
        const pdf = new jsPDF('p', 'pt', 'a4');
        let width = pdf.internal.pageSize.getWidth() * 2 / 3;
        let chart1 = $('#chart-most-sell')[0],
            chart2 = $('#chart-sold-count')[0];
        pdf.addImage(chart1, 'PNG', width/4 , 0, width, width * chart1.height / chart1.width);
        pdf.addPage();
        pdf.addImage(chart2, 'PNG', width/4 , 0, width, width * chart2.height / chart2.width);
        pdf.save('statistic.pdf');
    });
}

function handleCSV(){
    let csvContent = "data:text/csv;charset=utf-8,";
    let mostSoldProducts = [',Product Name,Quantity'];
    $('.product-name').each(function(index, item){
        let productName = $(item).text();
        let productQuantity = $('.product-quantity').eq(index).text();
        mostSoldProducts.push(index + ',' + productName + ',' + productQuantity);
    });
    
    let highestRatingProducts = [',Product Name,Rating'];
    $('.rate-product-name').each(function(index, item){
        let productName = $(item).text();
        let productRating = $('.product-rate').eq(index).text().replace(',', '.');
        highestRatingProducts.push(index + ',' + productName + ',' + productRating);
    });

    $('#download-sell-btn').click(function (){
        let uri = csvContent + mostSoldProducts.join('\n');
        let link = document.createElement("a");
        link.href = uri;
        link.download = "most-sold-products.csv";
        link.click();
    });

    $('#download-rate-btn').click(function (){
        let uri = csvContent + highestRatingProducts.join('\n');
        let link = document.createElement("a");
        link.href = uri;
        link.download = "highest-rated-products.csv";
        link.click();
    });
}

function drawChart(){
    drawMostSellChart();
    drawSoldCountChart();
}

function drawSoldCountChart(){
    const ctx = document.getElementById('chart-sold-count').getContext('2d');
    const myChart = new Chart(ctx, window.chart2Config);
}

function drawMostSellChart(){
    let labels = [];
    const randomColor = function() {
        r = Math.floor(Math.random() * 255);
        g = Math.floor(Math.random() * 255);
        b = Math.floor(Math.random() * 255);
        return "rgb(" + r + "," + g + "," + b + ")";
    };

    let colors = [];
    $('.product-name').each(function(index, item){
        let name = $(item).text();
        if (name.length > 50) {
            name = name.substring(0, 50) + '...';
        }
        labels.push(name);
        colors.push(randomColor());
    });
    let data = [];
    $('.product-quantity').each(function(index, item){
        data.push($(item).text());
    });
    const ctx = document.getElementById('chart-most-sell').getContext('2d');
    
    const myChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: '# of Votes',
                data: data,
                backgroundColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                }
            }
        },
    });
}

function handleChangeMode(){
    $('#mode-chart-btn').click(function (){
        $('#mode-table-content').prop('hidden', true);
        $('#mode-chart-content').prop('hidden', false);
    });
    $('#mode-table-btn').click(function (){
        $('#mode-table-content').prop('hidden', false);
        $('#mode-chart-content').prop('hidden', true);
    });
}

function handleTimeFilter(){
    $('.by-btn').click(function (){
        let time = $(this).attr('data-time');
        window.location.href = '/me/store/statistic/?time=' + time;
    });
}