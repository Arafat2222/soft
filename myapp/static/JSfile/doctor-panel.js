// Experience Input Handling
function getExperienceValue() {
    let exp = document.getElementById('experience').value;
    return parseInt(exp) || 0;
}

function updateExperience(value) {
    const expInput = document.getElementById('experience');
    if (value < 0) expInput.value = 0;
    if (value > 50) expInput.value = 50;
}

// Alert Auto Dismiss
function initializeAlerts() {
    window.setTimeout(function() {
        $(".alert").fadeTo(500, 0).slideUp(500, function(){
            $(this).remove(); 
        });
    }, 5000);
}

// Password Toggle
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const toggleIcon = document.getElementById('toggleIcon');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.classList.remove('fa-eye');
        toggleIcon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        toggleIcon.classList.remove('fa-eye-slash');
        toggleIcon.classList.add('fa-eye');
    }
}

// Tab Navigation
function initializeTabs() {
    $('.list-group-item').on('click', function (e) {
        e.preventDefault();
        $(this).tab('show');
    });
}

// Form Validation
function initializeFormValidation() {
    'use strict';
    window.addEventListener('load', function() {
        var forms = document.getElementsByClassName('needs-validation');
        Array.prototype.filter.call(forms, function(form) {
            form.addEventListener('submit', function(event) {
                if (form.checkValidity() === false) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    });
}

// Initialize all functions when document is ready
$(document).ready(function() {
    initializeAlerts();
    initializeTabs();
    initializeFormValidation();
});

// Image Preview
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            $('#imagePreview').attr('src', e.target.result);
        }
        reader.readAsDataURL(input.files[0]);
    }
}

// Profile Update Confirmation
function confirmProfileUpdate() {
    return confirm('Are you sure you want to update your profile?');
}