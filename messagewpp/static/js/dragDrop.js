function allowDrop(event) {
    event.preventDefault(); // Permitir soltar en la zona objetivo
}

function drag(event) {
    console.log("Elemento arrastrado:", event.target); // Verificar el elemento arrastrado
    if (!event.target.id) {
        console.error("Error: El elemento arrastrado no tiene un ID.");
        return;
    }
    event.dataTransfer.setData("text", event.target.id); // Guardar el ID del elemento
}

function drop(event) {
    event.preventDefault();
    const data = event.dataTransfer.getData("text");
    console.log("Intentando soltar elemento con ID:", data);
    
    if (!data) {
        console.error("Error: No se recibió ningún ID.");
        return;
    }
    
    const draggedElement = document.getElementById(data);
    if (!draggedElement) {
        console.error("Error: No se encontró el elemento con ID:", data);
        return;
    }
    
    // Verificar si el objetivo es un textarea
    if (event.target.tagName === "TEXTAREA") {

        const text = draggedElement.textContent.trim();
        
        // Agregar el contenido del elemento arrastrado al textarea

        event.target.value += text + "\n";
    } else {
        // Si no es un textarea, no hacer nada o mostrar un mensaje de error
        console.error("Error: Solo se puede soltar en un textarea.");
    }
}


