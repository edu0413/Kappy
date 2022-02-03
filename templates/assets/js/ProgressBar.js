$(document).ready(function(){
    $('.progress-value > span').each(function(){
        $(this).prop('Counter',0).animate({
            Counter: $(this).text() * 100
        },{
            duration: 2500,
            easing: 'swing',
            step: function (now){
                $(this).text(Math.ceil(now)/100);
            }
        });
    });
});