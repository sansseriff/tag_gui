


export function set_plot_styling(plot, color_mode) {
    // console.log(color_mode, "yesss")
    plot.toolbar.autohide = true;
    plot.toolbar.logo = null; //"grey" javascript uses 'null' as none...

    // var axis_color = "#9898a3";
    if (color_mode == 'dark') {
        // dark
        var axis_color = "#9c9c9c";
        plot.background_fill_color = "#393a40"; // this works

        plot.border_fill_color = "#2d2e33"
        // console.log("plot.axis: ", plot)
        plot.grid.grid_line_color = "#47484f"
        plot.grid.grid_line_alpha = 0.7



    }
    else {
        // light
        var axis_color = "#9898a3";
        plot.background_fill_color = "#fcfcfc";
        plot.border_fill_color = "#ffffff"
        // plot.axis.major_tick_line_alpha = 0.2
        // plot.axis.axis_line_alpha = 0.1
        // plot.axis.major_tick_line_alpha = 0.1
        // plot.axis.minor_tick_line_alpha = 0.1
        plot.grid.grid_line_color = "#9898a3"
        plot.grid.grid_line_alpha = 0.2




    }
    plot.outline_line_alpha = 0

    plot.grid.grid_line_width = 1.5
    plot.axis.axis_line_width = 1.7;
    plot.axis.axis_label_text_color = axis_color;
    plot.axis.axis_line_color = axis_color;
    plot.axis.major_tick_line_color = axis_color;
    plot.axis.major_tick_line_width = 1.7;
    plot.axis.minor_tick_line_color = axis_color;
    plot.axis.major_label_text_color = axis_color;
    plot.axis.major_label_text_font_size = "medium";

}