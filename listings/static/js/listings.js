const togglers = document.querySelectorAll('.toggler');
Array.prototype.map.call(togglers, (toggler => {
  const icon = toggler.querySelector('.fas')
  if ('ontouchstart' in document.documentElement || screen.width < 968) {
    toggler.Collapse.hide();
    swapIcon(icon);
  }
  toggler.addEventListener('click', () => {
    swapIcon(icon)
  });
}));

function swapIcon(icon) {
  icon.classList.replace('fa-plus', 'fa-minus') || icon.classList.replace('fa-minus', 'fa-plus');
}
