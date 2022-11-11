import './app.css'
import App from './App.svelte'
// import { Bokeh } from "./bokeh-2.2.0.min.js";
// import { embed } from '@bokeh/bokehjs'

const app = new App({
    target: document.getElementById('app')
})

export default app
const Bokeh = window.Bokeh;
// Bokeh.set_log_level('trace');
// Bokeh.set_log_level('debug');
//   Bokeh.set_log_level('info');
//   Bokeh.set_log_level('warn');
// Bokeh.set_log_level('error');
// Bokeh.set_log_level('fatal');
//   Bokeh.set_log_level('off');
// const Bokeh = window.Bokeh;
// console.log(Bokeh);
// console.log(Bokeh.document());

// console.log("view manager: ", Bokeh.ViewManager)



