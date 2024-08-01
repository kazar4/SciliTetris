function truncateText() {
    const maxLength = 30; // Maximum number of characters for the truncated text
    const galleryItems = document.querySelectorAll('.gallery-item p');

    galleryItems.forEach(p => {
        let textContent = p.textContent;

        p.setAttribute("data-src", textContent);

        if (textContent.length > maxLength) {
            p.textContent = textContent.slice(0, maxLength) + '...';
        }
    });
}

function showPopup(element) {
    var popup = document.getElementById("popup");
    var popupImg = document.getElementById("popup-img");
    var popupIframe = document.getElementById("popup-iframe");
    var popupText = document.getElementById("popup-text");
    var overlay = document.getElementById("overlay");

    var img = element.querySelector("img");
    var iframeSrc = element.getAttribute("data-src");

    if (iframeSrc) {
        // If there's a data-src attribute, it's a video
        popupIframe.src = iframeSrc;
        popupIframe.style.display = "block";
        popupImg.style.display = "none";
    } else if (img) {
        popupImg.src = img.src;
        popupImg.style.display = "block";
        popupIframe.style.display = "none";
        // Remove src from iframe to stop video playback
        popupIframe.src = "";
    }

    popupText.textContent = element.querySelector("p").getAttribute("data-src");
    popup.style.display = "block";
    overlay.style.display = "block";
}

function hidePopup() {
    var popup = document.getElementById("popup");
    var overlay = document.getElementById("overlay");
    
    popup.style.display = "none";
    overlay.style.display = "none";

    // Clear the iframe src to stop video playback
    document.getElementById("popup-iframe").src = "";
}


function loadGallery(imageCount, galleryLoc, image_descriptions) {
    const gallery = document.querySelector('.gallery');
    for (let i = 1; i <= imageCount; i++) {
        const galleryItem = document.createElement('div');
        galleryItem.className = 'gallery-item';
        galleryItem.setAttribute('onclick', 'showPopup(this)');

        const img = document.createElement('img');
        img.src = `./${galleryLoc}/${i}.jpeg`;
        console.log(img.src)
        img.alt = `Image ${i}`;

        const description = document.createElement('p');
        if (image_descriptions.length >= i) {
            description.textContent = image_descriptions[i - 1];
        } else {
            description.textContent = `Image ${i} description`;
        }

        galleryItem.appendChild(img);
        galleryItem.appendChild(description);
        gallery.appendChild(galleryItem);
    }
}
