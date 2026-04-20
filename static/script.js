document.addEventListener('DOMContentLoaded', () => {
    
    // --- FIXED: Changed from() to fromTo() to explicitly force visibility ---
    if (document.querySelector('.hero-content')) {
        gsap.fromTo(".hero-content h1", 
            { y: 60, opacity: 0 }, 
            { duration: 1.2, y: 0, opacity: 1, ease: "expo.out", delay: 0.1 }
        );
        gsap.fromTo(".hero-content p", 
            { y: 40, opacity: 0 }, 
            { duration: 1.2, y: 0, opacity: 1, ease: "expo.out", delay: 0.3 }
        );
        gsap.fromTo(".hero-content .neon-btn", 
            { y: 30, opacity: 0 }, 
            { duration: 1, y: 0, opacity: 1, stagger: 0.15, ease: "back.out(1.5)", delay: 0.5 }
        );
        gsap.fromTo(".glass-nav", 
            { y: -20, opacity: 0 }, 
            { duration: 1, y: 0, opacity: 1, ease: "power2.out" }
        );
    }

    const modal = document.getElementById('authModal');
    const openModalBtn = document.getElementById('openModalBtn');
    const closeSpan = document.getElementsByClassName('close')[0];

    function openModal() {
        modal.style.display = 'flex';
        gsap.fromTo(modal, {opacity: 0}, {opacity: 1, duration: 0.3, ease: "power2.out"});
        gsap.fromTo(".modal-content",
            { y: 60, scale: 0.9, opacity: 0, rotationX: -15, transformPerspective: 1000 },
            { y: 0, scale: 1, opacity: 1, rotationX: 0, duration: 0.7, ease: "expo.out" }
        );
        
        const activeForm = document.querySelector('.auth-form.active');
        if(activeForm) {
            gsap.fromTo(activeForm.querySelectorAll("input, button, p, h3"),
                { y: 20, opacity: 0 },
                { y: 0, opacity: 1, duration: 0.5, stagger: 0.05, ease: "back.out(1.2)", delay: 0.2 }
            );
        }
    }

    function closeModal() {
        gsap.to(".modal-content", { 
            y: 30, scale: 0.95, opacity: 0, duration: 0.3, ease: "power2.in" 
        });
        gsap.to(modal, { 
            opacity: 0, duration: 0.3, delay: 0.1, 
            onComplete: () => modal.style.display = 'none' 
        });
    }

    if (openModalBtn) {
        openModalBtn.onclick = function(e) {
            e.preventDefault();
            openModal();
        }
    }

    if (closeSpan) {
        closeSpan.onclick = closeModal;
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            closeModal();
        }
    }

    let currentSelection = null;
    let basePrice = 0;
    let activeType = '';

    const items = document.querySelectorAll('.selectable-item');
    const panelDisplay = document.getElementById('cost-breakdown');
    const inputItemId = document.getElementById('form_item_id');
    const inputItemType = document.getElementById('form_item_type');
    const inputTotalPrice = document.getElementById('form_total_price');
    const btnProceed = document.getElementById('proceed-btn');
    const inputNights = document.getElementById('nights-input');

    function refreshBillingEngine() {
        if (!currentSelection) {
            panelDisplay.innerHTML = '<p>Select an item to view real-time pricing.</p>';
            if (btnProceed) btnProceed.disabled = true;
            return;
        }

        let calculatedTotal = basePrice;
        let breakdownHTML = `<p>Base Fare: $${basePrice.toFixed(2)}</p>`;

        if (activeType === 'hotel' && inputNights) {
            const duration = parseInt(inputNights.value) || 1;
            calculatedTotal = basePrice * duration;
            breakdownHTML = `<p>$${basePrice.toFixed(2)} x ${duration} night(s)</p>`;
        }

        const platformFee = calculatedTotal * 0.12;
        const finalGrandTotal = calculatedTotal + platformFee;

        panelDisplay.innerHTML = `
            ${breakdownHTML}
            <p>Taxes & Platform Fees (12%): $${platformFee.toFixed(2)}</p>
            <div style="height: 1px; background: rgba(0,255,204,0.3); margin: 15px 0;"></div>
            <h3>Estimated Total: $<span class="glow-text">${finalGrandTotal.toFixed(2)}</span></h3>
        `;

        if (inputItemId) inputItemId.value = currentSelection.dataset.id;
        if (inputItemType) inputItemType.value = activeType;
        if (inputTotalPrice) inputTotalPrice.value = finalGrandTotal.toFixed(2);
        if (btnProceed) btnProceed.disabled = false;
    }

    items.forEach(el => {
        el.addEventListener('click', function() {
            items.forEach(i => i.classList.remove('selected'));
            this.classList.add('selected');
            currentSelection = this;
            basePrice = parseFloat(this.dataset.price);
            activeType = this.dataset.type;
            refreshBillingEngine();
        });
    });

    if (inputNights) {
        inputNights.addEventListener('input', refreshBillingEngine);
    }

    const dropdownSort = document.getElementById('sort-select');
    const containerHotelGrid = document.getElementById('hotel-grid');

    if (dropdownSort && containerHotelGrid) {
        dropdownSort.addEventListener('change', function() {
            const order = this.value;
            if (order === 'none') return;
            
            const hotelElements = Array.from(containerHotelGrid.getElementsByClassName('hotel-item'));

            hotelElements.sort((a, b) => {
                const valA = parseFloat(a.dataset.price);
                const valB = parseFloat(b.dataset.price);
                if (order === 'asc') return valA - valB;
                return valB - valA;
            });

            containerHotelGrid.innerHTML = '';
            hotelElements.forEach(element => containerHotelGrid.appendChild(element));
        });
    }

    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(msg => {
        msg.style.cursor = 'pointer';
        
        msg.addEventListener('click', () => {
            msg.classList.add('fade-out');
            setTimeout(() => msg.remove(), 500);
        });

        if (!msg.innerText.includes('CRITICAL')) {
            setTimeout(() => {
                if(document.body.contains(msg)) {
                    msg.classList.add('fade-out');
                    setTimeout(() => msg.remove(), 500);
                }
            }, 4000);
        }
    });

    const urlParams = new URLSearchParams(window.location.search);
    const modalToOpen = urlParams.get('modal');

    if (modalToOpen && modal) {
        openModal();
        if (window.switchTab) {
            window.switchTab(modalToOpen);
        }
        window.history.replaceState({}, document.title, window.location.pathname);
    }
});

window.switchTab = function(tabName) {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const forms = document.querySelectorAll('.auth-form');
    const resetTab = document.getElementById('resetTab');

    let newForm = null;

    tabBtns.forEach(btn => btn.classList.remove('active'));
    forms.forEach(form => {
        if(form.classList.contains('active')) {
            gsap.to(form, { opacity: 0, x: -20, duration: 0.2, onComplete: () => form.classList.remove('active') });
        }
    });

    if (resetTab) resetTab.style.display = 'none';

    if (tabName === 'login') {
        tabBtns[0].classList.add('active');
        newForm = document.getElementById('loginForm');
    } else if (tabName === 'signup') {
        tabBtns[1].classList.add('active');
        newForm = document.getElementById('signupForm');
    } else if (tabName === 'reset') {
        if (resetTab) {
            resetTab.style.display = 'block';
            resetTab.classList.add('active');
        }
        newForm = document.getElementById('resetForm');
    }

    if(newForm) {
        setTimeout(() => {
            newForm.classList.add('active');
            gsap.fromTo(newForm.querySelectorAll("input, button, p, h3"),
                { x: 20, opacity: 0 },
                { x: 0, opacity: 1, duration: 0.4, stagger: 0.05, ease: "power2.out" }
            );
        }, 200);
    }
};