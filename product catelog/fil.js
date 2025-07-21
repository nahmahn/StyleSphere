document.addEventListener('DOMContentLoaded', () => {
    const searchBar = document.getElementById('search-bar');
    const productGrid = document.getElementById('product-grid');
    const categoryFiltersContainer = document.getElementById('category-filters');
    const tagsFiltersContainer = document.getElementById('tags-filters');
    const productCountSpan = document.getElementById('product-count');

    let currentFilters = {};
    let currentSearchQuery = '';
    let debounceTimer;

    const fetchAndRenderProducts = async () => {
        productGrid.innerHTML = '<div class="loader"></div>';
        const requestBody = { text_query: currentSearchQuery, filters: currentFilters };
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody),
            });
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            const data = await response.json();
            renderProducts(data.products);
        } catch (error) {
            console.error("Failed to fetch products:", error);
            productGrid.innerHTML = `<p style="color: red;">Error: ${error.message}. Check the Flask server terminal.</p>`;
        }
    };

    const renderProducts = (products) => {
        productGrid.innerHTML = '';
        productCountSpan.textContent = products.length;
        if (!products || products.length === 0) {
            productGrid.innerHTML = "<p>No products found.</p>";
            return;
        }
        products.forEach(product => {
            const card = document.createElement('div');
            card.className = 'product-card';
            
            // This logic correctly creates the hover effect only if a person image is available
            const personImageHtml = product.person_image 
                ? `<img src="/images/person/${product.person_image}" alt="Model view" class="product-card-img person-view">` 
                : '';

            card.innerHTML = `
                <div class="product-card-img-container">
                    <img src="/images/cloth/${product.item_id}" alt="${product.category}" class="product-card-img cloth-view">
                    ${personImageHtml}
                </div>
                <div class="product-card-info">
                    <p class="product-card-category">${product.category}</p>
                    <p class="product-card-id">${product.item_id.split('_')[0]}</p>
                </div>
            `;
            productGrid.appendChild(card);
        });
    };
    
    const setupFilters = (filterData) => {
        categoryFiltersContainer.innerHTML = ''; tagsFiltersContainer.innerHTML = '';
        filterData.all_categories.forEach(cat => {
            const label = document.createElement('label');
            label.className = 'filter-label';
            label.innerHTML = `<input type="checkbox" class="filter-checkbox" value="${cat}" data-filter-key="category"> <span>${cat}</span>`;
            categoryFiltersContainer.appendChild(label);
        });
        filterData.popular_tags.forEach(tag => {
            const label = document.createElement('label');
            label.className = 'filter-label';
            label.innerHTML = `<input type="checkbox" class="filter-checkbox" value="${tag}" data-filter-key="tags"> <span>${tag}</span>`;
            tagsFiltersContainer.appendChild(label);
        });
        document.querySelectorAll('.filter-checkbox').forEach(checkbox => checkbox.addEventListener('change', handleFilterChange));
    };
    
    const handleFilterChange = (event) => {
        const checkbox = event.target;
        const key = checkbox.dataset.filterKey;
        const value = checkbox.value;
        if (!currentFilters[key]) currentFilters[key] = [];
        if (checkbox.checked) {
            currentFilters[key].push(value);
        } else {
            currentFilters[key] = currentFilters[key].filter(v => v !== value);
        }
        if (currentFilters[key].length === 0) delete currentFilters[key];
        fetchAndRenderProducts();
    };

    searchBar.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            currentSearchQuery = searchBar.value;
            fetchAndRenderProducts();
        }, 300);
    });

    const initializeApp = async () => {
        try {
            const filterResponse = await fetch('/api/filters');
            if (!filterResponse.ok) throw new Error(`HTTP error! Status: ${filterResponse.status}`);
            const filterData = await filterResponse.json();
            setupFilters(filterData);
            fetchAndRenderProducts();
        } catch (error) {
            console.error("Could not initialize filters:", error);
            categoryFiltersContainer.innerHTML = `<p style="color: red;">Could not load filters.</p>`;
        }
    };

    initializeApp();
});