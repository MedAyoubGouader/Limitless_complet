// Fonctions de gestion du formulaire de paiement
document.addEventListener('DOMContentLoaded', function() {
    // Formatage des champs de carte bancaire
    initCardFormatting();
    
    // Gestion de la soumission AJAX des formulaires de paiement
    initPaymentForms();
});

// Formatage des champs de carte
function initCardFormatting() {
    // Formatage du numéro de carte
    document.querySelectorAll('.card-number-input').forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 16) value = value.slice(0, 16);
            
            // Formatage par groupes de 4 chiffres
            let formattedValue = '';
            for (let i = 0; i < value.length; i++) {
                if (i > 0 && i % 4 === 0) {
                    formattedValue += ' ';
                }
                formattedValue += value[i];
            }
            e.target.value = formattedValue;
        });
    });
    
    // Formatage de la date d'expiration
    document.querySelectorAll('.card-expiry-input').forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 4) value = value.slice(0, 4);
            
            if (value.length > 2) {
                e.target.value = value.slice(0, 2) + '/' + value.slice(2);
            } else {
                e.target.value = value;
            }
        });
    });
    
    // Formatage du CVC
    document.querySelectorAll('.card-cvc-input').forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 3) value = value.slice(0, 3);
            e.target.value = value;
        });
    });
}

// Gestion de la soumission AJAX des formulaires de paiement
function initPaymentForms() {
    document.querySelectorAll('form[action*="payer"]').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Afficher le spinner de chargement
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Traitement en cours...';
            
            // Créer l'objet FormData
            const formData = new FormData(form);
            
            // Envoyer la requête AJAX
            fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Redirection en cas de succès
                    window.location.href = data.redirect || '/success/';
                } else {
                    // Afficher l'erreur
                    showError(form, data.message || 'Une erreur est survenue. Veuillez vérifier vos informations.');
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnText;
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                showError(form, 'Une erreur est survenue lors du traitement du paiement.');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            });
        });
    });
}

// Affichage des erreurs de paiement
function showError(form, message) {
    // Créer ou récupérer le conteneur d'erreur
    let errorContainer = form.querySelector('.payment-error');
    if (!errorContainer) {
        errorContainer = document.createElement('div');
        errorContainer.className = 'alert alert-danger payment-error mt-3';
        form.querySelector('.mt-4').insertAdjacentElement('beforebegin', errorContainer);
    }
    
    errorContainer.textContent = message;
    errorContainer.style.display = 'block';
    
    // Scroll vers l'erreur
    errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
}