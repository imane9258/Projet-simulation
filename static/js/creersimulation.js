let rowIndex = 1;

function ajouterLigne() {
    const tableBody = document.getElementById('servicesTableBody');
    const row = `
        <tr id="row${rowIndex}">
            <td><input type="text" name="designation${rowIndex}" required></td>
            <td><input type="text" name="quantite${rowIndex}" pattern="[0-9]*" required ></td>
            <td><input type="text" name="prix_unitaire${rowIndex}" pattern="[0-9]*" required></td>
            <td><input type="text" name="frais_transit${rowIndex}" pattern="[0-9]*" required></td>
            <td><input type="text" name="frais_douane${rowIndex}" pattern="[0-9]*" required></td>
            <td><input type="text" name="marge_percentage${rowIndex}" pattern="[0-9]*" required></td>
            <td><input type="text" name="pourcentage_banque${rowIndex}" pattern="[0-9]*" required></td>
            <td><button type="button" class="delete-button" onclick="supprimerLigne(this)">Supprimer</button></td>
        </tr>
    `;
    tableBody.insertAdjacentHTML('beforeend', row);
    rowIndex++;
}

function supprimerLigne(button) {
    const row = button.parentElement.parentElement;
    row.remove();
}

function simuler() {
    const form = document.getElementById('simulationForm');
    let isValid = true;

    // Réinitialiser les erreurs
    resetErrors();

    // Vérifier les champs requis
    form.querySelectorAll('input[required]').forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            afficherErreur(input, 'Ce champ est requis.');
        }
    });

    // Vérifier les champs avec des valeurs numériques
    form.querySelectorAll('input[type="text"]').forEach(input => {
        const value = input.value.trim();
        if (input.pattern && value && !(/^\d+$/.test(value))) {
            isValid = false;
            afficherErreur(input, 'Veuillez saisir des chiffres.');
        }
    });

    if (isValid) {
        // Afficher l'animation de chargement
        const loadingAnimation = document.createElement('div');
        loadingAnimation.classList.add('loading-animation');
        loadingAnimation.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Simulation en cours...';
        document.body.appendChild(loadingAnimation);

        // Simuler l'envoi du formulaire (ici, c'est juste une démonstration)
        setTimeout(() => {
            // Supprimer l'animation après un délai (simulé ici avec setTimeout)
            document.body.removeChild(loadingAnimation);

            // Envoyer le formulaire
            form.submit();
        }, 2000); // Temps de démonstration de l'animation (2 secondes)
    } else {
        form.reportValidity();
    }
}

function afficherErreur(input, message) {
    const errorDiv = document.createElement('div');
    errorDiv.classList.add('error-message');
    errorDiv.textContent = message;
    input.parentNode.appendChild(errorDiv);
    input.classList.add('error');
}

function resetErrors() {
    const form = document.getElementById('simulationForm');
    form.querySelectorAll('.error-message').forEach(error => {
        error.remove();
    });
    form.querySelectorAll('input').forEach(input => {
        input.classList.remove('error');
    });
}




