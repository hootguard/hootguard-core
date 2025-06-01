function loadComponent(componentId, filePath, callback) {
    fetch(filePath)
        .then(response => response.text())
        .then(data => {
            document.getElementById(componentId).innerHTML = data;
            if (callback) callback(); // Call the callback function if provided
        })
        .catch(err => console.error('Error loading the component:', err));
}

// Function to fetch the version from version.txt and update the footer
function fetchVersion() {
    fetch('/hootguard/version/version.txt') // Update this path if needed
        .then(response => response.text())
        .then(version => {
            const footerElement = document.querySelector('footer p');
            if (footerElement) {
                footerElement.innerHTML = `HootGuard © 2024<br>Version ${version.trim()}`;
            }
        })
        .catch(err => console.error('Error fetching version:', err));
}

document.addEventListener("DOMContentLoaded", function() {
    // Load navigation
    loadComponent('navigation-placeholder', '/hootguard/components/navigation.html');
    
    // Load footer and fetch version after loading the footer
    loadComponent('footer-placeholder', '/hootguard/components/footer.html', fetchVersion);
});
