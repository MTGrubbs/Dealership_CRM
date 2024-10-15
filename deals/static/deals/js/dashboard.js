
document.addEventListener('DOMContentLoaded', function() {
    const dailyCard = document.getElementById('daily-card');
    const monthlyCard = document.getElementById('monthly-card');
    const modal = document.getElementById('dealsModal');
    const closeBtn = document.querySelector('.close');
    
    // Get URLs from data attributes
    const urlsElement = document.getElementById('js-urls');
    const dailyDealsUrl = urlsElement.dataset.dailyDealsUrl;
    const monthlyDealsUrl = urlsElement.dataset.monthlyDealsUrl;

    console.log('URLs:', { dailyDealsUrl, monthlyDealsUrl });  // Debug log

    dailyCard.addEventListener('click', function() {
        showDeals('daily');
    });

    monthlyCard.addEventListener('click', function() {
        showDeals('monthly');
    });

    closeBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    window.addEventListener('click', function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    });

    function showDeals(period) {
        console.log('showDeals called with period:', period);  // Debug log
        let url = period === 'daily' ? dailyDealsUrl : monthlyDealsUrl;
        console.log('Using URL:', url);  // Debug log

        if (!url) {
            console.error('URL is undefined for period:', period);
            return;
        }

        let date = new Date();
        let dateParam = period === 'daily' 
            ? date.toISOString().split('T')[0]
            : date.toISOString().slice(0, 7);

        fetch(`${url}?date=${dateParam}`)
            .then(response => response.json())
            .then(deals => {
                console.log('Fetched deals:', deals);  // Debug log
                let tableBody = document.querySelector("#dealsTable tbody");
                tableBody.innerHTML = "";
                deals.forEach(deal => {
                    let row = tableBody.insertRow();
                    row.insertCell(0).textContent = deal.customer_name;
                    let gross = typeof deal.gross === 'string' ? parseFloat(deal.gross) : deal.gross;
                    row.insertCell(1).textContent = `$${gross.toFixed(2)}`;
                    row.insertCell(2).textContent = deal.car_type;
                    row.insertCell(3).textContent = deal.date || dateParam;
                    row.insertCell(4).textContent = deal.salesperson;
                });
                document.getElementById("modalTitle").textContent = 
                    period === 'daily' ? "Daily Deals" : "Monthly Deals";
                modal.style.display = "block";
            })
            .catch(error => console.error('Error:', error));
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const dateFilter = document.getElementById('date-filter');
    const form = document.getElementById('date-filter-form');

    dateFilter.addEventListener('change', function() {
        form.submit();
    });
});