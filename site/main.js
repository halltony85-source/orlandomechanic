
const burger=document.querySelector('.burger'),mnav=document.querySelector('.mnav');
if(burger&&mnav){
  const setOpen=v=>{mnav.classList.toggle('open',v);burger.setAttribute('aria-expanded',v?'true':'false');};
  burger.addEventListener('click',()=>setOpen(true));
  mnav.querySelector('.x').addEventListener('click',()=>setOpen(false));
  mnav.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>setOpen(false)));
}
