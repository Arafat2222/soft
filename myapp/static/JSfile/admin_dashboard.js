
// Add this with your other JavaScript functions
function searchDoctors() {
    const searchQuery = document.getElementById('doctorSearch').value;
    const tbody = document.querySelector('table tbody');

    fetch(`/search_doctors/?query=${encodeURIComponent(searchQuery)}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            tbody.innerHTML = ''; // Clear existing rows
            
            data.doctors.forEach(doctor => {
                const row = document.createElement('tr');
                row.className = 'hover:bg-gray-50 transition duration-200';
                row.dataset.id = doctor.id;
                row.dataset.fullName = doctor.full_name;
                row.dataset.username = doctor.username;
                row.dataset.email = doctor.email;
                row.dataset.degrees = doctor.degrees;
                row.dataset.experience = doctor.experience;
                row.dataset.categoryId = doctor.category_id;
                row.dataset.description = doctor.description;

                row.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                            ${doctor.image_url ? 
                                `<img class="h-10 w-10 rounded-full object-cover" src="${doctor.image_url}" alt="${doctor.full_name}">` :
                                `<div class="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                                    <i class="fas fa-user-md text-gray-400"></i>
                                </div>`
                            }
                            <div class="ml-4">
                                <div class="text-sm font-medium text-gray-900">${doctor.full_name}</div>
                            </div>
                        </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${doctor.username}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                            ${doctor.category_type}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${doctor.email}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${doctor.degrees}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${doctor.experience} years</td>
                    <td class="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">${doctor.description}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button onclick="openEditModal(
                            '${doctor.id}',
                            '${doctor.full_name}',
                            '${doctor.username}',
                            '${doctor.email}',
                            '${doctor.degrees}',
                            '${doctor.experience}',
                            '${doctor.category_id}',
                            '${doctor.description}'
                        )" class="text-blue-600 hover:text-blue-900 mr-3">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button onclick="confirmDelete('${doctor.id}')" class="text-red-600 hover:text-red-900">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error searching doctors');
    });
}

// Add event listener for real-time search
let searchTimeout;
document.getElementById('doctorSearch').addEventListener('input', function() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(searchDoctors, 500); // Search after 500ms of typing
});
