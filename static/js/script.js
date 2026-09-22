function toggleResponsavel(){
  const check = document.getElementById('eh_menor');
  const idade = document.getElementById('idade');
  const box = document.getElementById('box-responsavel');
  const isMenor = check.checked || (parseInt(idade.value) < 18);
  if(isMenor){
    box.style.display='block';
    document.getElementById('nome_responsavel').required=true;
  } else {
    box.style.display='none';
    document.getElementById('nome_responsavel').required=false;
  }
}
document.addEventListener('DOMContentLoaded',()=>{
  document.getElementById('idade').addEventListener('input',toggleResponsavel);
  document.getElementById('eh_menor').addEventListener('change',toggleResponsavel);
});
function copiarPix(){
  navigator.clipboard.writeText('33075478873');
  alert('Chave PIX copiada: 33075478873 - Priscila A. S. Moreira');
}
