import webuiapi

generation_params_hq = {
    "steps": 65,
    "enable_hr": True,
    "hr_scale": 1.5,
    "hr_upscaler": webuiapi.HiResUpscaler.Latent,
    "hr_second_pass_steps": 0,
    "hr_resize_x": 754,
    "hr_resize_y": 1009,
    "denoising_strength": 0.7,
}

generation_params_low = {
    "prompt": "style of Ilya Kuvshinov",
    "negative_prompt": "ugly,nude,",
    "seed": -1,
    "width": 520,
    "height": 696,
    "styles": [],
    "cfg_scale": 6,
    "sampler_index": "UniPC",
    "steps": 50,
    "enable_hr": False,
    "hr_scale": 1.5,
    "hr_upscaler": webuiapi.HiResUpscaler.Latent,
    "hr_second_pass_steps": 0,
    "hr_resize_x": 754,
    "hr_resize_y": 1009,
    "denoising_strength": 0.7,
}

generation_params_img2img = {
    "denoising_strength": 0.65,
    "image_cfg_scale": 1.5,
    "mask_blur": 4,
    "inpainting_fill": 0,
    "inpaint_full_res": True,
    "inpaint_full_res_padding": 0,
    "inpainting_mask_invert": 0,
    "initial_noise_multiplier": 0.7,
    "sampler_name": "Euler a",
    "steps": None,
    "cfg_scale": 7.0,
}
generation_params = generation_params_low
