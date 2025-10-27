



# ✅ Set your target directory
import os
import jupytext

# ✅ Set your target directory
target_dir = "./"  # or absolute path like "/Users/jay_m4/Downloads/wallstreet"

for filename in os.listdir(target_dir):
    if filename.endswith(".py"):
        py_path = os.path.join(target_dir, filename)
        ipynb_path = py_path.replace(".py", ".ipynb")

        print(f"Converting: {filename} → {os.path.basename(ipynb_path)}")

        # 🧠 Load .py file as notebook
        nb = jupytext.read(py_path)

        # 💾 Write notebook file
        jupytext.write(nb, ipynb_path)

print("✅ All .py files converted to .ipynb")
