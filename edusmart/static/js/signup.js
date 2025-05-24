document.addEventListener('DOMContentLoaded', function() {
    console.log('signup.js loaded'); // Debug: Confirm script runs

    const userTypeSelect = document.getElementById('user_type');
    const fields = {
        roll_number: document.getElementById('roll_number_field'),
        department: document.getElementById('department_field'),
        designation: document.getElementById('designation_field'),
        course: document.getElementById('course_field'),
        branch: document.getElementById('branch_field'),
        admin_token: document.getElementById('admin_token_field')
    };

    // Debug: Log elements
    console.log('user_type:', userTypeSelect);
    console.log('Fields:', fields);

    // Check if user_type select exists
    if (!userTypeSelect) {
        console.error('Error: user_type select not found');
        return;
    }

    // Check if all fields exist
    for (const [key, field] of Object.entries(fields)) {
        if (!field) {
            console.error(`Error: ${key}_field not found`);
        }
    }

    function toggleFields() {
        const role = userTypeSelect.value;
        console.log('Role selected:', role); // Debug: Log role change

        // Hide all fields and remove required attribute
        Object.values(fields).forEach(field => {
            if (field) {
                field.classList.add('field-hidden');
                const input = field.querySelector('input');
                if (input) input.required = false;
            }
        });

        // Show and set required fields based on role
        if (role === 'student') {
            fields.roll_number.classList.remove('field-hidden');
            fields.course.classList.remove('field-hidden');
            fields.branch.classList.remove('field-hidden');
            if (fields.roll_number) fields.roll_number.querySelector('input').required = true;
        } else if (role === 'teacher') {
            fields.department.classList.remove('field-hidden');
            fields.designation.classList.remove('field-hidden');
            if (fields.department) fields.department.querySelector('input').required = true;
            if (fields.designation) fields.designation.querySelector('input').required = true;
        } else if (role === 'admin') {
            fields.admin_token.classList.remove('field-hidden');
            if (fields.admin_token) fields.admin_token.querySelector('input').required = true;
        }
    }

    // Attach change event listener
    userTypeSelect.addEventListener('change', toggleFields);

    // Set initial state
    toggleFields();
});