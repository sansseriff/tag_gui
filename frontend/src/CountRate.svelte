<script>
    import { onMount } from "svelte";
    // export let master_data;
    // export let doc;

    // I think you need this so that bokeh
    // inits with correct screen size and stuff

    // const Bokeh = window.Bokeh;

    onMount(async () => {
        make_graph_1();
    });

    function make_graph_1() {
        const data = new Bokeh.ColumnDataSource({
            data: { x: [0], y: [0], x2: [0], y2: [0] },
        });

        const data_dummy = new Bokeh.ColumnDataSource({
            data: { x: [0, 1], y: [0, 1] },
        });

        // make a plot with some tools
        const count_rate = new Bokeh.Plotting.figure({
            // title: "Example of random data",
            // tools: "pan,wheel_zoom,box_zoom,reset,save",
            tools: "",
            // sizing_mode: "stretch_both",
            sizing_mode: "stretch_width",
            height: 300,
            width: 2000,
            output_backend: "webgl",
            x_axis_label: "time (s)",
            y_axis_label: "counts",
        });
        // count_rate.output_backend = "webgl";
        const count_rate_2 = new Bokeh.Plotting.figure({
            // title: "Example of random data",
            // tools: "pan,wheel_zoom,box_zoom,reset,save",
            tools: "",
            //tools: "",
            // sizing_mode: "stretch_both",
            sizing_mode: "stretch_width",
            height: 300,
            width: 2000,
        });

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

        // const circles = count_rate.circle(
        //     { field: "x" },
        //     { field: "y" },
        //     { source: data, radius: 2, fill_alpha: 1, line_color: null }
        // );

        const line_1 = count_rate.line(
            { field: "x" },
            { field: "y" },
            {
                source: data,
                line_width: 3,
                line_color: "#234a78",
            }
        );
        const line_2 = count_rate_2.line(
            { field: "x" },
            { field: "y" },
            {
                source: data_dummy,
                line_width: 3,
                line_color: "#a842d4",
            }
        );
        // doc.add_root(count_rate);
        // this attribute isn't available during the object initialization. Only after?

        // count_rate_2.output_backend = "webgl";
        //plot.toolbar_location = "left";  //works
        //plot.add_tools(new Bokeh.BoxZoomTool()); // this works!
        //plot.visible = false;
        //plot.sizing_mode = 'strech_both'
        count_rate.toolbar.autohide = true;
        count_rate.toolbar.logo = null; //"grey" javascript uses 'null' as none...
        count_rate.background_fill_color = "#fcfcfc"; // this works

        console.log(count_rate.axis);

        // add a line with data from the source

        // console.log(count_rate.axis);
        const axis_color = "#9898a3";
        // count_rate.axis.axis_label = "time (s)";
        count_rate.axis.axis_label_text_color = axis_color;
        count_rate.axis.axis_line_color = axis_color;
        count_rate.axis.axis_line_width = 1.7;
        count_rate.axis.major_tick_line_color = axis_color;
        count_rate.axis.major_tick_line_width = 1.7;
        count_rate.axis.minor_tick_line_color = axis_color;
        count_rate.axis.major_label_text_color = axis_color;
        count_rate.axis.major_label_text_font_size = "medium";

        // Bokeh.Plotting.show(count_rate, document.getElementById("count_rate"));

        const doc_2 = new Bokeh.Document();
        doc_2.add_root(count_rate_2);
        doc_2.add_root(count_rate);

        Bokeh.embed.add_document_standalone(
            doc_2,
            document.getElementById("count_rate")
        );

        let d = document.getElementById("count_rate");

        var val = 1;
        var cnt = 1;

        var interval = setInterval(function () {
            val = val + 1;
            data.data.x.push(val);
            data.data.y.push(Math.sin(val * 0.1));
            data.data.x2.push(val);
            data.data.y2.push(Math.sin(val * 0.5));
            data.change.emit();
            if (val == 2) {
                // This is super janky
                // console.log("THIS: ", d.firstChild);
                d.removeChild(d.firstChild);
            }

            if (data.data.x.length > 10000) {
                data.data.x.shift();
                data.data.y.shift();
                data.data.x2.shift();
                data.data.y2.shift();
            }

            if (cnt === 100) clearInterval(interval);
        }, 100);

        // Bokeh.embed.add_document_standalone(
        //     doc_2,
        //     document.getElementById("count_rate2")
        // );
        // Bokeh.embed.add_document_standalone(
        //     doc_2,
        //     document.getElementById("count_rate_2")
        // );
        // console.log("DHIO:SDKLFJDS");

        // console.log("embed: ", Bokeh.embed);
        // const doc = Bokeh.document();
        // console.log("roots: ", Bokeh.document());

        //const addDataButton = document.createElement("Button");
        //addDataButton.appendChild(document.createTextNode("Some data."));
        //document.getElementById("this").appendChild(addDataButton);
        //addDataButton.addEventListener("click", addPoint);
        //console.log("here")
        // var doc = new Bokeh.Document();
        // doc.add_root(count_rate);
        // var div = html``;
        // Bokeh.embed.add_document_standalone(doc, div);
        // document.getElementById("hist_div").innerHTML = div;
        // var bkdoc = Bokeh._.values(Bokeh.index)[0].model.document;
        // console.log(bkdoc);
    }
</script>

<div class="box">
    <div class="title">
        <h5>Count Rate</h5>
    </div>
    <div class="plot_container">
        <div id="count_rate" />
        <!-- <div id="count_rate_2" /> -->
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
</style>
