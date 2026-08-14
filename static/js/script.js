const menuBtn = document.getElementById("menuBtn");
const navMenu = document.getElementById("navMenu");


// ================= MOBILE MENU =================

if (menuBtn && navMenu) {

    menuBtn.addEventListener("click", () => {
        navMenu.classList.toggle("active");
    });

}


// Close menu after clicking a navigation link

document.querySelectorAll("#navMenu a").forEach(link => {

    link.addEventListener("click", () => {

        if (navMenu) {
            navMenu.classList.remove("active");
        }

    });

});


// ================= BOOKING FORM =================

const bookingForm = document.getElementById("bookingForm");

if (bookingForm) {

    bookingForm.addEventListener("submit", async function(event) {

        event.preventDefault();


        const name =
            document.getElementById("name").value.trim();

        const phone =
            document.getElementById("phone").value.trim();

        const service =
            document.getElementById("service").value;

        const date =
            document.getElementById("date").value;

        const time =
            document.getElementById("time").value;

        const request =
            document.getElementById("request").value.trim();


        // Check required fields

        if (!name || !phone || !service || !date || !time) {

            alert(
                "Please complete all required fields."
            );

            return;
        }


        // Prevent booking a date in the past

        const selectedDate =
            new Date(date + "T00:00:00");

        const today =
            new Date();

        today.setHours(0, 0, 0, 0);


        if (selectedDate < today) {

            alert(
                "Please select today or a future date."
            );

            return;
        }


        // Show temporary message

        const button =
            bookingForm.querySelector(
                ".booking-button"
            );

        const originalText =
            button.textContent;

        button.textContent =
            "SUBMITTING...";

        button.disabled = true;


        try {

            const response = await fetch(
                "/book",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        name: name,
                        phone: phone,
                        service: service,
                        date: date,
                        time: time,
                        request: request

                    })
                }
            );


            const result =
                await response.json();


            if (result.success) {

                alert(
                    "✓ APPOINTMENT REQUEST RECEIVED!\n\n" +

                    "Name: " +
                    result.name +

                    "\nService: " +
                    result.service +

                    "\nDate: " +
                    result.date +

                    "\nTime: " +
                    result.time +

                    "\n\nThank you for choosing " +
                    "DESTINY'S CUT."
                );


                bookingForm.reset();

            } else {

                alert(
                    result.message ||
                    "Unable to submit your appointment."
                );

            }


        } catch (error) {

            console.error(
                "Booking error:",
                error
            );

            alert(
                "Could not connect to the booking server.\n\n" +
                "Please make sure the Flask server is running."
            );

        }


        button.textContent =
            originalText;

        button.disabled = false;

    });

      }
