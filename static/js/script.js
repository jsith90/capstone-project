var modal = document.getElementById('id01');
var modal2 = document.getElementById('id02');
var modal3 = document.getElementById('nav-links');
var modal4 = document.getElementById("messageModal");

// table booking delete modal
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

// table booking edit modal
window.onclick = function(event) {
  if (event.target == modal2) {
    modal2.style.display = "none";
  }
}

// navbar links modal
window.onclick = function(event) {
  if (event.target == modal3) {
    modal3.style.display = "none";
  }
}

// When the page loads, check if there are messages and show the modal if there are
if (document.getElementById("messages").childElementCount > 0) {
  modal4.style.display = "block";
}

// search bookings in staff panel
$(document).ready(function(){
  $("#myInput").on("keyup", function() {
    var value = $(this).val().toLowerCase();
    $("#myTable tr").filter(function() {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
    });
  });
});

console.log('hello world');