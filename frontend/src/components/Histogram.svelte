<script>
    import { onMount } from "svelte";
    import { set_plot_styling } from "../util.js";
    import { colorModeStore } from "../stores";
    // export let master_data_2;
    // export let master_data_2;

    // const Bokeh = window.Bokeh;

    var val = 1;
    var cnt = 0;
    const x_length = 1000;
    var hist = null;

    $: if (hist != null) {
        set_plot_styling(hist, $colorModeStore.color);
    }

    onMount(async () => {
        const data_source = make_graph();

        // for (var j = 0; j < x_length; j++) {
        //     // data_source.data.x.push(j);
        //     data_source.data.y[j] = 40;
        // }

        var interval_2 = setInterval(function () {
            val = val + 1;
            for (var j = 0; j < x_length; j++) {
                // data_source.data.x.push(j);
                data_source.data.y[j] =
                    // data_source.data.y[j] +
                    2.1 + Math.sin(0.05 * j) + Math.sin(0.05 * val + j * 0.09);
            }
            data_source.change.emit();
            if (cnt === 100) clearInterval(interval_2);
        }, 20);
    });

    function make_graph() {
        const data = new Bokeh.ColumnDataSource({
            data: { x: [], y: [] }, // the columns can't ever be differnt lengths!
        });

        for (var j = 0; j < x_length; j++) {
            data.data.x.push(j);
            data.data.y.push(Math.sin(0.00628 * j + val));
        }

        const plt = Bokeh.Plotting;
        hist = plt.figure({
            tools: "",
            // tools: "pan,wheel_zoom,box_zoom,reset,save",
            sizing_mode: "stretch_width",
            height: 400,
            width: 2000,
            output_backend: "webgl",
            x_axis_label: "time (ns)",
            y_axis_label: "counts",
            y_axis_type: "log",
        });
        var line = new Bokeh.Line({
            x: { field: "x" },
            y: { field: "y" },
            line_color: "#eb4034",
            line_width: 1.8,
        });

        hist.add_glyph(line, data);
        set_plot_styling(hist);

        const doc = new Bokeh.Document();
        doc.add_root(hist);
        Bokeh.embed.add_document_standalone(
            doc,
            document.getElementById("hist_div")
        );
        // console.log("document:", doc);
        return data;
    }
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
    .box {
        flex-grow: 1;

        border-style: solid;
        border-width: 1.92px;
        border-color: rgb(225, 225, 225);
        /* border-radius: 5px; */
        margin: 10px;
        box-shadow: 3px 5px 20px -3px rgba(0, 0, 0, 0.05);
    }

    :global(body.dark-mode) .box {
        border-color: rgb(72, 72, 72);
        box-shadow: 3px 5px 20px -3px rgba(255, 255, 255, 0.05);
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
    :global(body.dark-mode) h5 {
        color: rgb(225, 225, 225);
    }
</style>
