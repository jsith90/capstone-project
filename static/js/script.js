const modal = document.getElementById('delete');
const modal2 = document.getElementById('edit');
const modal3 = document.getElementById('nav-links');
const modal4 = document.getElementById("messageModal");

// table booking delete modal
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
};

// table booking edit modal
window.onclick = function(event) {
  if (event.target == modal2) {
    modal2.style.display = "none";
  }
};

// navbar links modal
window.onclick = function(event) {
  if (event.target == modal3) {
    modal3.style.display = "none";
  }
};

// messages modal
if (document.getElementById("messages").childElementCount > 0) {
  modal4.style.display = "block";
}
      