import webuiapi

generation_params_hq = {
    "steps": 45,
    "enable_hr": True,
    "hr_scale": 2,
    "hr_upscaler": "4x_foolhardy_Remacri",
    "hr_second_pass_steps": 0,
    "denoising_strength": 0.4,
}

generation_params_low = {
    "prompt": "ultra realistic, high quality",
    #"negative_prompt": "ugly,nude, naked, poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, (deformed, distorted, disfigured:1.3), floating limbs, (mutated hands and fingers:1.4), disconnected limbs, mutation, mutated, ugly, disgusting, blurry, amputation, frames, borderline, text, character, duplicate, error, out of frame, watermark, low quality, ugly, deformed, blur  bad-artist",
    "negative_prompt": "bad hands, text, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, jpeg artifacts, signature, watermark, username, blurry, artist name, ((extra fingers)), ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((bad anatomy)), (((bad proportions))), ((extra limbs)), glitchy, ((extra hands)), ((mangled fingers)), ((deformed eyes)), 3hands, (half-turn pose), ((((game)))), ((((strategy))))), ((((3d)))), ((((lying)))), ugly,nude, naked, poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, (deformed, distorted, disfigured:1.3), floating limbs, (mutated hands and fingers:1.4), disconnected limbs, mutation, mutated, ugly, disgusting, blurry, amputation, frames, borderline, text, character, duplicate, error, out of frame, watermark, low quality, ugly, deformed, blur  bad-artist",
    "seed": -1,
    "width": 520,
    "height": 696,
    "styles": [],
    "cfg_scale": 6,
    "sampler_index": "Euler a",
    "steps": 35,
    "enable_hr": True,
    "hr_scale": 2,
    "hr_upscaler": "4x-UltraSharp",
    "hr_second_pass_steps": 0,
    "denoising_strength": 0.4,
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
