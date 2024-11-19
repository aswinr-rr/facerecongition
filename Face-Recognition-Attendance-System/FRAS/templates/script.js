document.addEventListener('DOMContentLoaded', function() {
    // Real-time validation for all forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = form.querySelectorAll('input[required]');
            let valid = true;
            inputs.forEach(input => {
                if (input.value.trim() === '') {
                    input.classList.add('input-error');
                    valid = false;
                } else {
                    input.classList.remove('input-error');
                }
            });

            if (!valid) {
                e.preventDefault(); // Prevent form submission if not valid
                alert('Please fill in all required fields.');
            } else {
                // Disable the submit button to prevent multiple clicks
                form.querySelector('button[type="submit"]').disabled = true;
            }
        });
    });

    // Show/hide date inputs based on attendance delete option
    const useTodayRadios = document.querySelectorAll('input[name="use_today"]');
    const dateInputs = document.getElementById('date-inputs');

    if (useTodayRadios.length) { // Check if delete attendance form exists
        useTodayRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'no') {
                    dateInputs.style.display = 'block'; // Show date inputs
                } else {
                    dateInputs.style.display = 'none'; // Hide date inputs
                }
            });
        });

        // Initially hide date inputs if "yes" is selected by default
        if (document.querySelector('input[name="use_today"]:checked').value === 'yes') {
            dateInputs.style.display = 'none';
        }
    }
});
