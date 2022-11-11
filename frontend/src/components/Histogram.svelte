<script>
    import { onMount } from "svelte";
    import { set_plot_styling } from "../util.js";
    import { colorModeStore } from "../stores";
    // export let master_data_2;
    // export let master_data_2;

    // const Bokeh = window.Bokeh;

    var val = 1;
    var cnt = 0;
    const x_length = 10000;

    onMount(async () => {
        const data_source = make_graph();

        var interval_2 = setInterval(function () {
            val = val + 1;

            for (var j = 0; j < x_length; j++) {
                // data_source.data.x.push(j);
                data_source.data.y[j] =
                    data_source.data.y[j] + Math.sin(0.00628 * j * 0.1 * val);
            }
            data_source.change.emit();

            if (cnt === 100) clearInterval(interval_2);
        }, 16);
    });

    function make_graph() {
        const data = new Bokeh.ColumnDataSource({
            data: { x: [], y: [] }, // the columns can't ever be differnt lengths!
        });

        for (var j = 0; j < x_length; j++) {
            data.data.x.push(j);
            data.data.y.push(Math.sin(0.00628 * j + val));
        }

        // const X = [];
        // const Y = [];
        // X.push(3);
        // Y.push(7);
        // for (var j = 0; j < 1024; j++) {
        //     Y.push(Math.sin(0.00628 * j + val));
        //     X.push(j);
        // }

        const plt = Bokeh.Plotting;
        var hist = plt.figure({
            tools: "",
            // tools: "pan,wheel_zoom,box_zoom,reset,save",
            sizing_mode: "stretch_width",
            height: 300,
            width: 2000,
            output_backend: "webgl",
            x_axis_label: "time (ns)",
            y_axis_label: "counts",
        });
        var line = new Bokeh.Line({
            x: { field: "x" },
            y: { field: "y" },
            line_color: "#eb4034",
            line_width: 1.8,
        });

        // hist.output_backend = "webgl";

        hist.add_glyph(line, data);

        set_plot_styling(hist);
        // hist.toolbar.autohide = true;
        // hist.toolbar.logo = null; //"grey" javascript uses 'null' as none...
        // hist.background_fill_color = "#fcfcfc"; // this works

        // const axis_color = "#9898a3";
        // hist.axis.axis_label_text_color = axis_color;
        // hist.axis.axis_line_color = axis_color;
        // hist.axis.axis_line_color = axis_color;
        // hist.axis.axis_line_width = 1.7;
        // hist.axis.major_tick_line_color = axis_color;
        // hist.axis.major_tick_line_width = 1.7;
        // hist.axis.minor_tick_line_color = axis_color;
        // hist.axis.major_label_text_color = axis_color;
        // hist.axis.major_label_text_font_size = "medium";

        // plt.show(hist, document.getElementById("hist_div"));

        const doc = new Bokeh.Document();
        doc.add_root(hist);
        Bokeh.embed.add_document_standalone(
            doc,
            document.getElementById("hist_div")
        );
        // console.log("document:", doc);
        return data;
    }

    // for (var j = 0; j < 1024; j++) {
    //     master_data_2.data.x.push(j);
    //     master_data_2.data.y.push(0);
    // }

    // for (var j = 0; j < 1024; j++) {
    //     master_data_2.data.x[j] = 0;
    // }
</script>

<div class="box">
    <div class="title">
        <h5>Histogram</h5>
    </div>
    <div class="plot_container">
        <div id="hist_div" />
    </div>
</div>

<style>
    /* html {
        width: 100%;
        height: 100%;
    } */
    .box {
        flex-grow: 1;

        /* display: flex;
        flex-direction: column; */
        /* width: 100%; */
        /* flex-direction: row; */
        /* flex-grow: 1; */
        border-style: solid;
        border-width: 1.92px;
        border-color: rgb(225, 225, 225);
        border-radius: 5px;
        margin: 10px;
        box-shadow: 3px 5px 20px -3px rgba(0, 0, 0, 0.1);
    }

    .title {
        /* flex-grow: 1; */
    }

    body {
        width: 100%;
        height: 100%;
        margin: 0;
    }

    #hist_div {
        padding: 15px 15px;

        /* flex-grow: 2; */
        /* min-height: 500px; */
    }
    .plot_container {
        /* flex-grow: 19; */
    }

    h5 {
        display: block;
        padding: 20px 0px 0px 0px;
        text-align: center;
        margin-left: auto;
        margin-right: auto;
        font-size: 1.1rem;
        font-weight: 100;
        color: #333;
    }
</style>
