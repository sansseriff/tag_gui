<script>
    import { colorModeStore } from "../stores";

    function toggle() {
        window.document.body.classList.toggle("dark-mode");
    }

    let checked = false;

    function handleClick(event) {
        // if (!checked && !window.confirm('Really opt-in?')) {
        //   return;
        // }
        window.document.body.classList.toggle("dark-mode");
        checked = !checked;
        colorModeStore.update((color_obj) => {
            if (color_obj.color == "light") {
                color_obj.color = "dark";
            } else {
                color_obj.color = "light";
            }
            return color_obj;
        });
        setTimeout(() => (event.target.checked = checked), 0);
    }
</script>

<!-- <button on:click={toggle}>
    <slot />
</button> -->

<div class="theme-switch-wrapper">
    <label class="theme-switch" for="checkbox">
        <input
            type="checkbox"
            id="checkbox"
            {checked}
            on:click|preventDefault={handleClick}
        />
        <div class="slider round" />
    </label>
    <!-- <em>Enable Dark Mode!</em> -->
</div>

<style>
    /* button {
        background-color: #f76027;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem;
        text-transform: uppercase;
        margin: 0.5rem;
    }
    :global(body.dark-mode) button {
        background-color: #0084f6;
        color: white;
    } */

    /*Simple css to style it like a toggle switch*/
    .theme-switch-wrapper {
        display: flex;
        align-items: center;
        margin: 0.5rem 1rem;
    }
    /* em {
        margin-left: 10px;
        font-size: 1rem;
    } */
    .theme-switch {
        display: inline-block;
        height: 30px;
        position: relative;
        width: 56px;
    }

    .theme-switch input {
        display: none;
    }

    .slider {
        background-color: #ccc;
        bottom: 0;
        cursor: pointer;
        left: 0;
        position: absolute;
        right: 0;
        top: 0;
        transition: 0.4s;
    }

    .slider:before {
        background-color: #fff;
        bottom: 4px;
        content: "";
        height: 22px;
        left: 4px;
        position: absolute;
        transition: 0.4s;
        width: 22px;
    }

    input:checked + .slider {
        background-color: #66bb6a;
    }

    input:checked + .slider:before {
        transform: translateX(26px);
    }

    .slider.round {
        border-radius: 34px;
    }

    .slider.round:before {
        border-radius: 50%;
    }

    :global(body.dark-mode) button {
        background-color: #0084f6;
        color: white;
    }
</style>
