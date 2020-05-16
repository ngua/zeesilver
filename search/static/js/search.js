const searchForm = document.querySelector('#search');
const searchIcon = searchForm.querySelector('i');
let clicks = 0;
searchIcon.addEventListener('click', () => {
  'ontouchstart' in document.documentElement && clicks === 0 ? clicks++ : searchForm.submit();
});
