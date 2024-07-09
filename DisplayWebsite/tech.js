


window.addEventListener('load', function() {
    let converter = new showdown.Converter(),
    text      = '# hello, markdown!',
    html      = converter.makeHtml(text);

    document.querySelector('#container').innerHTML = html
})