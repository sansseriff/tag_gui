<script>
    import { onMount } from "svelte";
    import { set_plot_styling } from "../util.js";
    import { colorModeStore } from "../stores";

    // I think you need this so that bokeh
    // inits with correct screen size and stuff
    var count_rate = null;

    // $: count = set_plot_styling($colorModeStore.color;
    // onMount(async () => {
    // $: set_plot_styling(hist, $colorModeStore.color);
    // })

    // $: if (count_rate != null) {
    //     set_plot_styling(count_rate, $colorModeStore.color);
    // }
    $: if (count_rate != null) {
        set_plot_styling(count_rate, $colorModeStore.color);
    }

    onMount(async () => {
        make_graph_1();
    });

    function make_graph_1() {
        // const data = new Bokeh.ColumnDataSource({
        //     data: { x: [], y: [], x2: [], y2: [] },
        // });

        let data = new Bokeh.ColumnDataSource({
            data: { x: [], y: [], x2: [], y2: [] },
        });

        const ToolTips = { index: "$index", "(x,y)": "($x,$y)" };

        // make a plot with some tools
        // count_rate = new Bokeh.Plotting.figure({
        //     // title: "Example of random data",
        //     // tools: "pan,wheel_zoom,box_zoom,reset,save",
        //     tools: "",
        //     // sizing_mode: "stretch_both",
        //     sizing_mode: "stretch_width",
        //     height: 400,
        //     width: 2000,
        //     output_backend: "webgl",
        //     x_axis_label: "time (s)",
        //     y_axis_label: "counts",
        //     // y_range: [0, 2],
        // });

        var custom_tooltips = [
            ["X", "@x"],
            ["Y", "@y"],
        ];

        var custom_hover = new Bokeh.HoverTool({
            tooltips: custom_tooltips,
            mode: "mouse",
        });
        // count_rate.add_tools(custom_hover);
        

        // count_rate.output_backend = "webgl";
        count_rate = new Bokeh.Plotting.figure({
            // title: "Example of random data",
            // tools: "pan,wheel_zoom,box_zoom,reset,save",
            tools: "",
            //tools: "",
            // sizing_mode: "stretch_both",
            sizing_mode: "stretch_width",
            height: 400,
            width: 2000,
        });
        count_rate.add_tools(custom_hover);

        // const N = xx.length
        // var range = Bokeh.LinAlg.range
        // var Random = Bokeh.LinAlg.random
        // const random = new Random(1)
        // const radii = Bokeh.LinAlg.range(N).map((_) => random.float() * 0.4 + 1.7);
        // const colors = [];
        // for (const [r, g] of zip(
        //     xx.map((x) => 50 + 2 * x),
        //     yy.map((y) => 30 + 2 * y)
        // ))
        //     colors.push(plt.color(r, g, 150));

        const line_2 = count_rate.line(
            { field: "x" },
            { field: "y" },
            {
                source: data,
                line_width: 3,
                line_color: "#5185c2",
            }
        );

        const line_2a = count_rate.line(
            { field: "x2" },
            { field: "y2" },
            {
                source: data,
                line_width: 3,
                line_color: "#b562cc",
            }
        );

        // set_plot_styling(count_rate);

        // count_rate.toolbar.autohide = true;
        // count_rate.toolbar.logo = null; //"grey" javascript uses 'null' as none...
        // count_rate.background_fill_color = "#fcfcfc"; // this works

        // console.log(count_rate.axis);

        // // add a line with data from the source

        // // console.log(count_rate.axis);
        // const axis_color = "#9898a3";
        // // count_rate.axis.axis_label = "time (s)";
        // count_rate.axis.axis_label_text_color = axis_color;
        // count_rate.axis.axis_line_color = axis_color;
        // count_rate.axis.axis_line_width = 1.7;
        // count_rate.axis.major_tick_line_color = axis_color;
        // count_rate.axis.major_tick_line_width = 1.7;
        // count_rate.axis.minor_tick_line_color = axis_color;
        // count_rate.axis.major_label_text_color = axis_color;
        // count_rate.axis.major_label_text_font_size = "medium";

        // Bokeh.Plotting.show(count_rate, document.getElementById("count_rate"));

        const doc_2 = new Bokeh.Document();
        doc_2.add_root(count_rate);
        // doc_2.add_root(count_rate);

        // Bokeh.embed.add_document_standalone(
        //     doc_2,
        //     document.getElementById("count_rate")
        // );

        let d = document.getElementById("count_rate");

        var val = 1;
        var cnt = 1;

        var interval = setInterval(function () {
            val = val + 1;
            data.data.x.push(val);
            data.data.y.push(1 + 0.08 * Math.sin(val * 0.1) + Math.random());
            data.data.x2.push(val);
            data.data.y2.push(0.1*Math.sin(val * 0.1) + 6 + 0.5*Math.random());
            data.change.emit();
            // if (val == 2) {
            //     // This is super janky
            //     // console.log("THIS: ", d.firstChild);
            //     d.removeChild(d.firstChild);
            // }

            if (data.data.x.length > 400) {
                data.data.x.shift();
                data.data.y.shift();
                data.data.x2.shift();
                data.data.y2.shift();
            }

            if (cnt === 100) clearInterval(interval);
        }, 16);

        Bokeh.embed.add_document_standalone(
            doc_2,
            document.getElementById("count_rate")
        );
    }
</script>

<div class="box">
    <div class="title">
        <h5>Count Rate</h5>
    </div>
    <div class="plot_container">
        <div id="count_rate" />
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

    #count_rate {
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
