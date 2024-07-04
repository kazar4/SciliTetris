const randomHexColorCode = () => {
    let n = (Math.random() * 0xfffff * 1000000).toString(16);
    return '#' + n.slice(0, 6);
  };

function makeGrid() {
    console.log("Creating Grid")

    const notebookGrid = document.querySelector(".tetris-grid")
    
    notebookGrid.innerHTML = "";
      
    randomHexColorCode();

    // Create grid items
    let rows = 15; // Adjust number of rows as needed
    let cols = 10 ; // Adjust number of columns as needed

    let colors = {0: "#000000", 1: "#FFFFFF", 2: "#FF0000", 3: "#FF00FF", 4: "#00FFFF"}

    twoDArr = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 4, 4, 0, 0, 2, 0, 2, 0, 0, 0, 0],
        [0, 0, 0, 4, 0, 0, 4, 0, 2, 0, 2, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 4, 0, 2, 2, 2, 2, 0, 0, 0],
        [0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 2, 0, 0, 0, 0],
        [0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0],
        [0, 0, 0, 4, 4, 4, 4, 0, 0, 0, 2, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ];

    for (let i = 0; i < rows; i++) {
        console.log(i)
        for (let j = 0; j < cols; j++) {
            const gridItem = document.createElement('div');
            gridItem.classList.add('grid-item');
    
            //x = i
            //i % cols;
            //y = j
            //Math.trunc(i / rows);
    
            //console.log(twoDArr[y][x])
    
            // console.log(y, x)
            // console.log(twoDArr[x][y])
    
            // Randomly fill some grid item
            //Math.random() < 0.2
           // if (twoDArr[y][x] != 0) { // Adjust fill probability as needed
    
                //console.log(y, x)
               // gridItem.classList.add('filled');
    
            gridItem.style.backgroundColor = colors[twoDArr[i][j]]
                //randomHexColorCode();
           // }
    
            notebookGrid.appendChild(gridItem);
        }
    }
}

function makeGridAnimate() {
    console.log("Creating Grid")

    const notebookGrid = document.querySelector(".tetris-grid")
    
    notebookGrid.innerHTML = "";
      

    // Create grid items
    let rows = 15; // Adjust number of rows as needed
    let cols = 10 ; // Adjust number of columns as needed

    let colors = {0: "#000000", 1: "#FFFFFF", 2: "#FF0000", 3: "#FF00FF", 8: "#00FFFF", 6:"rgb(128,0,128)"}


    // for (let i = 0; i < rows; i++) {
    //     console.log(i)
    //     for (let j = 0; j < cols; j++) {
    //         const gridItem = document.createElement('div');
    //         gridItem.classList.add('grid-item');

    //         gridItem.style.backgroundColor = colors[twoDArr[i][j]]
    //         notebookGrid.appendChild(gridItem);
    //     }
    // }

    let currentFrame = 0;

        function displayFrame() {
            notebookGrid.innerHTML = ''; // Clear the previous frame
            const twoDArr = frameData.frames[currentFrame];
            for (let i = 0; i < rows; i++) {
                for (let j = 0; j < cols; j++) {
                    const gridItem = document.createElement('div');
                    gridItem.classList.add('grid-item');
                    gridItem.style.backgroundColor = colors[twoDArr[i][j]];
                    notebookGrid.appendChild(gridItem);
                }
            }
            currentFrame = (currentFrame + 1) % frameData.frames.length; // Loop back to the first frame
        }

        setInterval(displayFrame, 500);
}

document.addEventListener("DOMContentLoaded", () => {
    const text = document.querySelector(".handwriting-logo");
    //var text = document.createElementNS(svgNS, 'text');
    const letters = "SciLi Tetris".split("");
    //text.textContent.split("");
    // text.textContent = "";

    var svgNS = "http://www.w3.org/2000/svg";

    console.log("DOM LOADED");

    seperatations = [25, 25, 22, 23.5, 25.5, 25, 25, 24.3, 24.2, 24.2, 23.5, 23]
    
    letters.forEach((letter, index) => {

        setTimeout(() => {
            // console.log("turn on")
            // span.style.opacity = "1";
            // span.style.transition = "opacity 0.3s";
            // span.display = "block";
            const span = document.createElementNS(svgNS, "text");
            span.innerHTML = letter;
            span.style.opacity = "1";
            span.setAttribute("x", 12 + seperatations[index] * index + "px");
            span.setAttribute("y", "80%");
            span.setAttribute("text-anchor", "middle");
            text.appendChild(span);

        }, 300 * index);
    });


    //makeGrid();
    makeGridAnimate()
});

window.addEventListener("resize", () => {
    //makeGrid();
    makeGridAnimate()
})
