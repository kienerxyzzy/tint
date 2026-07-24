colors = {
    "c0": "\033[31m",
    "c1": "\033[33m",
    "c2": "\033[32m",
    "c3": "\033[36m",
    "name": "\033[36m",
    "err": "\033[31m",
    "output": "\033[36m",
    "linja": "\033[30m\033[46m",
}
reset = "\033[0m"
tint = f"{colors["c0"]}T{colors["c1"]}I{colors["c2"]}N{colors["c3"]}T{reset}"
print(
    f"""{colors["c0"]}█████  {colors["c1"]}█████          {colors["c2"]}█   █  {colors["c3"]}█████
  {colors["c0"]}█      {colors["c1"]}█            {colors["c2"]}██  █    {colors["c3"]}█
  {colors["c0"]}█      {colors["c1"]}█            {colors["c2"]}█ █ █    {colors["c3"]}█
  {colors["c0"]}█      {colors["c1"]}█            {colors["c2"]}█  ██    {colors["c3"]}█
  {colors["c0"]}█{colors["c1"]}I{colors["c2"]}N{colors["c3"]}T {colors["c1"]}█████S (still) {colors["c2"]}█   █OT  {colors["c3"]}█CL
{tint} REPL, Version 2.0
Developed by {colors["name"]}KCN-037/Stonkalyasatone/N.P.Kien{reset}. in \033[41m\033[33m * {reset} Vietnam.
{tint} is a simplified variant of Tcl that allows it's interpreter to fit in under 200 lines of Python.
\033[1mDon't believe me? Count how many lines there are in main.py.{reset}
"""
)
import main as tint

I = tint.Instance()

while True:
    try:
        line = input(">>>")
        if line == ".load":
            try:
                with open(input("file:")) as f:
                    script = f.read()
            except Exception as e:
                print(f"{colors["err"]}Error opening file: {str(e)}{reset}")
                script = ""
            result = I.execute(script)
        elif line == ".secret":
            print("pennywort " * 36)  #:))))))
            result = ""
        else:
            result = I.execute(line)
        if result != "":
            print(f"{colors["linja"]}{result}{reset}")
    except SyntaxError as e:
        print(f"{colors["err"]}Syntax error: {str(e)}{reset}")
    except AssertionError as e:
            print(f"Internal error, pls report to dev: {str(e)}")
    except KeyboardInterrupt:
        print("\nbye")
        break
    except Exception as e:
        print(f"{colors["err"]}Error: {str(e)}{reset}")
    
