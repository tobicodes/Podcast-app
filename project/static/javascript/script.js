console.log("yo")

$(function() {
    $.ajax({
      url: "/users/40/requests"
    }).then(function(obj){
      console.log(obj)
    })
});

