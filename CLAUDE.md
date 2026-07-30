# dasImguiImplot project instructions

dasImguiImplot is the daslang binding + boost-v2 wrapper layer for
[ImPlot](https://github.com/epezent/implot) (v0.16, vendored), an immediate-mode
plotting library for Dear ImGui. It is built **on top of
dasImgui** (part of the daslang tree, `modules/dasImgui`) and mirrors its conventions —
`[container]` macros, the snapshot/telemetry rail, the `imgui_harness` lifecycle,
dastest integration tests, and the `daslang-live` HTTP driver. **Read dasImgui's
`CLAUDE.md` first** for all of that shared machinery; this file documents only what is
implot-specific. It is a near-exact sibling of
[dasImguiNodeEditor](https://github.com/borisbat/dasImguiNodeEditor) — when something
here is underspecified, the node-editor's `CLAUDE.md` is the closest precedent.

Unlike the node editor, implot ships **no consumer lint** (ImPlot is stateless
immediate-mode — there are no queue/ownership invariants to protect, so raw
`implot::*` calls are fine) and **no live-command module** (ImPlot's live story is
data-feeding, deferred).

## Modules

Registered in `.das_module` via `register_native_path("imgui", "<name>", …)`. A NEW
daslib module MUST get its own line there, or `require imgui/<name>` fails with
`error[20605] … file not found`.

| Module | Require | Role |
|---|---|---|
| `imgui_implot_boost_v2` | `require imgui/imgui_implot_boost_v2` | **the v2 boost — what new code uses.** Snapshot `plot`/`subplots` scopes, OR-typed items, `Setup*`/`SetNext*` styling, drag tools, coord helpers. `shared`. |
| `imgui_implot_app` | `require imgui/imgui_implot_app` | `with_implot_app(feature){…}` test driver (implot mirror of dasImgui's `with_imgui_app`). `public`, NOT `shared`. |
| `imgui_implot_playwright` | `require imgui/imgui_implot_playwright` | ImPlot-aware test layer over `imgui_playwright` (`PlotSession` + `plot_*`/`drag_*` readers + `wait_for_*`). `public`, NOT `shared`. |
| `imgui_implot_boost` | `require imgui/imgui_implot_boost` | legacy v1 thin `with_plot`/`with_subplots` + near-1:1 item wrappers; kept for back-compat. |

The native module is `implot` (`require implot`) — `Module("implot")`,
`dasModuleImplot.shared_module`, `src/dasIMPLOT.*`.

## Dev workflow

- **Edit source under `D:\DASPKG\dasImguiImplot`.** Run/lint/test with both modules on
  the load path: `-load_module D:/DASPKG/dasImgui -load_module D:/DASPKG/dasImguiImplot`
  (MCP tools: `load_modules: ["D:/DASPKG/dasImgui", "D:/DASPKG/dasImguiImplot"]`). No
  junction or daspkg install needed for local iteration. (Junctions at
  `D:\Work\daScript\modules\{dasImgui,dasImguiImplot}` exist for the generator's
  `get_das_root()/modules/...` paths; the doc generator resolves its own root from a
  loaded module's `fileName`, so `-load_module` is enough there too.)
- **C++ build:** `cmake --build D:/DASPKG/dasImguiImplot/_build --config Release` (timeout
  0 — builds are slow; configure once with `-DDASLANG_DIR=D:/Work/daScript`). **dasImgui
  must be built first** (sibling under the same parent — the implot C++ links
  `dasModuleImgui` and uses dasImgui's imgui headers; the configure derives the dasImgui
  dir as `<repo-parent>/dasImgui`). **Shut down `daslang-live` before relinking** — it
  holds `dasModuleImplot.shared_module` open.
- **Pure-daslib edits** (the `daslib/*.das` wrappers, examples, tests) need NO C++
  rebuild — just rerun. Only `src/*.cpp` / `src/*.inc` / vendored `implot/*` changes need
  `cmake --build`. A main.cpp-only change (e.g. a new forwarder) is an incremental
  compile (no regen, no GLOB change).
- **Inspect via live/headless, not OS screen grabs.** `imgui_snapshot` (widget tree, incl.
  each plot's serialized state) and `screenshot` are ground truth.

## Regenerating the binding (only when the native surface changes)

`bind/bind_implot.das` is a `CppGenBind` subclass; run it with a local daslang that has
`dasClangBind` enabled (works on MSVC now — `find_package(Clang 22.1)` + the official
LLVM `libclang.dll`). Output is committed to `src/`. **Before every regen: delete the
stale func chunks** — `rm src/dasIMPLOT.func_*.cpp` then reconfigure. Fewer bound
functions → fewer `func_N.cpp`; CMake GLOBs `dasIMPLOT.func_*.cpp`, so a lingering
higher-numbered chunk from a prior run gets compiled and breaks the build.

Key binding facts (see the project memory / `bind_implot.das` for the full recipe):
- **Templated `Plot*` are skipped by libclang** → hand-written non-template forwarders in
  `src/dasIMPLOT.main.cpp`, macro-stamped float/double/int, registered in `initMain()`.
  `TArray<T>::data` is `char*` → cast `(const T*)`. Struct args (ImPlotPoint/Range/Rect)
  are flattened to scalar doubles in the forwarder.
- **`ImPlotPoint`/`ImPlotRange`/`ImPlotRect`/`ImPlotStyle` bound as managed structs**
  (`local_type_names`), NOT vector-aliased — daslang has no double-vector type.
- **The forwarders flatten item `flags` to bare `int`; the GENERATED bindings keep the
  real enum** (e.g. `DragPoint`'s `flags : ImPlotDragToolFlags`). So a v2 wrapper over a
  forwarder takes `flags : int`, but one over a generated native takes the enum type.
- **Single shared ImGui:** compile `implot.cpp`/`implot_items.cpp` with
  `IMGUI_API=__declspec(dllimport)`, link `dasModuleImgui.lib`, do NOT recompile
  `imgui.cpp`. `IMPLOT_CUSTOM_NUMERIC_TYPES=(float)(double)(ImS32)` trims instantiations.
- **v0.16→ImGui-1.90.6 patch** (the only one), in `implot.cpp` after the imgui includes:
  `#ifndef IM_OFFSETOF → offsetof`, `#ifndef IM_FLOOR → IM_TRUNC` (both retired behind
  `IMGUI_DISABLE_OBSOLETE_FUNCTIONS`, which we keep for ABI match). Also set
  `IMPLOT_DISABLE_OBSOLETE_FUNCTIONS` in both the generator clang args and CMake defs.

## boost-v2 API (the surface to use)

A chart is a `plot` scope. `plot`/`subplots` are `[container]` macros whose FIRST param is
a `var state : PlotScopeState` (a persistent global the caller owns); the macro injects
`widget_ident`, brackets `BeginPlot`/`EndPlot`, runs the body only when visible, and
serializes the plot's per-frame state into the snapshot under the container path.

```
plot(WAVES, (title = "waves", size = float2(-1.0f, 480.0f), flags = ImPlotFlags.None)) {
    setup_axes("sample", "value")
    setup_axes_limits(0.0lf, 200.0lf, -1.5lf, 1.5lf)
    next_line_style(float4(0.3f, 0.7f, 1.0f, 1.0f), 2.0f)
    plot_line("sin", g_sin)                 // OR-typed: array<float>|array<double>|array<int>
    next_marker_style(ImPlotMarker.Circle, 4.0f)
    plot_scatter("samples", g_xs, g_ys)     // paired xs/ys overload: array<auto(T)>; array<T>
}
```

- **Snapshot payload** (keyed `<window>/<plot>`): `pos`/`plot_size` (screen px),
  `x_min..y_max` (data coords), `hovered`, `mouse_x`/`mouse_y` (data coords), `visible`.
  **Captured EAGERLY in-scope between BeginPlot/EndPlot** — ImPlot's query funcs
  (`GetPlotPos`/`GetPlotLimits`/`GetPlotMousePos`/`IsPlotHovered`) are ONLY valid there
  (unlike the node-editor's lazy serialize-at-snapshot hook on a persistent editor).
  `mouse_*` is guarded on `IsMousePosValid(null)` — off-window / headless it reads the
  ±FLT_MAX sentinel.
- **Items** (`plot_line`/`scatter`/`stairs`/`bars`/`stems`/`shaded`/`shaded_between`/
  `inf_lines`/`text`/`dummy`/`error_bars`/`digital`/`heatmap`/`histogram`/`histogram2d`)
  are single OR-typed wrappers (`float|double|int`) over the type-overloaded forwarders,
  with paired `xs`/`ys` overloads tying both arrays to one element type.
- **Styling:** `setup_axes`/`setup_axis`/`setup_axes_limits`/`setup_axis_limits`/
  `setup_legend` (configure before items); `next_line_style`/`next_fill_style`/
  `next_marker_style`/`next_axes_limits`/`next_axes_to_fit` (style the NEXT item;
  auto-sentinel defaults mirror ImPlot's "auto").
- **Drag tools** (`drag_point`/`drag_line_x`/`drag_line_y`/`drag_rect`): interactive
  handles INSIDE a plot scope. Each owns a persistent state struct (`DragPointState{x,y,
  held}` / `DragLineState{value,held}` / `DragRectState{x_min..y_max,held}`) the caller
  passes; `addr` of its fields feeds the native's `double*` out-params (struct-field-via-
  reference needs `unsafe(addr(...))` wrapped at the addr — the outer call's unsafe does
  NOT cover it). They register as a LEAF under `<plot>/<id>` via **pushed-path
  container_finalize** (`widget_prelude` PushID → `container_path_push` → the shared
  `finalize_state` → `container_path_pop`), with the bbox computed from the handle's DATA
  position via `PlotToPixels` — NOT `widget_finalize`, which re-captures bbox from
  `GetItemRect` (a drag tool submits no normal ImGui item, so that bbox is stale). The
  computed bbox is what a test synth-drags onto. ImPlot moves the bound value only on
  `held && IsMouseDragging(0)`.
- **Coords:** `plot_to_pixels`/`pixels_to_plot` (valid in-scope).

## Tests + CI

`tests/integration/*.das` via `dastest` + `with_implot_app`. Run **headless** (spawned
daslang-live subprocesses else pop real windows and flake). Mixed dir: dastest runs both
`[test]` files and in-process `def main : int` smokes (exit-0 = PASS) side by side.

```
daslang -load_module D:/DASPKG/dasImguiImplot \
  D:/Work/daScript/dastest/dastest.das -- --test modules/dasImguiImplot/tests/integration \
  --timeout 600 --isolated-mode --isolated-mode-threads 4 --headless
```

CI: `.github/workflows/tests.yml` (ubuntu/macos; Windows deferred — builds + passes
locally under MSVC, opportunistic re-enable) + `docs.yml` (lint changed `.das` →
`utils/implot2rst.das` → stub/Uncategorized gates → `sphinx-build -W` → Pages on master).
Both workflows `daspkg install ../dasImguiImplot` only — dasImgui is in-tree
(`modules/dasImgui`, built by the daslang superbuild).

**Test helpers (`imgui_implot_playwright`)** — `implot_open(app, plot_path)` returns a
`PlotSession {app, plot}` (just the pair — ImPlot is stateless, no handle); readers pull
the serialized state (`plot_axis_limits`/`plot_hovered`/`plot_mouse_pos`/`plot_bbox`/
`plot_center`, and `drag_*_value`/`drag_held` keyed by `handle_path(s, id)`); the
`wait_for_*` polls gate an assertion on a state change landing (`wait_for_axis_limits`,
`wait_for_hovered`, `wait_for_point_moved`). The module is `public` (not `shared`) — it
requires the non-shared `imgui_playwright`, and a `shared` module can't require a
non-shared one (error 20115).

## Docs

`utils/implot2rst.das` (run from the daspkg-installed module dir, or via `-load_module`)
emits one `doc/source/stdlib/generated/<module>.rst` per documented module (boost_v2 /
app / playwright; v1 boost excluded). **Every `def public` must match a `group_by_regex`
bucket** or the Uncategorized gate fails. Handmade intros under
`doc/source/stdlib/handmade/` are inlined into each generated page (must exist before the
run, no `// stub`). `external_types.rst` anchors the refs the generated pages emit for
non-documented modules (the `implot` enums + `imgui_playwright::ImguiApp`); documented-
module structs self-anchor, daslang-core types resolve via intersphinx. Validate locally
with `sphinx-build -W` before pushing. `generated/` + `doc/build/` are gitignored.

## Gotchas

1. **Name collisions with dasImgui's required-public modules.** v2 requires
   `imgui/imgui_boost_runtime` + `imgui/imgui_boost_v2` public, so their `PlotState`
   (ImGui PlotLines widget state) and the `plot_histogram`/`plot_lines` widget call-macros
   are in scope. My plot state is `PlotScopeState` (not `PlotState`); ImPlot's statistical
   histogram is `histogram`/`histogram2d` (not `plot_histogram*` — the widget call-macro
   intercepts that name and rejects the positional-string form, `error[50503]`).
   `plot_line` singular is fine (ImGui's is `plot_lines`).
2. **`label` is a reserved word** (labeled blocks). Axis-label params are `axis_label`.
3. **`CreateContext` is ambiguous** (imgui + implot both export it) → qualify
   `implot::CreateContext()`; `DestroyContext(ptr)` disambiguates by arg type. Create the
   ImPlot context once after the ImGui context (init), destroy at shutdown.
4. **A block-taking wrapper can't have default args between the last explicit arg and the
   block** — daslang binds the trailing block to the param right after the explicit args,
   so a default slot there swallows the block. Use arity overloads (v1 `with_plot`) or a
   `[container]` macro (v2 `plot`, where defaults work).
5. **Drag-tool grab rects must not overlap.** A press on a point sitting on another tool's
   edge handle (e.g. a point at `y=0.5` on a rect whose `y_max=0.5`) lets the other tool
   steal the active-id, so the wrong value moves. Space handles apart. (This is real-input
   behavior, not a synth artifact — synthetic input drives ImPlot's `DragPoint` exactly
   like a real mouse.)
6. **`harness_new_frame` runs `imgui_synth_tick`** — the synth-IO drain. A hand-rolled
   `live_*` render loop that skips it silently no-ops all synthetic input. Examples use the
   harness (`harness_init`/`begin_frame`/`new_frame`/`end_frame`/`shutdown`), so they run
   standalone (windowed), headless (`--headless --headless-frames N`), and live identically.
7. **`is`/`as` on ImPlot enums use dot access** (`ImPlotFlags.None`), and the daslang doc
   domain labels them `enum-implot-<Name>` — anchor any new one referenced in a signature.
