import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [svelte(),
        // commonjsExternals.default({
        //     externals: [
        //         'choices.js',
        //         'flatbush',
        //         'timezone',
        //         'stream',
        //         '@bokeh/numbro',]
        // })
    ]

})



// export default defineConfig({
//     plugins: [svelte(),
//     commonjsExternals.default({
//         externals: [
//             'choices.js',
//             'flatbush',
//             'timezone',
//             'stream',
//             '@bokeh/numbro',]
//     })
//     ]