$('#cpass').on('keyup',function(){
   x=document.getElementById("cpass");
   if($('#pass').val()!=$('#cpass').val()){
       x.style.border="solid";
       x.style.borderWidth="2px";
       x.style.borderColor="#ff0000";
       return false;
   }
  else {
     x.style.border="none";
     x.style.borderWidth="0px";
     x.style.borderColor="#ff0000";
}
});
$('#registersubmit').on('submit',function(){
   if($('#pass').val()!=$('#cpass').val()){
       return false;
   }
   return true;
});