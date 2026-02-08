# Save as: orchastrator.py
import os
import sys
import argparse
import subprocess
import shutil
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

# --- 1. SETUP THE BRAIN ---
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("❌ Critical Error: GOOGLE_API_KEY is missing!")
    sys.exit(1)

# We use 1.5-Flash because it is fast and has high rate limits (15 RPM)
print("🧠 Initializing Brain: gemini-2.5-flash...")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0, 
    google_api_key=api_key
)

TARGET_DIR = "" 

# --- 2. UTILS ---
def get_python_files(directory):
    py_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and "venv" not in root:
                py_files.append(os.path.join(root, file))
    return py_files

def run_cmd(cmd_list, desc):
    print(f"\n⚙️  Running Tool: {desc}...")
    try:
        # We assume tools are in the path or installed in the env
        subprocess.run(
            cmd_list,
            cwd=TARGET_DIR,
            check=True,
            shell=True,
            capture_output=True,
            text=True
        )
        print(f"   ✅ Tool Success")
        return True
    except subprocess.CalledProcessError:
        print(f"   ⚠️  Tool Failed (Will attempt AI Fallback if available)")
        return False

# --- 3. THE PHASES ---

def phase_1_syntax():
    print("\n🔹 [Phase 1] Syntax Modernization (Python 2 -> 3)")
    
    # Step A: The Tool (2to3)
    run_cmd(["2to3", "-w", "-n", "."], "2to3 Automatic Fixer")
    
    # Step B: The AI Cleanup (Hybrid Loop)
    print("   🕵️  Scanning for stubborn Python 2 code...")
    files = get_python_files(TARGET_DIR)
    
    for file_path in files:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        # Heuristic: Check for Python 2 print style (print "text")
        if 'print "' in content or "print '" in content:
            filename = os.path.basename(file_path)
            print(f"   🧠 AI Detected Python 2 syntax in: {filename}")
            print(f"      ↳ rewriting file...")
            
            prompt = ChatPromptTemplate.from_template(
                """Fix Python 2 syntax to Python 3. 
                Focus on: print(), exception handling, and imports.
                Return ONLY the code.
                CODE: {code}"""
            )
            try:
                new_code = (prompt | llm | StrOutputParser()).invoke({"code": content})
                new_code = new_code.replace("```python", "").replace("```", "").strip()
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_code)
                print(f"      ✅ Fixed: {filename}")
                time.sleep(1) # Rate Limit Safety
            except Exception as e:
                print(f"      ❌ Failed to fix {filename}: {e}")

def phase_2_format():
    print("\n🔹 [Phase 2] Code Formatting")
    run_cmd(["black", "."], "Black Formatter")

def phase_3_dependencies():
    print("\n🔹 [Phase 3] Dependency Resolution")
    req_path = os.path.join(TARGET_DIR, "requirements.txt")
    
    # Step A: Tool
    if run_cmd(["pipreqs", ".", "--force", "--encoding=utf-8"], "pipreqs"):
        return

    # Step B: AI Fallback
    print("   🦅 Engaging AI Dependency Scanner...")
    all_imports = set()
    for file_path in get_python_files(TARGET_DIR):
        try:
            with open(file_path, "r", errors="ignore") as f:
                for line in f:
                    if line.strip().startswith(("import ", "from ")):
                        all_imports.add(line.strip())
        except: pass
    
    if all_imports:
        print(f"   🧠 Analyzing {len(all_imports)} imports...")
        prompt = ChatPromptTemplate.from_template(
            "Convert these imports to a requirements.txt list. Ignore stdlib. Return ONLY content.\n{imports}"
        )
        try:
            reqs = (prompt | llm | StrOutputParser()).invoke({"imports": "\n".join(all_imports)})
            with open(req_path, "w", encoding="utf-8") as f:
                f.write(reqs.replace("```","").strip())
            print("   ✅ AI generated requirements.txt")
        except:
            print("   ❌ AI failed to generate requirements.")

def phase_4_documentation():
    print("\n🔹 [Phase 4] Auto-Documentation")
    files = get_python_files(TARGET_DIR)
    
    for file_path in files:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()
            
        if '"""' not in code[:100]:
            filename = os.path.basename(file_path)
            print(f"   📝 Generating Docstring for: {filename}...")
            try:
                prompt = ChatPromptTemplate.from_template(
                    "Write a one-line summary docstring for this code. Return ONLY the string.\nCODE: {code}"
                )
                doc = (prompt | llm | StrOutputParser()).invoke({"code": code[:1000]})
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f'"""{doc.strip()}"""\n' + code)
                time.sleep(1)
            except Exception as e:
                print(f"      ⚠️ Skipped {filename}: {e}")

def phase_5_readme():
    print("\n🔹 [Phase 5] README Generation")
    # Quick check to see what files exist
    files = [os.path.basename(f) for f in get_python_files(TARGET_DIR)]
    structure = "\n".join(files[:20])
    
    print(f"   🧠 analyzing project structure...")
    prompt = ChatPromptTemplate.from_template(
        """Create a README.md for a project with these files:
        {structure}
        Include: Title, Overview, Usage. Return ONLY Markdown."""
    )
    try:
        readme = (prompt | llm | StrOutputParser()).invoke({"structure": structure})
        with open(os.path.join(TARGET_DIR, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme.replace("```markdown","").replace("```","").strip())
        print("   ✅ README.md created.")
    except:
        print("   ❌ README failed.")

def phase_6_doctor_loop():
    print("\n🔹 [Phase 6] The Doctor (Logic Repair Loop)")
    files = get_python_files(TARGET_DIR)
    
    for file_path in files:
        filename = os.path.basename(file_path)
        print(f"   🩺 Checkup: {filename}...")
        
        # 1. Try to Compile/Run
        try:
            # We use py_compile first to check for syntax errors that 2to3 missed
            subprocess.run([sys.executable, "-m", "py_compile", file_path], check=True, capture_output=True)
            print(f"      ✅ Syntax Valid.")
        except subprocess.CalledProcessError as e:
            # 2. If it fails, AI Fix
            print(f"      🔥 CRASH DETECTED! Asking Doctor to fix...")
            error_msg = e.stderr.decode()
            
            with open(file_path, "r", encoding="utf-8") as f:
                broken_code = f.read()
                
            prompt = ChatPromptTemplate.from_template(
                """Act as a Python Debugger. Fix the error in this code.
                ERROR: {error}
                CODE: {code}
                Return ONLY the fixed code."""
            )
            try:
                fixed_code = (prompt | llm | StrOutputParser()).invoke({
                    "error": error_msg, "code": broken_code
                })
                clean_code = fixed_code.replace("```python", "").replace("```", "").strip()
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(clean_code)
                print(f"      ✨ Doctor cured the file.")
                time.sleep(1)
            except:
                print(f"      ☠️ Doctor failed to save patient.")

# --- MAIN ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", help="Target folder path")
    args = parser.parse_args()
    
    TARGET_DIR = os.path.abspath(args.folder)
    if not os.path.exists(TARGET_DIR):
        print("❌ Folder not found!")
        sys.exit(1)

    print(f"🔌 Connected to: {TARGET_DIR}")
    
    phase_1_syntax()
    phase_2_format()
    phase_3_dependencies()
    phase_4_documentation()
    phase_5_readme()
    phase_6_doctor_loop()
    
    print("\n🏆 Repository Evolution Complete and cleaned BOSS")