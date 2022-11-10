<script>
    import svelteLogo from "./assets/svelte.svg";
    import Counter from "./lib/Counter.svelte";
    import { onMount } from "svelte";
    import CountRate from "./CountRate.svelte";
    import Controlls from "./Controlls.svelte";
    import Histogram from "./Histogram.svelte";

    // import * as Bokeh from window;

    // Bokeh.set_log_level("info");
    // Bokeh.logger.info(`Bokeh ${Bokeh.version}`);

    // const Bokeh_2 = structuredClone(Bokeh);

    var val = 1;
    var val2 = 0;
    var cnt = 0;

    //   Bokeh.set_log_level('trace');
    //   Bokeh.set_log_level('debug');
    //   Bokeh.set_log_level('info');
    //   Bokeh.set_log_level('warn');
    //   Bokeh.set_log_level('error');
    //   Bokeh.set_log_level('fatal');
    //   Bokeh.set_log_level('off');

    function setup_websocket(data) {
        const ws = new WebSocket("ws://10.7.0.173:8000/ws");
        let x = 0;
        const list = document.getElementById("list");
        ws.onmessage = function (event) {
            const measurement = JSON.parse(event.data);
            x += 1;
            data.data.x.push(x);
            data.data.y.push(measurement.value);
            data.change.emit();
            if (data.data.x.length > 500) {
                data.data.x.shift();
                data.data.y.shift();
            }
        };
    }
</script>

<main class="container">
    <div>
        <Controlls />
        <div class="measurement_box">
            <Histogram />
            <CountRate />
        </div>
    </div>
</main>

<style>
    .container {
        width: 100%;
        height: 100%;
        /* margin: 0;
        display: flex; */
        max-width: 1300px;
        margin: 0 auto;
        padding: 0 0px;
    }
    .measurement_box {
        display: flex;
        flex-direction: row;
    }

    :global(body) {
        background-color: white;
        /* color: #0084f6; */
        transition: background-color 0.3s;
    }
    :global(body.dark-mode) {
        background-color: #1d3040;
        color: #bfc2c7;
    }
</style>
