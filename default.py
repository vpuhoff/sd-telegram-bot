import webuiapi

generation_params_hq = {
            "steps": 65,
            "enable_hr": True,
            "hr_scale": 1.5,
            "hr_upscaler": webuiapi.HiResUpscaler.Latent,
            "hr_second_pass_steps": 0,
            "hr_resize_x": 754,
            "hr_resize_y": 1009,
            "denoising_strength": 0.7
        }

generation_params_low = {
            "prompt": "style of Ilya Kuvshinov",
            "negative_prompt": "ugly",
            "seed": -1,
            "width": 520,
            "height": 696,
            "styles": [],
            "cfg_scale": 6,
            "sampler_index": 'UniPC',
            "steps": 35,
            "enable_hr": False,
            "hr_scale": 1.5,
            "hr_upscaler": webuiapi.HiResUpscaler.Latent,
            "hr_second_pass_steps": 0,
            "hr_resize_x": 754,
            "hr_resize_y": 1009,
            "denoising_strength": 0.7
        }

generation_params = generation_params_low