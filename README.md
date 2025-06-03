# zip-split-bypass

A toolkit for recovering single-file ZIPs that have been deliberately flagged as “split” volumes. Provides three methods—Java’s `jar xf`, Info-ZIP’s `unzip -FF`, and a Python rebuild script—to bypass bogus split-volume markers. Includes a minimal sample “fake-split” archive for demonstration.

---

## 🚀 Quickstart

1. **Clone this repository**  
   ```bash
   git clone https://github.com/your-username/zip-split-bypass.git
   cd zip-split-bypass
````

2. **Generate a “fake-split” sample archive**
   A helper script creates **`examples/fake_archive.zip`**, containing a single file (`data/sample.txt`) but with local headers marked split-spanning. Run:

   ```bash
   python3 scripts/generate_fake_zip.py
   ```

   You’ll see:

   ```
   examples/fake_archive.zip
   ```

   Inside is `data/sample.txt`, but 7-Zip or WinRAR will complain “Need fake\_archive.z01.”

3. **Choose your extraction method**:

   * **Java’s `jar xf`**

     ```bash
     cd examples
     jar xf fake_archive.zip
     ```

     Extracts directly from the central directory. The file appears as:

     ```
     examples/data/sample.txt
     ```

   * **Info-ZIP’s `unzip -FF`**

     ```bash
     cd examples
     unzip -FF fake_archive.zip -d extracted_sample
     ```

     The `-FF` flag rebuilds a valid central directory. The file appears as:

     ```
     examples/extracted_sample/data/sample.txt
     ```

   * **Python script → `scripts/rebuild_truezip.py`**

     ```bash
     python3 scripts/rebuild_truezip.py examples/fake_archive.zip final_rebuilt.zip
     unzip final_rebuilt.zip -d extracted_sample_py
     ```

     The script scans for valid local-file headers, decompresses entries, and writes a new ZIP (`final_rebuilt.zip`). The file appears as:

     ```
     examples/extracted_sample_py/data/sample.txt
     ```

---

## 📂 Repository Structure

```
zip-split-bypass/
├── .gitignore
├── LICENSE
├── README.md                  ← this file
├── scripts/
│   ├── generate_fake_zip.py   ← creates a toy “fake-split” ZIP
│   └── rebuild_truezip.py     ← Python script to rebuild a valid ZIP
├── examples/
│   ├── fake_archive.zip       ← generated “fake-split” sample ZIP
│   ├── final_rebuilt.zip      ← output from running rebuild_truezip.py
│   ├── extracted_sample/      ← result of `jar xf fake_archive.zip`
│   └── extracted_sample_py/   ← result of `unzip final_rebuilt.zip -d …`
└── docs/
    └── walkthrough.md         ← (optional) deeper explanation and screenshots
```

* **`.gitignore`**

  ```
  __pycache__/
  *.pyc
  *.zip
  *.log
  ```
* **`LICENSE`**

  * MIT License text.
* **`scripts/generate_fake_zip.py`**

  * Generates `examples/fake_archive.zip` with a single file (`data/sample.txt`) whose local-file headers are flagged as split-spanning.
* **`scripts/rebuild_truezip.py`**

  * Parses valid local-file headers (PK\x03\x04), decompresses each entry, and writes a fresh ZIP (`final_rebuilt.zip`) with all paths intact.
* **`examples/`**

  * Contains the generated fake-split ZIP and the extracted outputs for each method.
* **`docs/walkthrough.md`** (optional)

  * Detailed narrative on ZIP internals, split-volume flags, and step-by-step screenshots.

---

## 📜 Background & Motivation

ZIP archives consist of two key structures:

1. **Local-file headers**: Stored immediately before each file’s data. Many GUI extractors read these first.
2. **Central directory**: Located at the end of the archive; lists every file’s true path, CRC, sizes, and offset.

A “fake-split” ZIP deliberately sets the “split-spanning” bit in local-file headers (or uses uppercase paths) so that extractors (7-Zip, WinRAR, Windows Explorer) report:

```
Need volume “fake_archive.z01” to continue
```

or produce CRC errors. In reality, all data resides in the single `.zip` file; only the headers are mangled. The central directory remains correct.

This repository demonstrates three ways to ignore those bogus markers and recover the full contents of any such ZIP, using a minimal sample archive.

---

## 🛠️ Methods Overview

### 1. Java’s built-in `jar xf`

* **Description:** Uses Java’s archive tool to extract directly from the central directory, ignoring invalid local headers.
* **Pros:**

  * Preinstalled with most Java runtimes.
  * Zero-code solution; extracts immediately to disk.
* **Cons:**

  * Requires Java on your system.
  * Doesn’t produce a new ZIP file; files are extracted directly.

**Usage:**

```bash
cd examples
jar xf fake_archive.zip
ls data/sample.txt
```

---

### 2. Info-ZIP’s `unzip -FF`

* **Description:** Command-line `unzip` with “fix broken archives” mode.
* **Pros:**

  * Included by default on Linux/macOS.
  * Available on Windows via WSL, Git Bash, Cygwin, or GnuWin32.
  * No Java dependency.
* **Cons:**

  * Must install Info-ZIP’s `unzip` on Windows if not already available.

**Usage:**

```bash
cd examples
unzip -FF fake_archive.zip -d extracted_sample
ls extracted_sample/data/sample.txt
```

---

### 3. Python Script: `scripts/rebuild_truezip.py`

* **Description:** Scans for every valid local-file header (`PK\x03\x04`), decompresses each entry, and writes a fresh, valid ZIP (`final_rebuilt.zip`) preserving all paths.
* **Pros:**

  * Pure-Python; no external dependencies beyond Python 3.
  * Works even if both local headers and central directory are partially corrupted.
* **Cons:**

  * Creates an intermediate ZIP file rather than extracting directly.

**Usage:**

```bash
python3 scripts/rebuild_truezip.py examples/fake_archive.zip final_rebuilt.zip
unzip final_rebuilt.zip -d extracted_sample_py
ls extracted_sample_py/data/sample.txt
```

---

## 📄 Scripts Overview

#### `scripts/generate_fake_zip.py`

```python
#!/usr/bin/env python3
"""
generate_fake_zip.py

Creates a minimal “fake-split” ZIP at examples/fake_archive.zip containing:
  - data/sample.txt with sample text
  - Local-file headers flagged as split-spanning (general-purpose bit 0x0008)

USAGE:
    python3 scripts/generate_fake_zip.py
"""

import os
import struct
from zipfile import ZipFile, ZIP_DEFLATED

OUTPUT_PATH = "examples/fake_archive.zip"
TEMP_ZIP = "examples/_temp.zip"

# Step 1: Create a normal ZIP with a single file
if os.path.exists(TEMP_ZIP):
    os.remove(TEMP_ZIP)
with ZipFile(TEMP_ZIP, "w", compression=ZIP_DEFLATED) as zf:
    zf.writestr("data/sample.txt", "This is a test in a fake-split ZIP.\n")

# Step 2: Read that ZIP’s bytes, then rewrite local headers to set split flag
with open(TEMP_ZIP, "rb") as f:
    data = bytearray(f.read())

i = 0
while True:
    sig_pos = data.find(b"PK\x03\x04", i)
    if sig_pos < 0 or sig_pos + 8 > len(data):
        break
    # General-purpose flag at offset sig_pos+6 (2 bytes)
    gp_offset = sig_pos + 6
    orig_flags = struct.unpack_from("<H", data, gp_offset)[0]
    new_flags = orig_flags | 0x0008  # set split-spanning bit
    struct.pack_into("<H", data, gp_offset, new_flags)
    i = sig_pos + 30

# Step 3: Save as fake_archive.zip
with open(OUTPUT_PATH, "wb") as f:
    f.write(data)
os.remove(TEMP_ZIP)
print(f"✅ Generated fake-split ZIP: '{OUTPUT_PATH}'.")
```

#### `scripts/rebuild_truezip.py`

```python
#!/usr/bin/env python3
"""
rebuild_truezip.py

Reads a “fake-split” or corrupted ZIP, locates every valid PK\x03\x04 local-file header,
decompresses each entry, and writes a brand-new, valid ZIP.

USAGE:
    python3 rebuild_truezip.py <input_fake_zip> <output_fixed_zip>

Example:
    python3 scripts/rebuild_truezip.py examples/fake_archive.zip final_rebuilt.zip
"""

import struct
import zlib
import os
import sys
from zipfile import ZipFile, ZIP_DEFLATED

def rebuild(zip_in_path, zip_out_path):
    if os.path.exists(zip_out_path):
        os.remove(zip_out_path)

    with open(zip_in_path, "rb") as f:
        data = f.read()

    entries = []
    offset = 0
    data_len = len(data)

    while True:
        pos = data.find(b"PK\x03\x04", offset)
        if pos < 0 or pos + 30 > data_len:
            break

        (
            _sig,
            ver_needed,
            gp_flag,
            compression,
            mod_time,
            mod_date,
            crc32_lo,
            comp_size,
            uncomp_size,
            name_len,
            extra_len
        ) = struct.unpack_from("<4sHHHHHIIIHH", data, pos)

        header_end = pos + 30
        name_start = header_end
        name_end = name_start + name_len
        extra_end = name_end + extra_len
        data_start = extra_end
        data_end = data_start + comp_size

        if data_end > data_len:
            break

        filename = data[name_start:name_end].decode("utf-8", errors="ignore")
        comp_data = data[data_start:data_end]

        entries.append({
            "filename": filename,
            "compression": compression,
            "comp_data": comp_data
        })

        offset = data_end

    if not entries:
        print("❌ No valid local-file entries found. Exiting.")
        sys.exit(1)

    with ZipFile(zip_out_path, "w", compression=ZIP_DEFLATED) as newzip:
        for entry in entries:
            fn = entry["filename"]
            comp_data = entry["comp_data"]
            comp_method = entry["compression"]

            if comp_method == 8:
                try:
                    uncompressed = zlib.decompress(comp_data, -15)
                except Exception as e:
                    print(f"⚠️ Failed to decompress {fn}: {e}. Skipping.")
                    continue
            elif comp_method == 0:
                uncompressed = comp_data
            else:
                print(f"⚠️ Unsupported compression ({comp_method}) for {fn}. Skipping.")
                continue

            newzip.writestr(fn, uncompressed)

    print(f"✅ Rebuilt valid ZIP: '{zip_out_path}'.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 rebuild_truezip.py <input_fake_zip> <output_fixed_zip>")
        sys.exit(1)

    _, input_zip, output_zip = sys.argv
    rebuild(input_zip, output_zip)
```

---

## 🔍 Example Walkthrough

1. **Generate the sample fake-split ZIP**

   ```bash
   python3 scripts/generate_fake_zip.py
   ```

   Produces `examples/fake_archive.zip` containing `data/sample.txt` with split-spanning headers.

2. **Try extracting with 7-Zip (FAIL)**

   ```bash
   7z x examples/fake_archive.zip
   # → “Need fake_archive.z01” or CRC error
   ```

3. **Method A – Java `jar xf` (SUCCESS)**

   ```bash
   jar xf examples/fake_archive.zip
   ls data/sample.txt
   ```

   Output:

   ```
   examples/data/sample.txt
   ```

4. **Method B – Info-ZIP `unzip -FF` (SUCCESS)**

   ```bash
   unzip -FF examples/fake_archive.zip -d examples/extracted_sample
   ls examples/extracted_sample/data/sample.txt
   ```

   Output:

   ```
   examples/extracted_sample/data/sample.txt
   ```

5. **Method C – Python script (SUCCESS)**

   ```bash
   python3 scripts/rebuild_truezip.py examples/fake_archive.zip final_rebuilt.zip
   unzip final_rebuilt.zip -d examples/extracted_sample_py
   ls examples/extracted_sample_py/data/sample.txt
   ```

   Output:

   ```
   examples/extracted_sample_py/data/sample.txt
   ```

All three methods correctly recover `data/sample.txt`.

---

## 📜 License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for full text.

---

## 🙏 Acknowledgments

* Info-ZIP team (for `unzip -FF`).
* Java maintainers (for the `jar` utility).
* Python’s `zipfile` module (for script-based rebuilding).
* The concept of a “fake-split” Minecraft datapack inspired this minimal sample.

---

## 📞 Contact / Feedback

If you encounter issues, have suggestions, or want to contribute improvements, please open an issue or pull request on GitHub. Contributions welcome for:

* Additional sample archives (beyond `data/sample.txt`).
* Scripts in other languages replicating the same functionality.
* Windows-specific batch/PowerShell wrappers for `jar xf` or `unzip -FF`.
* Enhanced documentation or translations.

Happy extracting!

```
```
