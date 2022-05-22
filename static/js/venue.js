const deleteBtn = document.getElementById("delete-button");
deleteBtn.onclick = function (e) {
  const venueId = e.target.dataset["id"];
  fetch("/venues/" + venueId, {
    method: "DELETE",
  })
    .then((response) => response.json())
    .then(data => console.log(data))
    .then((window.location.href = "/"));
};
