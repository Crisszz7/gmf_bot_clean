const statusMessage = document.getElementById('status--message')
const notExcel = document.getElementById('not-excel');
const closeModal = document.getElementById('modalin-close')
const iconCloseModal = document.getElementById('close')
const openModal = document.getElementById('openModal')
const modalinSendUserJob = document.getElementById('modalin-send-user-job')
const buttonMenuOptionsUser = document.getElementById('button--menu-options-user')
const menuOptionsUser = document.getElementById('menu-options-user')
const openModalSendJob = document.getElementById('open-modal-send-job')
const howShowInfo = document.getElementById('container-how-show-info')


// if(menuOptionsUser){
//     buttonMenuOptionsUser.addEventListener('click', function () {
//         menuOptionsUser.style.left = '3rem' 
//         menuOptionsUser.style.opacity = 1    
//     })
// }


function mostrarTabla() {
    document.getElementById('vista-card').classList.add('mhidden')
    document.getElementById('vista-table').classList.remove('mhidden')
        document.getElementById('vista-card').style.display = 'none'
}

function mostrarCard() {
    document.getElementById('vista-card').classList.remove('mhidden')
    document.getElementById('vista-table').classList.add('mhidden')
    document.getElementById('vista-card').style.display = 'grid';
    document.getElementById('vista-card').style.gridTemplateColumns = 'repeat(3, 1fr)'

}

// openModalSendJob.addEventListener('click', function() {
//     modalinSendUserJob.classList.add('open');
// })

if(openModal){
    openModal.addEventListener('click', function () {
        closeModal.classList.add('open');
    })
}

if(iconCloseModal){
    iconCloseModal.addEventListener('click', function() {
        closeModal.classList.remove('open');
    })
}

document.querySelectorAll('.tool-menu-edit-delete-postulante').forEach((icon) => {
    icon.addEventListener('click', function () {

        document.querySelectorAll('.menu-edit-delete-postulante').forEach(menu => menu.classList.add('hidden'));

        // Busca el td donde está el ícono
        const parentTd = icon.closest('td');
        const nextTd = parentTd?.nextElementSibling; //	Busca el <td> que está justo después del que contiene el ícono.

        // Si el siguiente td tiene el menú, lo alternamos
        const menu = nextTd?.querySelector('.menu-edit-delete-postulante');
        if (menu) {
            menu.classList.toggle('hidden'); //toggle() elimina o añade una clase de css dependiendo si ya la tiene o no
        }
    });
});

document.addEventListener('click', function (e) {
    if (!e.target.closest('.tool-menu-edit-delete-postulante') && //e.target → el elemento exacto donde hiciste clic.
        !e.target.closest('.menu-edit-delete-postulante')) { //.closest(selector) → busca el ancestro más cercano (padre, abuelo, etc.) que coincida con ese selector.
        document.querySelectorAll('.menu-edit-delete-postulante').forEach(menu => {
            menu.classList.add('hidden');
        });
    }
});




if(statusMessage){
    setTimeout(()=>{
        statusMessage.remove()
    }, 5000)
}

if (notExcel) {
    setTimeout(()=> {
        notExcel.remove()
    }, 5000)
}