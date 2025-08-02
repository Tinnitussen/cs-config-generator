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

    console.log('Initializing sticky editor for element:', editorElement);

    const getContainerTop = () => {
        const top = editorContainerElement.getBoundingClientRect().top + window.scrollY;
        console.log('Container top calculated as:', top);
        return top;
    };

    let containerTop = 0;

    // Wait a bit for the layout to stabilize before getting the initial top position
    setTimeout(() => {
        containerTop = getContainerTop();
    }, 200);

    window.addEventListener('resize', () => {
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
        console.log('Scroll Y:', window.scrollY, 'Container Top:', containerTop);
        if (containerTop > 0 && window.scrollY > containerTop) {
            if (!editorElement.classList.contains('sticky')) {
                console.log('Making editor sticky');
                const containerWidth = editorContainerElement.offsetWidth;
                editorContainerElement.style.height = `${editorContainerElement.offsetHeight}px`;
                editorElement.style.width = `${containerWidth}px`;
                editorElement.classList.add('sticky');
            }
        } else {
            if (editorElement.classList.contains('sticky')) {
                console.log('Removing sticky from editor');
                editorElement.classList.remove('sticky');
                editorElement.style.width = '';
                editorContainerElement.style.height = '';
            }
        }
    });
};
