document.addEventListener('DOMContentLoaded', function() {
    // Add subtle animation to error page elements
    const errorContainer = document.querySelector('.error-container');
    if (errorContainer) {
        errorContainer.style.opacity = '0';
        errorContainer.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            errorContainer.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            errorContainer.style.opacity = '1';
            errorContainer.style.transform = 'translateY(0)';
        }, 100);
    }
    
    // Add pulse animation to error code
    const errorCode = document.querySelector('.error-page h1');
    if (errorCode) {
        setInterval(() => {
            errorCode.classList.add('pulse-animation');
            setTimeout(() => {
                errorCode.classList.remove('pulse-animation');
            }, 1000);
        }, 3000);
    }
});

// Add CSS for pulse animation
document.head.insertAdjacentHTML('beforeend', `
<style>
.pulse-animation {
    animation: pulse 1s ease;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}
</style>
`); 