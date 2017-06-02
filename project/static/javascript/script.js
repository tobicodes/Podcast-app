
$(function() {
  $('.save-form').on('submit', function(e){
    var id = $(this).data('id')
    e.preventDefault();
    $.ajax({
      method: 'POST',
      url: "/users/liked/"+id
    }).then(function(obj){
      $(e.target).find('input').attr('disabled','disabled')
    })
  })
    
});

