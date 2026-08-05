const id = (e) => {
  return document.getElementById(e);
};
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
let I = new Instance();
I.customs["puts"] = async (e) => {
  id("output").value += e.join(" ") + "\n";
  await delay(100);
};
I.customs["gets"] = async (e) => {
  let t = prompt(e.join(" ")) ?? "";
  await delay(100);
  return t;
};
I.customs["lit"] = (e) => {
  return e.join(" ");
};
/**
 *  @type {AbortController|null}
 */
let a = null;
id("run").addEventListener("click", async (e) => {
  id("output").value = "";
  a?.abort();
  a = new AbortController();
  I.variables = {};
  I.globals = {};
  I.procedures = {};
  I.scope_stack = [];
  I.execute(id("code").value, a.signal).then((e) => {
    if (e.status == TINT_ERR) {
      id("output").value += `Error: ${e.result}\n`;
    }
  });
});
id("halt").addEventListener("click", (e) => {
  a?.abort();
});
