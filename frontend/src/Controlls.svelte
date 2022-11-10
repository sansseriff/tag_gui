<script>
    import Channel from "./Channel.svelte";
    import { v4 as uuidv4 } from "uuid";

    let channels = [
        {
            id: uuidv4(),
            input: 5,
            input_delay: 1000,
            trigger_level: -0.02,
            dead_time: 100,
        },
        {
            id: uuidv4(),
            input: -14,
            input_delay: 500,
            trigger_level: -0.02,
            dead_time: 100,
        },
        {
            id: uuidv4(),
            input: 9,
            input_delay: 1000,
            trigger_level: -0.02,
            dead_time: 100,
        },
    ];
</script>

<div class="controlls">
    <div class="header">
        <div class="heading">
            <h3>Time Tagger Controll</h3>
        </div>
    </div>
    <div class="data_input">
        {#each channels as channel}
            <Channel {channel} />
        {/each}
    </div>
    <div class="footer">
        <h3 id="plus">+</h3>
        <button>Add Measurment</button>
    </div>
</div>

<style>
    .controlls {
        margin: 0 10px;
        padding: 0px 0px;
        border-bottom: 1.5px solid rgb(229, 229, 229);
        border-left: 1.5px solid rgb(229, 229, 229);
        border-right: 1.5px solid rgb(229, 229, 229);
        box-shadow: 3px 5px 20px -3px rgba(0, 0, 0, 0.1);
        border-radius: 0 0 5px 5px;
    }
    .heading {
        margin-left: auto;
        margin-right: 0;
        width: 250px;
        height: 50px;
        background-color: #76b1ff;
        /* display: flex; */
        margin-bottom: 0px;
        border-radius: 0 0 0px 90px;
    }
    h3 {
        /* Time Tagger Controll */
        display: block;
        text-align: right;
        /* height: 40px; */
        padding: 12px 25px;
        color: white;
        font-weight: 200;
        font-size: larger;
        /* top: 50%; */
    }
    #plus {
        display: block;
        color: rgb(92, 92, 92);
        font-size: xx-large;
        font-weight: 100;
        padding: 9px 18px;
        height: 50px;
    }

    .header {
        border-bottom: 1.5px solid rgb(229, 229, 229);
        margin-bottom: 0px;
    }
    .footer {
        display: flex;
        flex-direction: row;
        border-top: 1.5px solid rgb(229, 229, 229);
        /* border-bottom: 1.5px solid rgb(229, 229, 229); */
        height: 50px;
    }

    button {
        display: block;
        background: none;
        color: black;
        border-style: none;
        height: 50px;
        margin: 0;
        padding: 16px;
        cursor: pointer;
        font-weight: 200;
        font-size: larger;
    }
    li {
        list-style: none;
        padding: 5px;
    }

    .data_input {
        padding: 30px;
    }
</style>
