# zip-split-bypass

Bypass fake split-volume ZIPs and recover files from ZIPs that falsely present as multi-part archives.

Some ZIP files are crafted in a way that tricks common unzip tools (like Windows Explorer, WinRAR, 7-Zip, and Python's zipfile module) into thinking the archive is part of a split volume set. These ZIPs worked fine in its intended environment, but refuse to extract normally, reporting errors like:

> "You need to have the following volume to continue extraction: [FILENAME].z01"

This repository provides **working solutions** to recover the actual contents of such ZIP files.

---

## 🔍 Motivation

This project originated from an investigation into a ZIP file that appeared broken to every standard extraction tool, yet functioned perfectly within its intended application (such as a Minecraft datapack). Closer inspection revealed the file was not truly split, but a fake split archive — a fully valid ZIP file containing all necessary data, deliberately crafted to resemble part of a multi-volume archive. This manipulation effectively misleads unzip utilities into thinking additional parts are missing, causing extraction to fail and confusing users.

I developed this tool to help users recover files from such misleading ZIPs **without needing to understand ZIP internals or use complex command-line tools**.

---

## 📚 Background

ZIP files store an index of their contents — known as the **central directory** — at the end of the archive. Most extraction tools (including Windows Explorer, 7-Zip, WinRAR, and Python's `zipfile` module) rely on this directory to locate and extract file data. In **multi-volume ZIP archives**, this directory is expected to appear only in the **final volume** (typically with the `.zip` extension), while earlier segments are named `.z01`, `.z02`, and so on.

Some ZIP files exploit this behavior by **intentionally placing the central directory at a nonstandard offset**, causing tools to **misidentify them as incomplete split archives**. As a result, these tools refuse to open the file and demand missing volumes — even though the file is complete and valid. This technique is sometimes used to:

* Bypass automated extraction tools
* "Obfuscate" the archive contents
* Prevent casual inspection or tampering
* Trigger false "corrupt archive" errors in common software

Despite this, the archive remains structurally valid — the contents are intact, just **mislabeled or offset** to fool extraction tools.

Fortunately, **Java’s `jar` tool does not perform volume validation** and instead reads directly from the central directory, regardless of its offset.

---

## ✅ Recommended Method — Java’s `jar xf`

The most reliable and simplest solution is to use Java’s `jar` tool.

### 🛠 Steps (Manual)

```sh
jar xf [FILENAME].zip
````

* Works even if other tools report errors
* Preserves file and folder names
* No special setup beyond Java

---

## 🖱️ One-Click Method for Non-Technical Users

Use `quick_extract.py` — a zero-config script that prompts for your ZIP and extracts it automatically using the Java method.

### 📦 `quick_extract.py`

* Prompts you to select the fake ZIP file
* Extracts using Java’s `jar xf`
* Outputs files into a folder named after the ZIP

> Example: `Downloads/fake.zip` will be extracted to `Downloads/fake/`.

#### ▶️ To run:

1. Make sure you have **Java installed**.
2. Install Python 3 if you don’t have it.
3. Double-click `quick_extract.py` or run it with:

```sh
python quick_extract.py
```

> ✅ Works on Windows, macOS, and Linux.

---

## 📂 Repository Structure

```
zip-split-bypass/
├── quick_extract.py             # User-friendly Java-based extractor
└── README.md
```

---

## 🧪 Compatibility

Tested with:

* Windows 10/11
* macOS
* Linux
* Python 3.8+
* Java 8+ (JDK or JRE)

---

## 🙏 Acknowledgments

This project originated from a reverse-engineering effort of a ZIP file that evaded traditional extraction, appearing corrupt or incomplete due to intentionally manipulated headers. Special thanks to:

* The Minecraft datapack community, for surfacing creative use cases
* The authors of Python’s `zipfile` module and Java’s `jar` utility
* The creators of ZIP specs and unzip tools, whose limitations led to this creative workaround

---

## 📜 License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for full text.

---

Happy extracting!
