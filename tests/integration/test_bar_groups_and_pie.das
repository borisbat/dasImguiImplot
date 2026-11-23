options gen2
options _comment_hygiene = true
options indenting = 4
options no_unused_block_arguments = false
options no_unused_function_arguments = false

require dastest/testing_boost public
require imgui/imgui_implot_app public
require imgui/imgui_implot_playwright public
require daslib/json public
require daslib/json_boost public

//! Headless regression for bar_groups_and_pie: spawn the tutorial and assert both the
//! BARS plot (plot_bar_groups, a labelled-series matrix) and the PIE plot (plot_pie_chart)
//! register and draw. The bar plot pins fixed axis limits (ImPlotCond.Always), so its
//! limits converging proves the categorical item actually submitted inside a real scope —
//! the string-array (array<string> -> const char* const[]) path end to end.

let SUBJECT = "modules/dasImguiImplot/examples/tutorial/bar_groups_and_pie.das"

[test]
def test_bar_groups_and_pie(t : T?) {
    with_implot_app(SUBJECT) $(d) {
        let bars = implot_open(d, "PLOT_WIN/BARS")
        var bsnap = implot_wait_visible(bars, 15.0f)
        t |> success(bsnap != null && plot_visible(bsnap, bars),
                     "BARS plot (plot_bar_groups) rendered")
        // Limits pinned with ImPlotCond.Always in the tutorial — converging proves the
        // labelled-series item submitted (the scope ran past plot_bar_groups, not before).
        var lsnap = wait_for_axis_limits(bars, -0.5lf, 4.0lf - 0.5lf, 0.0lf, 18.0lf)
        t |> success(lsnap != null, "BARS axis limits converged to the pinned range")

        let pie = implot_open(d, "PLOT_WIN/PIE")
        var psnap = implot_wait_visible(pie, 6.0f)
        t |> success(psnap != null && plot_visible(psnap, pie),
                     "PIE plot (plot_pie_chart) rendered")
    }
}
