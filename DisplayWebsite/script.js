let toggleOn = false;
const buttonContainer = document.querySelector('.button-container');
const originalButtonDetails = buttonContainer.innerHTML;
const mainButton = document.getElementById('main-button');
const positions = ['arc-1', 'arc-2', 'arc-3'];
const positionsText = ['tech details!', 'the project!', 'photos'];
const links = ["./tech.html", "./about.html", ""];

function changeLocation(i) {
    console.log("hi")
    console.log("going to " + links[i])
    window.location = links[i];
}

function toggleButton() {
    if (!toggleOn) {
        toggleOn = true;

        for (let i = 0; i < 3; i++) {
            const newButton = document.createElement('button');

            newButton.classList.add('arc', 'glow-on-hover', 'show');
            newButton.setAttribute("onclick", `changeLocation("${i}");`);
            newButton.innerHTML = '<span> ' + positionsText[i] + '</span>';

            buttonContainer.insertBefore(newButton, mainButton.nextSibling);

            setTimeout(() => {
                const buttons = document.getElementsByClassName('arc');
                for (let j = 0; j < buttons.length; j++) {
                    buttons[j].style.opacity = "1";
                    buttons[j].style.zIndex = "0";
                    buttons[j].classList.add(positions[j])
                }
            }, 300)

        }
    } else {
        toggleOn = false;
        setTimeout(() => {
            const buttons = document.getElementsByClassName('arc');
            for (let j = 0; j < buttons.length; j++) {
                buttons[j].style.opacity = "0";
                buttons[j].style.zIndex = "-1";
                buttons[j].classList.remove(positions[j])
            }
            setTimeout(() => {
                buttonContainer.innerHTML = originalButtonDetails;
            }, 300)
        }, 300)
    }
};
