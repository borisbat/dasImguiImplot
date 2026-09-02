#pragma once

#include "implot_stub.h"

namespace das {

// ImPlot's value structs (ImPlotPoint, ImPlotRange, ImPlotRect, ImPlotStyle,
// ImPlotInputMap) are double-based and bound as managed structs by the generator —
// daslang has no double-vector type to alias to, so there is no typeFactory here.
// ImVec2/ImVec4 aliasing (float2/float4) comes from cb_dasIMGUI.h, included ahead of
// this header by the generated dasIMPLOT.h.

// Per-function fixup applied during makeExtern of every generated binding: strip the
// ref off const ImVec2&/ImVec4& args so daslang passes them by value, and flag string
// args for the const char* cast. Mirrors dasImguiNodeEditor's imgui_node_editorTempFn.
struct implotTempFn {
    implotTempFn() = default;
    ___noinline bool operator()( Function * fn ) {
        if ( tempArgs || implicitArgs ) {
            for ( auto &arg : fn->arguments ) {
                if ( arg->type->isTempType() ) {
                    arg->type->temporary = tempArgs;
                    arg->type->implicit = implicitArgs;
                    arg->type->explicitConst = explicitConstArgs;
                }
            }
        }
        if ( tempResult ) {
            if ( fn->result->isTempType() ) {
                fn->result->temporary = true;
            }
        }
        for ( auto &arg : fn->arguments ) {
            if ( arg->type->constant && arg->type->ref && !arg->type->isArray() ) {
                if ( arg->type->baseType == Type::tFloat2 || arg->type->baseType == Type::tFloat4 ) {
                    arg->type->ref = false;
                }
            }
        }
        return true;
    }
    bool tempArgs = false;
    bool implicitArgs = true;
    bool tempResult = false;
    bool explicitConstArgs = false;
};

}
