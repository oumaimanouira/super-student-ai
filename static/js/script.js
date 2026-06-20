document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector(".card-form");
    const submitBtn = document.getElementById("submit-btn");

    if (form && submitBtn) {
        form.addEventListener("submit", () => {
            const nomProjet = form.querySelector("#nom_projet");
            const description = form.querySelector("#description");

            if (!nomProjet.value.trim() || !description.value.trim()) {
                return;
            }

            const btnText = submitBtn.querySelector(".btn-text");
            const btnSpinner = submitBtn.querySelector(".btn-spinner");

            if (btnText && btnSpinner) {
                btnText.textContent = "Analyse en cours...";
                btnSpinner.hidden = false;
            }

            submitBtn.disabled = true;
        });
    }

    const flashes = document.querySelectorAll(".flash");

    flashes.forEach((flash) => {
        setTimeout(() => {
            flash.style.transition = "opacity 0.5s ease";
            flash.style.opacity = "0";

            setTimeout(() => flash.remove(), 500);
        }, 6000);
    });
});