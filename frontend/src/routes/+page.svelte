<script>
    import { onMount } from 'svelte';

    // TODO : Dev, Production
    const api_host = 'http://localhost:8080';

    class Image {
        /**
         * @param {string} id
         * @param {string} url
         * @param {string | null} thumb
         * @param {string} title
         */
        constructor (id, url, thumb, title) {
            this.id = id;
            this.url = url;
            this.thumb = thumb ?? url;
            this.title = title;
            this.base64 = null;
        }

        async getBase64 () {
            if (this.base64) {
                return this.base64;
            }

            await fetch(`${api_host}/api/download`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                body: JSON.stringify({
                    "url": this.url
                })
            }).then(res => {
                this.base64 = res.text();
            });

            return this.base64;
        }
    }

    class GeneratedImgFromCaption {
        constructor () {
            /** @type {(Image|null)[]} */
            this.generatedImgs = [];
            this.caption = '...';
            this.ing_gen_num = num_karlo + num_sd;
            this.editing = false;
        }

        /** @param {string} caption */
        setCaption (caption) {
            this.caption = caption;
            this.more();
        }
        
        async more() {
            this.ing_gen_num = num_karlo + num_sd;
            img_selected.generations = img_selected.generations;

            const cb = (results)=>{
              for (let i = 0; i < results.length; i++) {
                this.generatedImgs.push(new Image(
                        `karlo_gen_${i}`,
                        results[i]['image'],
                        'data:image/png;base64, ' + results[i]['image'],
                        ''
                    ));
                }
            };

            let karlo_promise = karlo_generation(this.caption, cb)
            await karlo_promise;

            this.ing_gen_num = 0;
            img_selected.generations = img_selected.generations;
        }
    }

    const SearchStatus = {
        INIT: 0,
        SEARCHING: 1,
        DONE: 2,
    };
    
    let num_col = 6;
    let status = SearchStatus.INIT;
    let loading_pct = 0;
    let ing_var_num = 0;
    let new_prompt = '';

    const num_karlo = 2;
    const num_sd = 2
    
    onMount(() => {
        if (window.screen.width * 1.33 > window.screen.height) {
        } else {
            num_col = 2;
        }
	});
    
    let prompt_presets = [
        '',
        // ', cinematic, hyper realistic, 4K, very detailed',
        // ', oil painting',
        // ', sticker illustration',
        // ', anime style',
        // ', cartoon style',
    ]
    
    /** @type {Image[]} */
    let images = [];
    let prompt = '';
    let img_selected = {
        'selected': false,
        /** @type {string} */
        'id': '',
        /** @type {undefined | null | Image} */
        'data': null,
        /** @type {GeneratedImgFromCaption[]} */
        'generations': [],
        /** @type {Image[]} */
        'variations': []
    };
    
     /**
     * @param {string} img_id
     * @param {((results: any) => void) | undefined} callback
     */
      export async function karlo_variation(img_id, callback){
        const num_var = num_karlo + num_sd;
        ing_var_num = num_var;
        // @ts-ignore
        var img_src = document.getElementById(img_id).src;
        
        // post request 
        let promises = [];
        const rp = fetch(`${api_host}/api/karlo/variations`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                "mode": "AA",
                "prompt": {
                    "text": "",
                    "image": img_src,
                    "batch_size": num_karlo,
                }
            })
        });
        promises.push(rp);

        // stable diffusion
        for (let i = 0; i < num_sd; i ++) {
          const rp = fetch(`http://34.124.237.132:${9000+i}/variation`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
                  'Access-Control-Allow-Origin': '*'
              },
              body: JSON.stringify({
                "prompt": '',
                'source_img': img_src,
                'steps': 20,
                'strength': 0.6
              })
          });
          promises.push(rp);
        }
        
        const responses = await Promise.all(promises);
        ing_var_num = 0;

        for (let i = 0; i < responses.length; i ++) {
          let response = responses[i];

          // print success message if response is ok
          if (response.ok) {
              console.log('Success');
          } else {
              console.log('Request failed!');
              return false;
          }
          // response to json
          const result = await response.json();

          if (callback === undefined) {
            callback = (results) => {
            for (let i = 0; i < results.length; i++) {
                img_selected.variations.push(new Image(
                  `karlo_var_${img_selected.variations.length + i}`,
                  results[i]['image'],
                  'data:image/png;base64, ' + results[i]['image'],
                  ''
                ));
            }
                
            }
          }
          callback(result['images']);
          img_selected.variations = img_selected.variations;
        }
    }

    /**
     * @param {string} prompt
     * @param {((results: Object[]) => void) | undefined} callback
     */
     export async function karlo_generation(prompt, callback){
        // post request 
        /** @type {Promise<any>[]} */
        let promises = [];
        const rp = fetch(`${api_host}/api/karlo/t2i`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({
                "mode": "AA",
                "prompt": {
                    "text": prompt,
                    "batch_size": num_karlo,
                }
            })
        });
        promises.push(rp);

        // stable diffusion
        for (let i = 0; i < num_sd; i ++) {
          const rp = fetch(`http://34.124.237.132:${9000+i}/generate`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
                  'Access-Control-Allow-Origin': '*'
              },
              body: JSON.stringify({
                "prompt": prompt,
              })
          });
          promises.push(rp);
        }

        const responses = await Promise.all(promises);

        for (let i = 0; i < responses.length; i ++) {
          let response = responses[i];
          // print success message if response is ok
          if (response.ok) {
              console.log('Success');
          } else {
              console.log('Request failed!');
              return false;
          }

          // response to json
          const result = await response.json();
          // @ts-ignore
          callback(result['images']);
        }
    }

    /**
     * 
     * @param gen {GeneratedImgFromCaption}
     */
    function karlo_generation_new(gen) {
        gen.editing = false;
        let idx = img_selected['generations'].indexOf(gen);

        const genImg = new GeneratedImgFromCaption();
        img_selected['generations'].splice(idx + 1, 0, genImg);
        genImg.setCaption(new_prompt);
    }

    export async function google_images(prompt=''){
        let url = `${api_host}/api/gsearch/` + prompt
        let response = await fetch(url).then(response => response.json());
        return response['images_results'];
    }

    async function image_search(){
        status = SearchStatus.SEARCHING;
        img_selected.selected = false;
        loading_pct = 70;
        console.log('image_search: ' + prompt);
        let data = await google_images(prompt);

        images = [];
        
        for (let i = 0; i < data.length; i++) {
            images.push(new Image(
                `google_img_${i}`,
                data[i]['original'],
                data[i]['thumbnail'],
                data[i]['title']
            ));
        }
        images = images;
        status = SearchStatus.DONE;
    }

    /**
     * 검색 결과에서 특정 이미지를 클릭했을 때.
     * @param {string} img_id
     */
    async function click_img(img_id){
        let img = images.find(img => img.id == img_id);

        img_selected.variations = []
        img_selected.generations = []

        let imgobj = new Image('temp_selected', img.url, null, '');
        imgobj.getBase64().then((b64)=>{
          // @ts-ignore
          document.getElementById(img_id).src = 'data:image/png;base64, ' + b64;
          img_selected.data.thumb = 'data:image/png;base64, ' + b64;
          karlo_variation(img_id, undefined);
        }).catch(()=>karlo_variation(img_id, undefined));

        img_selected['selected'] = true;
        img_selected['id'] = img_id;
        img_selected['data'] = img;

        const genImg = new GeneratedImgFromCaption();
        img_selected['generations'].push(genImg)
        genImg.setCaption(await fetch('http://gpu-cloud-vnode47.dakao.io:7288/captioning', {        // 7288 : nlpconnect, 7289 : coyo pre-trained
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            // @ts-ignore
            body: JSON.stringify({"data": await img.getBase64()})
        }).then(response => response.json()).then(data => `${prompt}, ${data['caption']}`));
    }
    
</script>

<div class="my-auto w-full {status == SearchStatus.DONE ? 'h-full' : ''}">
    <input class='query w-full border-0 text-5xl font-semibold focus:ring-0 px-4 sm:px-6 lg:px-8' style="text-align:center" type="text" bind:value={ prompt } on:change={() => image_search() } autofocus>
    <div class="w-full bg-gray-200 h-px mb-6 {status == SearchStatus.DONE ? 'hidden' : ''}">
        <div id="loading" class="bg-gray-400 h-px" style="width: {loading_pct}%"></div>
    </div>

    {#if img_selected.selected}
    <div class="relative z-10" role="dialog" aria-modal="true">
        <!--
          Background backdrop, show/hide based on slide-over state.
      
          Entering: "ease-in-out duration-500"
            From: "opacity-0"
            To: "opacity-100"
          Leaving: "ease-in-out duration-500"
            From: "opacity-100"
            To: "opacity-0"
        -->
        <!-- <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div> -->
      
        <div class="fixed inset-y-0 right-0 overflow-hidden">
          <div class="absolute inset-y-0 right-0 overflow-hidden">
            <div class="pointer-events-none fixed inset-y-0 right-0 flex w-screen">
              <!--
                Slide-over panel, show/hide based on slide-over state.
      
                Entering: "transform transition ease-in-out duration-500 sm:duration-700"
                  From: "translate-x-full"
                  To: "translate-x-0"
                Leaving: "transform transition ease-in-out duration-500 sm:duration-700"
                  From: "translate-x-0"
                  To: "translate-x-full"
              -->
              <div class="pointer-events-auto w-full relative border-l-2">
                <!--
                  Close button, show/hide based on slide-over state.
      
                  Entering: "ease-in-out duration-500"
                    From: "opacity-0"
                    To: "opacity-100"
                  Leaving: "ease-in-out duration-500"
                    From: "opacity-100"
                    To: "opacity-0"
                -->
      
                <!-- Slide-over panel, show/hide based on slide-over state. -->
                <div class="bg-gray-50 h-full overflow-y-auto p-8">

                    <div class="absolute top-0 right-0 -ml-8 flex pt-4 pr-2 sm:-ml-10 sm:pr-4">
                        <button type="button" class="rounded-md text-gray-300 hover:text-white focus:outline-none focus:ring-2 focus:ring-white" on:click={()=>{img_selected.selected=false;}}>
                          <span class="sr-only">Close panel</span>
                          <!-- Heroicon name: outline/x-mark -->
                          <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                    </div>

                  <div class="space-y-6">
                    <div>
                      <div class="block overflow-hidden w-1/4 rounded-lg">
                        <img src="{img_selected.data?.thumb}" alt="{img_selected.data?.title}" class="object-cover object-center w-full">
                      </div>
                      <div class="mt-4 flex items-start justify-between">
                        <div>
                          <h2 class="text-lg font-medium text-gray-900">{img_selected.data?.title}</h2>
                          <!-- <p class="text-sm font-medium text-gray-500">3.9 MB</p> -->
                        </div>
                        
                      </div>
                    </div>
                    
                    <div>
                      <h3 class="font-medium text-gray-900">Generation</h3>  

                      {#each img_selected['generations'] as gen}
                      <div class="mt-2 flex items-center justify-between">
                        <p class="text-sm italic text-gray-500">{gen.caption}</p>

                        <button type="button" class="-mr-2 flex h-8 w-8 items-center justify-center rounded-full bg-white text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500" on:click={()=>{img_selected['selected']=false; prompt=gen.caption; image_search();}}>
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
                                <path fill-rule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clip-rule="evenodd" />
                            </svg>      
                        </button>
                      </div>
                      <ul role="list" class="w-full max-w-fit grid grid-cols-4 gap-x-4 gap-y-8 sm:gap-x-6 xl:gap-x-8">
                      
                      {#each gen.generatedImgs as img}
                        <li class="relative">
                          <div class="group aspect-w-10 aspect-h-7 block overflow-hidden rounded-lg bg-gray-100 focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 focus-within:ring-offset-gray-100">
                            <img src="{img.thumb}" alt="" class="pointer-events-none object-cover group-hover:opacity-75">
                            <button type="button" class="absolute inset-0 focus:outline-none">
                              <span class="sr-only">View details for IMG_4985.HEIC</span>
                            </button>
                          </div>
                          <!-- <p class="pointer-events-none mt-2 block truncate text-sm font-medium text-gray-900">IMG_4985.HEIC</p> -->
                          <!-- <p class="pointer-events-none block text-sm font-medium text-gray-500">3.9 MB</p> -->
                        </li>
                      {/each}
                      </ul>
                      
                      <ul role="list" class="w-full max-w-fit grid grid-cols-4 gap-x-4 gap-y-8 sm:gap-x-6 xl:gap-x-8">
                      {#each Array(gen.ing_gen_num * 2) as _, i}
                      <li class="relative animate-pulse">
                        <div class="justify-center items-center bg-gray-300 rounded dark:bg-gray-700 group aspect-w-10 aspect-h-10 block overflow-hidden rounded-lg bg-gray-100">
                            <svg class="text-gray-200" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" fill="currentColor"></svg>
                        </div>
                      </li>
                      {/each}
                      </ul>

                      <!-- Generation Options -->
                      {#if !gen.editing}
                      <div class="relative mt-4">
                        <div class="absolute inset-0 flex items-center" aria-hidden="true">
                          <div class="w-full border-t border-gray-300"></div>
                        </div>
                        <div class="relative flex justify-center">
                          <span class="isolate inline-flex -space-x-px rounded-md shadow-sm">

                            <button type="button" on:click={()=>gen.more()} disabled='{gen.ing_gen_num > 0}' class="relative inline-flex items-center rounded-l-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium leading-5 text-gray-400 hover:bg-gray-50 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500">
                                <span class="sr-only">More</span>
                                <!-- Heroicon name: plus -->
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 20" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                                </svg>
                            </button>

                            <button type="button" on:click={()=>{new_prompt=gen.caption;gen.editing=true;}} disabled='{gen.ing_gen_num > 0}' class="relative inline-flex items-center rounded-r-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium leading-5 text-gray-400 hover:bg-gray-50 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500">
                                <span class="sr-only">Edit</span>
                                <!-- Heroicon name: mini/pencil -->
                                <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                    <path d="M2.695 14.763l-1.262 3.154a.5.5 0 00.65.65l3.155-1.262a4 4 0 001.343-.885L17.5 5.5a2.121 2.121 0 00-3-3L3.58 13.42a4 4 0 00-.885 1.343z" />
                                </svg>
                            </button>

                          </span>
                        </div>
                      </div>
                      {/if}
                      <!-- Generation Options Ends -->

                      <!-- Prompt Editor -->
                      {#if gen.editing}
                      <div class="mx-auto max-w-3xl mt-4 transform divide-y divide-gray-100 overflow-hidden rounded-xl bg-white shadow-2xl ring-1 ring-black ring-opacity-5 transition-all">
                        <div class="relative">
                          <!-- Heroicon name: mini/magnifying-glass -->
                          <svg class="pointer-events-none absolute top-3.5 left-4 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M14.25 6.087c0-.355.186-.676.401-.959.221-.29.349-.634.349-1.003 0-1.036-1.007-1.875-2.25-1.875s-2.25.84-2.25 1.875c0 .369.128.713.349 1.003.215.283.401.604.401.959v0a.64.64 0 01-.657.643 48.39 48.39 0 01-4.163-.3c.186 1.613.293 3.25.315 4.907a.656.656 0 01-.658.663v0c-.355 0-.676-.186-.959-.401a1.647 1.647 0 00-1.003-.349c-1.036 0-1.875 1.007-1.875 2.25s.84 2.25 1.875 2.25c.369 0 .713-.128 1.003-.349.283-.215.604-.401.959-.401v0c.31 0 .555.26.532.57a48.039 48.039 0 01-.642 5.056c1.518.19 3.058.309 4.616.354a.64.64 0 00.657-.643v0c0-.355-.186-.676-.401-.959a1.647 1.647 0 01-.349-1.003c0-1.035 1.008-1.875 2.25-1.875 1.243 0 2.25.84 2.25 1.875 0 .369-.128.713-.349 1.003-.215.283-.4.604-.4.959v0c0 .333.277.599.61.58a48.1 48.1 0 005.427-.63 48.05 48.05 0 00.582-4.717.532.532 0 00-.533-.57v0c-.355 0-.676.186-.959.401-.29.221-.634.349-1.003.349-1.035 0-1.875-1.007-1.875-2.25s.84-2.25 1.875-2.25c.37 0 .713.128 1.003.349.283.215.604.401.96.401v0a.656.656 0 00.658-.663 48.422 48.422 0 00-.37-5.36c-1.886.342-3.81.574-5.766.689a.578.578 0 01-.61-.58v0z" />
                          </svg>

                          <input type="text" bind:value={new_prompt} on:change={()=>{karlo_generation_new(gen)}} class="h-12 w-full border-0 bg-transparent pl-11 pr-4 text-gray-800 placeholder-gray-400 focus:ring-0 sm:text-sm" placeholder="Prompt to generate image..." role="combobox" aria-expanded="false" aria-controls="options">

                          <div class="absolute inset-y-0 right-0 flex py-1.5 pr-1.5">
                            <kbd class="inline-flex items-center rounded border border-gray-200 px-2 font-sans text-sm font-medium text-gray-400">↵</kbd>
                          </div>
                        </div>
                      </div>
                      {/if}
                      <!-- Prompt Editor Ends -->

                      {/each}

                      

                    </div>
                    <div>
                      <h3 class="font-medium text-gray-900">Variations</h3>
                      <ul role="list" class="w-full max-w-fit grid grid-cols-4 gap-x-4 gap-y-8 sm:gap-x-6 xl:gap-x-8">
                        
                        {#each img_selected.variations as variation}
                        <li class="relative">
                          <div class="group aspect-w-10 aspect-h-10 block overflow-hidden rounded-lg bg-gray-100 focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 focus-within:ring-offset-gray-100">
                            <img src="{variation.thumb}" alt="" class="pointer-events-none object-cover group-hover:opacity-75">
                            <button type="button" class="absolute inset-0 focus:outline-none">
                              <span class="sr-only">View details for IMG_4985.HEIC</span>
                            </button>
                          </div>
                        </li>
                        {/each}
                        {#each Array(ing_var_num) as _, i}
                        <li class="relative animate-pulse">
                            <div class="justify-center items-center bg-gray-300 rounded dark:bg-gray-700 group aspect-w-10 aspect-h-10 block overflow-hidden rounded-lg bg-gray-100">
                                <svg class="text-gray-200" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" fill="currentColor"></svg>
                            </div>
                        </li>
                        {/each}
                      
                      </ul>

                      <!-- Variation More Button -->
                      <div class="relative mt-4">
                        <div class="absolute inset-0 flex items-center" aria-hidden="true">
                          <div class="w-full border-t border-gray-300"></div>
                        </div>
                        <div class="relative flex justify-center">
                          <button type="button" on:click={()=>{karlo_variation(img_selected['id'], undefined)}} disabled='{ing_var_num>0}' class="inline-flex items-center rounded-lg border border-gray-300 bg-white px-4 py-1.5 text-sm font-medium leading-5 text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                            <!-- Heroicon name: mini/plus -->
                            <svg class="-ml-1.5 mr-1 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                              <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
                            </svg>
                            <span>More</span>
                          </button>
                        </div>
                      </div>
                      <!-- Variation More Button Ends -->
                    </div>

                    <!-- <div class="flex">
                      <button type="button" class="flex-1 rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Download</button>
                      <button type="button" class="ml-3 flex-1 rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">Delete</button>
                    </div> -->
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
    </div>
    {/if}


    {#if status == SearchStatus.DONE}
    <div class="flex">
        <main class="flex flex-row mx-auto">
            {#each Array(num_col) as _, col_i (col_i)}
            <div class="flex flex-1 flex-col overflow-hidden">
            {#each images.filter((v, i, arr) => {return i % num_col == col_i}) as img, index (index)}
            <div class="flex flex-col overflow-hidden rounded-lg mx-1 my-1 group {img_selected.id == img.id ? 'ring-2 ring-gray-300 ring-offset-1' : ''}">
                <!-- svelte-ignore a11y-click-events-have-key-events -->
                <img class="h-full w-full object-center object-cover group-hover:opacity-75" src="{img.thumb}" alt="{img.title}" id="{img.id}" on:click={click_img(img.id)}>
            </div>
            {/each}

            </div>
            {/each}
        </main>

        <!-- <div class="mx-auto grid max-w-lg gap-5 lg:max-w-none lg:grid-cols-3 {img_thumbs[0] ? 'visible' : 'collapse'} py-4 px-4 sm:py-6 sm:px-6 lg:px-8">
            <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" on:click={handleAddImage}>
            Load More .. 
            </button>
            <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded" on:click={karlo_generation}>
                Generate ..
            </button>
        </div> -->

    </div>
    <!-- 페이지에 대한 추가 Action 리스트 -->
    <div class="relative">
        <div class="absolute inset-0 flex items-center" aria-hidden="true">
        <div class="w-full border-t border-gray-300"></div>
        </div>
        <div class="relative flex justify-center">
        <span class="isolate inline-flex -space-x-px rounded-md shadow-sm">

            <button type="button" class="relative inline-flex items-center rounded-l-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-400 hover:bg-gray-50 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500">
            <span class="sr-only">Draw More</span>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
                <path d="M5.433 13.917l1.262-3.155A4 4 0 017.58 9.42l6.92-6.918a2.121 2.121 0 013 3l-6.92 6.918c-.383.383-.84.685-1.343.886l-3.154 1.262a.5.5 0 01-.65-.65z" />
                <path d="M3.5 5.75c0-.69.56-1.25 1.25-1.25H10A.75.75 0 0010 3H4.75A2.75 2.75 0 002 5.75v9.5A2.75 2.75 0 004.75 18h9.5A2.75 2.75 0 0017 15.25V10a.75.75 0 00-1.5 0v5.25c0 .69-.56 1.25-1.25 1.25h-9.5c-.69 0-1.25-.56-1.25-1.25v-9.5z" />
            </svg>
              
            </button>
            
        </span>
        </div>
    </div>
    {/if}

</div>


