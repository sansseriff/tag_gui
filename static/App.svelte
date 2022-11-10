<script>
  import Topbar from "./components/Topbar.svelte";
  import { clickOutside } from "./click_outside.js";
  let showModal = false;
</script>

<main>
  <body>
    <Topbar />
    <div id="myPlot" />
    {#if showModal}
      <div class="box" use:clickOutside on:outclick={() => (showModal = false)}>
        Click outside me!
      </div>
    {/if}
  </body>
</main>

<style>
  body {
    width: 100%;
    height: 100%;
    margin: 0;
  }

  #myPlot {
    padding: 10px 10px;
  }
  .box {
    --width: 100px;
    --height: 100px;
    position: absolute;
    width: var(--width);
    height: var(--height);
    left: calc(50% - var(--width) / 2);
    top: calc(50% - var(--height) / 2);
    display: flex;
    align-items: center;
    padding: 8px;
    border-radius: 4px;
    background-color: #7051ed;
    color: #fff;
    text-align: center;
    font-weight: bold;
  }
</style>
