/*
Fichier regroupant les éléments relatifs au changement de thème
*/

const htmlEl = document.getElementsByTagName('html')[0];
const toggleTheme = (theme) => {
  htmlEl.dataset.theme = theme;
}

// recherche dans les cookies la présence d'une valeur pour le thème
if (document.cookie.split(';').some(function(item) {
  return item.trim().lastIndexOf('theme=') == 0
})) {
  if (document.cookie.split(';').some(function(item) {
    return item.lastIndexOf('theme=light') >= 0
  })) {
    toggleTheme('light');
  } else {
    toggleTheme('dark');
  }
}

//fonction de changement de thème
function changeTheme() {
  var checkbox = document.getElementById("darkSwitch");

  if (checkbox.checked == true){
    toggleTheme('light');
    document.cookie = "theme=light; path=/";
  } else {
    toggleTheme('dark');
    document.cookie = "theme=dark; path=/";
  }
}
$(document).on("click", ".action-buttons .dropdown-menu", function(e){
  e.stopPropagation();
});
