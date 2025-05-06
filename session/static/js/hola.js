const myButton = document.querySelector(".btn-click-modal-form");
const myButtonDeleteAdmin = document.querySelectorAll(".btn-click-delete-administer-confirm")
const myButtonCloseModal = document.querySelector(".bx-x")
const myModal = document.querySelector(".box-modal")
const MyModalMessage = document.getElementById("messages-container")
const MyLoginMessageError = document.getElementById("mensaje");


console.log(MyLoginMessageError)

if (myButton && myModal) {
    myButton.addEventListener('click', function () {
        myModal.classList.remove('hidden')
        myModal.classList.add('flex')
    })
}

if (myButtonCloseModal && myModal) {
    myButtonCloseModal.addEventListener('click', function () {
        myModal.classList.add('hidden')
    })
}

if (MyModalMessage ) {
    setTimeout(() => {
        MyModalMessage.remove()
    }, 5000)
}

if (MyLoginMessageError) {
    setTimeout(() =>{
        MyLoginMessageError.remove()
    }, 5000)
}

