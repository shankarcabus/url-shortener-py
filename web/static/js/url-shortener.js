$(function(){
  $(".main-field").on("submit", function(){

    var originalUrl = $(".field-input").val(),
      $urlBox = $('.short-url-box'),
      $mainField = $('.main-field');

    // Clean validation
    $mainField.removeClass('invalid');

    // Loading state
    $urlBox.removeClass('loaded')
      .addClass('loading');

    $.ajax({
      type: "POST",
      url: '/save',
      data: {
        url: originalUrl
      },
      success: function(data){
        $urlBox.removeClass('loading') // Removes loading
          .addClass('loaded')
          .find('.short-url')
          .text(data)
          .select();
      },
      error: function(){
        $mainField.addClass('invalid');
      }
    });
    return false;
  });
});
