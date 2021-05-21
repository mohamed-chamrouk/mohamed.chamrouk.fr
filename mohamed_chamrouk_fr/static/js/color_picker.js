function getInputValue(){
  // Selecting the input element and get its value
  var inputVal = document.getElementById("colorInput").value;

  if (inputVal == 0) {
    document.documentElement.style.setProperty('--primary-color', '#62c4ff');
  } else if (inputVal.length != 7) {
    window.alert("Seule les valeurs héxadécimale sont supportées.");
    document.documentElement.style.setProperty('--primary-color', '#62c4ff');
  } else {
    document.documentElement.style.setProperty('--primary-color', inputVal);
  }

}
