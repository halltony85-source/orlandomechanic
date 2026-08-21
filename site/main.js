
const burger=document.querySelector('.burger'),mnav=document.querySelector('.mnav');
if(burger&&mnav){
  burger.addEventListener('click',()=>mnav.classList.add('open'));
  mnav.querySelector('.x').addEventListener('click',()=>mnav.classList.remove('open'));
  mnav.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>mnav.classList.remove('open')));
}
