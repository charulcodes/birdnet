
var slideIndex = 1, n=1;
showSlides();

function changeSlide(n)
{
    showSlide(slideIndex += n);
}
function showSlide(n)
{
    var slides = document.getElementsByClassName("slide");
    // var captions = document.getElementsByClassName("caption");
    if(n>slides.length) { slideIndex=1; }
    if(n<1) { slideIndex=slides.length; }
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
        // captions[i].style.display = "none";
    }
    slides[slideIndex-1].style.display = "block";
    // captions[slideIndex-1].style.display = "block";
}

function showSlides() {
    var i;
    var slides = document.getElementsByClassName("slide");
    // var captions = document.getElementsByClassName("caption");
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
        // captions[i].style.display = "none";
    }
    slideIndex++;
    if (slideIndex > slides.length) {slideIndex = 1}
    slides[slideIndex-1].style.display = "block";
    // captions[slideIndex-1].style.display = "block";
    setTimeout(showSlides, 7000); // Change image every 7 seconds
}