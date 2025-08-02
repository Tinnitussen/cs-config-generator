window.makeEditorSticky = function (editorElement) {
    if (!editorElement) {
        console.warn('Sticky element not provided.');
        return;
    }
    const editorContainerElement = editorElement.parentElement;
    if (!editorContainerElement) {
        console.warn('Sticky element\'s container not found.');
        return;
    }

    const getContainerTop = () => {
        return editorContainerElement.getBoundingClientRect().top + window.scrollY;
    };

    let containerTop = getContainerTop();
    
    // Recalculate on resize to handle responsive layout changes
    window.addEventListener('resize', () => {
        // Temporarily un-stick to get the correct original position
        const wasSticky = editorElement.classList.contains('sticky');
        if (wasSticky) {
            editorElement.classList.remove('sticky');
        }
        
        containerTop = getContainerTop();

        if (wasSticky) {
            editorElement.classList.add('sticky');
        }
    });

    window.addEventListener('scroll', function () {
        if (window.scrollY > containerTop) {
            if (!editorElement.classList.contains('sticky')) {
                const containerWidth = editorContainerElement.offsetWidth;
                // Before making it sticky, set a height on the container to prevent collapse.
                editorContainerElement.style.height = `${editorContainerElement.offsetHeight}px`;
                editorElement.style.width = `${containerWidth}px`;
                editorElement.classList.add('sticky');
            }
        } else {
            if (editorElement.classList.contains('sticky')) {
                editorElement.classList.remove('sticky');
                editorElement.style.width = '';
                editorContainerElement.style.height = ''; // Remove the height
            }
        }
    });
};
