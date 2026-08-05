const id = (e) => {
  return document.getElementById(e);
};
let status = true;
/**@type {Worker|null}*/
let worker = null;
id("run").addEventListener("click", async (e) => {
  if (status) {
    status = false;
    id("output").value = "";
    id("run").innerHTML = "HALT";
    worker = new Worker("worker.js");
    worker.onmessage = async (e) => {
      //console.log(e.data)
      if (e.data.done === true) {
        worker = null;
        id("run").innerHTML = "EXEC";
        status = true;
        id("output").value += e.data.data.result + "\n";
      } else {
        id("output").value += e.data.data + "\n";
      }
    };
    worker.postMessage(id("code").value);
  } else {
    worker?.terminate();
    worker = null;
    id("run").innerHTML = "EXEC";
    status = true;
  }
});
