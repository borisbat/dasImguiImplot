# dasImguiImplot

[ImPlot](https://github.com/epezent/implot) bindings for the
[daslang](https://dascript.org/) programming language — an immediate-mode
plotting library for Dear ImGui, usable from daslang scripts.

Sibling project to [dasImguiNodeEditor](https://github.com/borisbat/dasImguiNodeEditor);
it depends on, but does not modify, dasImgui — which ships as part of the
[daslang](https://github.com/GaijinEntertainment/daScript) tree itself
(`modules/dasImgui`), so no separate dasImgui install is needed.

## Status

Early development. The native binding is in place (every enum, the core value
structs, ~150 functions, plus hand-written `Plot*` forwarders for float/double/int
data). The daslang-idiomatic wrapper tiers, headless tests, docs, and tutorials
are in progress.

## Versions

- **ImPlot v0.16** (vendored under `implot/`, patched for ImGui 1.90.6).
- **Dear ImGui 1.90.6-docking** — matches dasImgui's pinned version; ImPlot shares
  dasImgui's single ImGui context (no separate context to manage).

## Requirements

- daslang SDK (with dynamic-module support) — dasImgui is part of the daslang
  tree (`modules/dasImgui`), so building daslang provides it
- CMake 3.16+, a C++17 compiler (MSVC / GCC / Clang)

## Build

Via daspkg (dasImgui already ships with daslang; this builds just the overlay):

```
daspkg install github.com/borisbat/dasImguiImplot
```

Or configure the native module directly (the package must sit next to
`modules/dasImgui` in a daslang tree, with dasImgui already built):

```
cmake -S . -B _build -DDASLANG_DIR=<daslang-sdk-root>
cmake --build _build --config Release
```

This produces `dasModuleImplot.shared_module`. Load it (in-tree dasImgui
resolves natively — no extra `-load_module` for it):

```
daslang -load_module <path>/dasImguiImplot script.das
```

## License

MIT — see [LICENSE](LICENSE). Vendored ImPlot is MIT (see `implot/LICENSE`).
