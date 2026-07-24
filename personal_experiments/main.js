// @ts-check
// TINT Is Not Tcl
// A simple scripting language that fit in 180-ish lines of Python, now ported to JS for web reasons!
/**
 *
 * @param {{result:String|null,status:Number}} x
 * @returns {Boolean}
 */
function istrue(x) {
  return x.result != "0" && x.result != " ";
}
const TINT_OK = 0;
const TINT_ERR = 1;
const TINT_BREAK = 2;
const TINT_CONTINUE = 3;
const TINT_RETURN = 4;

class Instance {
  constructor() {
    /** @type {Record<string, string>} */
    this.variables = {};
    /** @type {Record<string, string>} */
    this.globals = {};
    /** @type {Record<string, {args:Array<string>,body:String}>} */
    this.procedures = {};
    /** @type {Record<string, Function>} */
    this.customs = {};
    /** @type {Array<Record<string, string>>} */
    this.scope_stack = [];
    this.running = false;
  }
  reset() {
    /** @type {Record<string, string>} */
    this.variables = {};
    /** @type {Record<string, string>} */
    this.globals = {};
    /** @type {Record<string, {args:Array<string>,body:String}>} */
    this.procedures = {};
    /** @type {Record<string, Function>} */
    this.customs = {};
    /** @type {Array<Record<string, string>>} */
    this.scope_stack = [];
    this.running = false;
  }
  /**
   * Executes a TINT command. FOR INTERNAL USE ONLY!
   * @param {Array<String>} c A command to run.
   * @param {AbortSignal} sig
   * @returns {Promise<{result:String|null,status:Number}>}
   */
  async run(c, sig) {
    if (sig.aborted) {
      throw new DOMException("Aborted", "AbortError");
    }
    console.log(c);
    /**@type {String|null} */
    let res = null;
    let t;
    if (c.length == 0) {
      return { status: TINT_OK, result: null };
    }
    let cmd = c[0];
    switch (cmd) {
      case "$":
        res = this.variables[c[1]] ?? "";
        break;
      case "$_":
        res = this.globals[c[1]] ?? "";
        break;
      case "set":
        this.variables[c[1]] = c[2] ?? "";
        break;
      case "set_":
        this.globals[c[1]] = c[2] ?? "";
        break;
      case "+":
        t = Number(c[1]) + Number(c[2]);
        res = (isNaN(t) ? "" : t).toString();
        break;
      case "-":
        t = Number(c[1]) - Number(c[2]);
        res = (isNaN(t) ? "" : t).toString();
        break;
      case "*":
        t = Number(c[1]) * Number(c[2]);
        res = (isNaN(t) ? "" : t).toString();
        break;
      case "/":
        t = Number(c[1]) / Number(c[2]);
        res = (isNaN(t) ? "" : t).toString();
        break;
      case "%":
        t = Number(c[1]) % Number(c[2]);
        res = (isNaN(t) ? "" : t).toString();
        break;
      case ">":
        t = Number(c[1]) > Number(c[2]);
        res = t ? "1" : "0";
        break;
      case "<":
        t = Number(c[1]) < Number(c[2]);
        res = t ? "1" : "0";
        break;
      case ">=":
        t = Number(c[1]) >= Number(c[2]);
        res = t ? "1" : "0";
        break;
      case "<=":
        t = Number(c[1]) <= Number(c[2]);
        res = t ? "1" : "0";
        break;
      case "==":
        t = c[1] == c[2];
        res = t ? "1" : "0";
        break;
      case "!=":
        t = c[1] != c[2];
        res = t ? "1" : "0";
        break;
      case "ord":
        res = c[1].codePointAt(0)?.toString() ?? "-1";
        break;
      case "chr":
        res = String.fromCharCode(parseInt(c[1]) ?? 0);
        break;
      case "len":
        res = c[1].length.toString();
        break;
      case "at":
        res = c[1].at(parseInt(c[2])) ?? "";
        break;
      case "break":
        return { status: TINT_BREAK, result: "" };
      case "continue":
        return { status: TINT_CONTINUE, result: "" };
      case "return":
        return { status: TINT_RETURN, result: c[1] ?? "" };
      case "if":
        if (c.length == 3) {
          t = await this.execute("expr "+(c[1] ?? ""), sig);
          if (t.status == TINT_ERR) {
            return t;
          }
          if (istrue(t)) {
            t = await this.execute(c[2] ?? "", sig);
            if (t.status != TINT_OK) {
              return t;
            }
          }
        } else if ((c.length + 1) % 3 == 0) {
          let flag = true;
          for (let i = 1; i < c.length - 3; i += 3) {
            t = await this.execute("expr "+(c[i] ?? ""), sig);
            if (t.status == TINT_ERR) {
              return t;
            }
            if (istrue(t)) {
              t = await this.execute(c[i + 1] ?? "", sig);
              if (t.status != TINT_OK) {
                return t;
              }
              flag = false;
              break;
            }
          }
          if (flag) {
            t = await this.execute(c[c.length - 1] ?? "", sig);
            //console.log("ELSE",t)
            if (t.status != TINT_OK) {
              return t;
            }
          }
        } else {
          return { status: TINT_ERR, result: "Malformed IF statement!" };
        }
        break;
      case "while":
        while (1) {
          if (sig.aborted) {
            throw new DOMException("Aborted", "AbortError");
          }
          t = await this.execute(c[1] ?? "", sig);
          if (t.status == TINT_ERR) {
            return t;
          }
          if (!istrue(t)) {
            break;
          }
          t = await this.execute(c[2] ?? "", sig);
          if (t.status == TINT_ERR) {
            return t;
          } else if (t.status == TINT_BREAK) {
            break;
          } else if (t.status == TINT_CONTINUE) {
            continue;
          } else if (t.status == TINT_RETURN) {
            return t;
          }
        }
        break;
      case "proc":
        this.procedures[c[1]] = { args: c[2].split(" "), body: c[3] };
        break;
      case "expr":
        t = c[1];
        for (let i = 2; i < c.length; i+=2) {
          let t2 = await this.run([c[i], t, c[i + 1]], sig);
          if (t2.status == TINT_ERR) {
            return t2;
          }
          t = t2.result ?? "";
        }
        res = t;break;
      default:
        if (this.procedures[cmd]) {
          this.scope_stack.push({ ...this.variables });
          this.variables = {};
          t = this.procedures[cmd].args ?? [];
          for (let i = 0; i < t.length; i++) {
            this.variables[t[i]] = c[i + 1];
          }
          t = await this.execute(this.procedures[cmd].body, sig);
          if (t.status == TINT_ERR) {
            return t;
          }
          res = t.result ?? "";
          //console.log("result", t.result);
          this.variables = { ...this.scope_stack.pop() };
        } else if (this.customs[cmd]) {
          let t = await this.customs[cmd](c.slice(1));
          res = t??"";
        } else {
          return { status: TINT_ERR, result: `Nonexistent command ${cmd}!` };
        }
    }
    return { status: TINT_OK, result: res };
  }
  /**
   * Executes a TINT script. FOR INTERNAL USE ONLY!
   * @param {String} S A script to execute.
   * @param {AbortSignal} sig
   * @returns {Promise<{result:String|null,status:Number}>}
   */
  async execute(S, sig) {
    console.log(S);
    let bufstack = [""];
    let symstack = [];
    let cmd = [];
    let res = "";
    let curly = 0;
    let temp;
    let output;
    let cmt=false
    const code = S + "\n";
    for (let i = 0; i < code.length; i++) {
      if (sig.aborted) {
        throw new DOMException("Aborted", "AbortError");
      }
      let c = code[i];
      if ((c == "[" || c == "(") && curly == 0) {
        symstack.push(c);
        bufstack.push("");
      } else if (c == "{") {
        symstack.push("{");
        bufstack.push("");
        curly++;
      } else if (c == "}") {
        if (symstack.length == 0) {
          return {
            status: TINT_ERR,
            result: "} without matching {",
          };
        }
        if (symstack.pop() != "{") {
          return {
            status: TINT_ERR,
            result: "} without matching {",
          };
        }
        temp = bufstack.pop();
        curly--;
        if (symstack.length == 0) {
          bufstack[bufstack.length - 1] += temp;
        } else {
          bufstack[bufstack.length - 1] += "{" + temp + "}";
        }
      } else if (c == "]" && curly == 0) {
        if (symstack.length == 0) {
          return {
            status: TINT_ERR,
            result: "] without matching [",
          };
        }
        if (symstack.pop() != "[") {
          return {
            status: TINT_ERR,
            result: "] without matching [",
          };
        }
        temp = bufstack.pop();
        if (temp !== undefined) {
          output = await this.execute(temp, sig);
          if (output.status != TINT_OK) {
            return output;
          }
          bufstack[bufstack.length - 1] += output.result;
        } else {
          console.error("wait this shouldn't happen");
          return {
            status: TINT_ERR,
            result: "wait this shouldn't happen",
          };
        }
      } else if (c == ")" && curly == 0) {
        if (symstack.length == 0) {
          return {
            status: TINT_ERR,
            result: ") without matching (",
          };
        }
        if (symstack.pop() != "(") {
          return {
            status: TINT_ERR,
            result: ") without matching (",
          };
        }
        temp = bufstack.pop();
        if (symstack.length == 0) {
          bufstack[bufstack.length - 1] += temp;
        } else {
          bufstack[bufstack.length - 1] += "(" + temp + ")";
        }
      } else if (symstack.length == 0 && c == " ") {
        if (cmd.length > 0 || bufstack[0].length > 0) {
          cmd.push(bufstack[0]);
          bufstack[0] = "";
        }
      } else if (symstack.length == 0 && (c == ";" || c == "\n")) {
        if (cmd.length > 0 || bufstack[0].length > 0) {
          cmd.push(bufstack[0]);
          bufstack[0] = "";
        }
        //console.log(cmd);
        if (cmd.length != 0) {
          output = await this.run(cmd, sig);
          //console.log(cmd,"->",output)
          if (output.status != TINT_OK) {
            return output;
          }
          if (output.result !== null) {
            if (output.status != TINT_OK) {
              return output;
            }
            res = output.result;
          }
        }
        cmd = [];
      } else {
        bufstack[bufstack.length - 1] += c;
      }
    }
    return { status: TINT_OK, result: res };
  }
}
