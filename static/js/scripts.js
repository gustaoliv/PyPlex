function goBack(){
    window.history.back();
}
function VerificaVal(){
    if ($("#tipo_0").prop("checked")) {
        $('#val').val('2');
        $('#val').prop('readonly', true);
      }
    else{
        $('#val').val('');
        $('#val').prop('readonly', false);
    }
}