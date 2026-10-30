<script>
(function(){
 const back=x=>{x=clamp(x);const c1=1.9,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2)};
 document.querySelectorAll('h1').forEach(h=>{const walk=(n,inEm)=>{if(n.nodeType==3){const f=document.createDocumentFragment();n.textContent.split(/(\s+)/).forEach(t=>{if(!t.trim()){f.appendChild(document.createTextNode(t))}else{const s=document.createElement('span');s.className='wd'+(inEm?' ac':'');s.textContent=t;s.style.display='inline-block';f.appendChild(s)}});n.replaceWith(f)}else{[...n.childNodes].forEach(c=>walk(c,inEm||n.tagName=='EM'))}};[...h.childNodes].forEach(c=>walk(c,false))});
 const st=document.createElement('style');st.textContent='h1 em{background:none!important;-webkit-background-clip:initial!important;color:inherit!important}.wd.ac{font-family:Crimson,serif;font-style:italic;font-weight:400;letter-spacing:-.02em;background:linear-gradient(95deg,#ffc9a8,#f6b6d4 45%,#b9a6ff);-webkit-background-clip:text;color:transparent;padding-right:.1em}';document.head.appendChild(st);
 const bts=document.querySelector('.bts');if(bts)[...bts.children].slice(1).forEach(c=>{c.style.opacity=0});
 const _s=window.setU;
 window.setU=async function(u){
  await _s(u);
  document.querySelectorAll('h1').forEach(h=>{const d=parseFloat(h.dataset.in||.1);h.style.opacity=1;h.style.transform='none';h.querySelectorAll('.wd').forEach((w,i)=>{const e=ease((u-d-i*.09)/.55);w.style.opacity=e;w.style.transform='translateY('+((1-e)*46)+'px) scale('+(.94+.06*e)+')';w.style.filter='blur('+((1-e)*12)+'px)'})});
  let idx=0;document.querySelectorAll('.photo[data-in],.card[data-in]').forEach(el=>{idx++;const d=parseFloat(el.dataset.in),e=clamp((u-d)/.7),eb=back(e),base=el.dataset.base||'';const fl=el.classList.contains('photo')?Math.sin(u*1.7+idx*1.3)*5:0;el.style.opacity=ease((u-d)/.4);el.style.transform=base+' translateY('+((1-eb)*60-fl)+'px) scale('+(.9+.1*eb)+')';if(el.classList.contains('prompt'))el.style.clipPath='inset(0 '+(100-100*ease((u-d)/.9))+'% 0 0 round 24px)'});
  if(bts)[...bts.children].slice(1).forEach((c,i)=>{const e=ease((u-3.2-i*.8)/.5);c.style.opacity=e;c.style.transform='translateX('+((1-e)*-40)+'px)'});
  const g=document.querySelector('.glow');if(g)g.style.transform='translate('+Math.sin(u*.5)*50+'px,'+Math.cos(u*.4)*40+'px) scale(1.2)';
  document.querySelectorAll('.tag i').forEach(i=>{i.style.boxShadow='0 0 '+(8+8*Math.sin(u*4))+'px var(--c,#fff)'});
  document.body.style.transformOrigin='50% 50%';document.body.style.transform='scale('+(1+.025*clamp(u/7))+')';
  const fb=document.querySelector('.foot .bar u');if(fb){if(!fb.dataset.w)fb.dataset.w=parseFloat(fb.style.width);const to=parseFloat(fb.dataset.w),from=Math.max(to-10,0);fb.style.width=(from+(to-from)*ease(u/.8))+'%'}
 }
})();
</script>
