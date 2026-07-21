let I = new Instance();
document.getElementById("run").addEventListener("click", (e) => {
  console.log("ok");
  //console.log(document.getElementById("code").value)
  console.log(I.execute(document.getElementById("code").value));
});
