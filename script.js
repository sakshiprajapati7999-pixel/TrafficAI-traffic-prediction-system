// ==============================
// TrafficAI Home Page JS
// ==============================

// Navbar Shadow on Scroll
window.addEventListener("scroll", function () {

    const navbar = document.querySelector(".custom-nav");

    if (window.scrollY > 50) {
        navbar.style.background = "#08101f";
        navbar.style.boxShadow = "0 8px 20px rgba(0,0,0,.35)";
    } else {
        navbar.style.background = "#0F172A";
        navbar.style.boxShadow = "none";
    }

});


// ==============================
// Counter Animation
// ==============================

const counters = document.querySelectorAll(".counter");

counters.forEach(counter => {

    const updateCounter = () => {

        const target = +counter.getAttribute("data-target");
        const count = +counter.innerText;

        const increment = Math.ceil(target / 100);

        if (count < target) {

            counter.innerText = count + increment;

            setTimeout(updateCounter, 20);

        } else {

            counter.innerText = target;

        }

    };

    updateCounter();

});


// ==============================
// Smooth Scroll
// ==============================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {

    anchor.addEventListener("click", function (e) {

        e.preventDefault();

        document.querySelector(this.getAttribute("href")).scrollIntoView({

            behavior: "smooth"

        });

    });

});

console.log("TrafficAI Home Loaded Successfully");