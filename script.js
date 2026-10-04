// ========================================
// Friendship Website - Main JavaScript
// ========================================

document.addEventListener("DOMContentLoaded", function () {

    // ----------------------------------------
    // Auto-hide flash messages
    // ----------------------------------------
    const flashMessages = document.querySelectorAll(".flash-message");

    flashMessages.forEach(function (message) {
        setTimeout(function () {
            message.style.opacity = "0";

            setTimeout(function () {
                message.remove();
            }, 500);

        }, 4000);
    });


    // ----------------------------------------
    // Confirm actions
    // ----------------------------------------
    const confirmButtons = document.querySelectorAll("[data-confirm]");

    confirmButtons.forEach(function (button) {
        button.addEventListener("click", function (event) {

            const message = button.getAttribute("data-confirm");

            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });


    // ----------------------------------------
    // Profile photo preview
    // ----------------------------------------
    const photoInput = document.getElementById("profile_photo");
    const photoPreview = document.getElementById("photoPreview");

    if (photoInput && photoPreview) {

        photoInput.addEventListener("change", function () {

            const file = this.files[0];

            if (!file) {
                return;
            }

            // Check file type
            const allowedTypes = [
                "image/jpeg",
                "image/png",
                "image/gif",
                "image/webp"
            ];

            if (!allowedTypes.includes(file.type)) {
                alert("Please select a JPG, PNG, GIF or WEBP image.");
                this.value = "";
                return;
            }

            // Check file size - 5 MB
            if (file.size > 5 * 1024 * 1024) {
                alert("Image size must be less than 5 MB.");
                this.value = "";
                return;
            }

            const reader = new FileReader();

            reader.onload = function (event) {
                photoPreview.src = event.target.result;
            };

            reader.readAsDataURL(file);
        });
    }


    // ----------------------------------------
    // Search users
    // ----------------------------------------
    const searchInput = document.getElementById("searchInput");
    const userCards = document.querySelectorAll(".user-card");

    if (searchInput && userCards.length > 0) {

        searchInput.addEventListener("input", function () {

            const searchText = this.value.toLowerCase().trim();

            userCards.forEach(function (card) {

                const text = card.innerText.toLowerCase();

                if (text.includes(searchText)) {
                    card.style.display = "";
                } else {
                    card.style.display = "none";
                }
            });
        });
    }


    // ----------------------------------------
    // Chat auto scroll
    // ----------------------------------------
    const chatBox = document.getElementById("chatBox");

    if (chatBox) {
        chatBox.scrollTop = chatBox.scrollHeight;
    }


    // ----------------------------------------
    // Chat form
    // ----------------------------------------
    const chatForm = document.getElementById("chatForm");
    const messageInput = document.getElementById("messageInput");

    if (chatForm && messageInput) {

        chatForm.addEventListener("submit", function () {

            if (messageInput.value.trim() === "") {
                return;
            }

            // Prevent accidental double submission
            const sendButton = chatForm.querySelector("button[type='submit']");

            if (sendButton) {
                sendButton.disabled = true;
                sendButton.innerText = "Sending...";
            }
        });
    }


    // ----------------------------------------
    // Mobile menu
    // ----------------------------------------
    const menuButton = document.getElementById("menuButton");
    const mobileMenu = document.getElementById("mobileMenu");

    if (menuButton && mobileMenu) {

        menuButton.addEventListener("click", function () {
            mobileMenu.classList.toggle("active");
        });
    }


    // ----------------------------------------
    // Password show/hide
    // ----------------------------------------
    const passwordToggles = document.querySelectorAll(".password-toggle");

    passwordToggles.forEach(function (toggle) {

        toggle.addEventListener("click", function () {

            const inputId = this.getAttribute("data-target");
            const passwordInput = document.getElementById(inputId);

            if (!passwordInput) {
                return;
            }

            if (passwordInput.type === "password") {
                passwordInput.type = "text";
                this.innerText = "Hide";
            } else {
                passwordInput.type = "password";
                this.innerText = "Show";
            }
        });
    });


    // ----------------------------------------
    // Prevent empty forms
    // ----------------------------------------
    const forms = document.querySelectorAll("form");

    forms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const requiredInputs = form.querySelectorAll("[required]");

            let valid = true;

            requiredInputs.forEach(function (input) {

                if (input.value.trim() === "") {
                    valid = false;
                    input.classList.add("input-error");
                } else {
                    input.classList.remove("input-error");
                }
            });

            if (!valid) {
                event.preventDefault();
                alert("Please fill in all required fields.");
            }
        });
    });

});