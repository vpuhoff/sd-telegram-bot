import webuiapi

generation_params_hq = {
            "prompt": "style of Ilya Kuvshinov",
            "negative_prompt": "ugly",
            "seed": -1,
            "width": 640,
            "height": 480,
            "styles": [],
            "cfg_scale": 5,
            "sampler_index": 'Euler a',
            "steps": 50,
            "enable_hr": True,
            "hr_scale": 1.5,
            "hr_upscaler": webuiapi.HiResUpscaler.ESRGAN_4x,
            "hr_second_pass_steps": 0,
            "hr_resize_x": 1000,
            "hr_resize_y": 800,
            "denoising_strength": 0.6
        }

generation_params_low = {
            "prompt": "style of Ilya Kuvshinov",
            "negative_prompt": "ugly",
            "seed": -1,
            "width": 128,
            "height": 128,
            "styles": [],
            "cfg_scale": 5,
            "sampler_index": 'Euler a',
            "steps": 25,
            "enable_hr": True,
            "hr_scale": 1.5,
            "hr_upscaler": webuiapi.HiResUpscaler.ESRGAN_4x,
            "hr_second_pass_steps": 0,
            "hr_resize_x": 256,
            "hr_resize_y": 256,
            "denoising_strength": 0.6
        }

generation_params = generation_params_low