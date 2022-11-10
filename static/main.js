import App from "./App.svelte";
import Bokeh from "bokeh";

const app = new App({
  target: document.body,
  // props: {
  //   name: "world",
  // },
});

export default app;

var val = 1;
var cnt = 0;

const source = new Bokeh.ColumnDataSource({
  data: { x: [0, 1, 2, 3, 4, 5], y: [0, 0, 0, 0, 0, 0] },
});
// make a plot with some tools
const plot = Bokeh.Plotting.figure({
  title: "Clock Locking",
  // tools: "pan,wheel_zoom,box_zoom,reset,save",
  tools: "",
  sizing_mode: "stretch_both",
  height: 400,
  width: 1200,
});
console.log(plot); //this lets you find all the color attributes
plot.output_backend = "webgl";
//plot.toolbar_location = "left";  //works
//plot.add_tools(new Bokeh.BoxZoomTool()); // this works!
//plot.visible = false;
//plot.sizing_mode = 'strech_both'

// for dark mode:
// plot.background_fill_color = "black";
// plot.border_fill_color = "black";

plot.toolbar.autohide = true;
plot.toolbar.logo = null; //"grey" javascript uses 'null' as none...
// plot.min_border_left = 0;
// plot.min_border_right = 0;
// plot.background_fill_color = "#2e2e2e"; //works
plot.min_border_left = 0;

// add a line with data from the source
plot.line(
  { field: "x" },
  { field: "y" },
  {
    source: source,
    line_width: 3,
    line_color: "#234a78",
  }
);

Bokeh.Plotting.show(plot, document.getElementById("myPlot"));

function addPoint() {
  // add data --- all fields must be the same length.
  source.data.x.push(val);
  source.data.y.push(Math.sin(val * 0.1) + 0.01 * val);
  source.change.emit();
}

//const addDataButton = document.createElement("Button");
//addDataButton.appendChild(document.createTextNode("Some data."));
//document.getElementById("this").appendChild(addDataButton);
//addDataButton.addEventListener("click", addPoint);
//console.log("here")

// var interval = setInterval(function () {
//   //Plotly.extendTraces('graph', {
//   //  y: [[rand()]]
//   //}, [0])
//   val = val + 1;
//   source.data.x.push(val);
//   source.data.y.push(Math.sin(val * 0.1));
//   source.change.emit();
//   //console.log(source.data.x.length)

//   if (source.data.x.length > 1000) {
//     source.data.x.shift();
//     source.data.y.shift();
//   }

//   if (cnt === 100) clearInterval(interval);
// }, 16);

// addPoint();
// addPoint();

const ws = new WebSocket("ws://10.7.0.173:8000/ws");
let x = 0;
const list = document.getElementById("list");
ws.onmessage = function (event) {
  const measurement = JSON.parse(event.data);
  x += 1;
  source.data.x.push(x);
  source.data.y.push(measurement.value);
  source.change.emit();
  if (source.data.x.length > 500) {
    source.data.x.shift();
    source.data.y.shift();
  }
};
