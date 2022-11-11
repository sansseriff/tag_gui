<script>
    export let channel;

    // console.log(channel);
</script>

<div class="channel-box">
    <div class="channel">
        <div class="pad">
            <input class="input" id="first" type="text" value={channel.input} />
            <input class="input" type="text" value={channel.input_delay} />
            <input class="input" type="text" value={channel.trigger_level} />
            <input class="input" type="text" value={channel.dead_time} />
        </div>
    </div>
</div>

<style>
    .channel-box {
        margin: 5px;
    }
    input {
        padding: 2px;
        /* border-width: 2px; */
        border-style: none;
        border-left: 1.5px solid rgb(229, 229, 229);

        /* border-style: solid; */
        /* border-color: rgb(229, 229, 229); */
        /* border-radius: 5px; */
    }
    .channel {
        border-width: 1.5px;
        border-style: solid;
        border-color: rgb(229, 229, 229, 0.5);
        /* border-radius: 5px; */
        box-shadow: 3px 5px 5px -3px rgba(0, 0, 0, 0.05);
    }

    :global(body.dark-mode) .channel {
        /* border-color: rgb(229, 229, 229, 0.5); */
        border-color: rgb(72, 72, 72);
    }

    #first {
        border-left: 1.5px solid rgb(229, 229, 229, 0);
    }

    .pad {
        display: flex;
        flex-direction: row;
        padding: 5px;
    }
</style>
