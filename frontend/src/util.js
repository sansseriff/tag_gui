


export function set_plot_styling(plot) {
    plot.toolbar.autohide = true;
    plot.toolbar.logo = null; //"grey" javascript uses 'null' as none...

    const axis_color = "#9898a3";
    // if (color_mode == 'dark') {
    //     // light
    //     const axis_color = "#d4d4d4";
    //     plot.background_fill_color = "#2d2e33"; // this works

    // }
    plot.background_fill_color = "#fcfcfc";

    plot.axis.axis_label_text_color = axis_color;
    plot.axis.axis_line_color = axis_color;
    plot.axis.axis_line_width = 1.7;
    plot.axis.major_tick_line_color = axis_color;
    plot.axis.major_tick_line_width = 1.7;
    plot.axis.minor_tick_line_color = axis_color;
    plot.axis.major_label_text_color = axis_color;
    plot.axis.major_label_text_font_size = "medium";

}