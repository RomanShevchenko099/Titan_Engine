import os, json, re, asyncio, subprocess, torch, edge_tts, random, time
from openai import OpenAI
from diffusers import FluxPipeline
from huggingface_hub import login
import config


class TitanEngine:
    def __init__(self):
        login(token=config.HF_TOKEN)
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=config.OR_KEY)
        self.pipe = None
        self.flux_semaphore = asyncio.Semaphore(1)

    def load_flux(self):
        if self.pipe is None:
            self.pipe = FluxPipeline.from_pretrained(
                config.VIDEO_CONFIG["model_flux"],
                torch_dtype=torch.bfloat16
            ).to("cuda")

    async def generate_script(self, topic, num_scenes, style):
        prompt = (
            f"Topic: {topic}. Style: {style}. Return ONLY a JSON array with {num_scenes} elements. "
            "Format:. "
            "No markdown, no comments, just raw JSON."
        )

        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, lambda: self.client.chat.completions.create(
            model=config.VIDEO_CONFIG["model_llm"],
            messages=[{"role": "user", "content": prompt}]
        ))

        content = res.choices[0].message.content.strip()
        # Очистка від можливих ```json ... ```
        content = re.sub(r'```json|```', '', content)
        return json.loads(content)

    async def render_ffmpeg(self, visual, audio, output, text, is_video):
        w, h = config.VIDEO_CONFIG["width"], config.VIDEO_CONFIG["height"]
        v_filter = (f"scale=iw*2:-1,zoompan=z='pzoom+0.001':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=125:s={w}x{h}"
                    if not is_video else f"scale={w}:{h},setsar=1")

        clean_text = text.replace("'", "").replace(":", "")
        drawtext = (f"drawtext=text='{clean_text}':fontfile={config.VIDEO_CONFIG['font_path']}:"
                    f"fontsize=40:fontcolor=white:box=1:boxcolor=black@0.6:x=(w-text_w)/2:y=h-100")

        input_cmd = ["-loop", "1", "-i", visual] if not is_video else ["-i", visual]
        cmd = ["ffmpeg", "-y"] + input_cmd + [
            "-i", audio, "-vf", f"{v_filter},{drawtext}",
            "-c:v", "h264_nvenc", "-preset", "p4", "-c:a", "aac", "-shortest", "-pix_fmt", "yuv420p", output
        ]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        await proc.communicate()

    async def process_scene(self, i, scene_data, style):
        img_p = os.path.join(config.OUT_DIR, f"{i}.png")
        aud_p = os.path.join(config.OUT_DIR, f"{i}.mp3")
        vid_p = os.path.join(config.SCENES_DIR, f"s_{i}.mp4")

        await edge_tts.Communicate(scene_data["text"], config.VIDEO_CONFIG["voice"]).save(aud_p)

        async with self.flux_semaphore:
            self.load_flux()
            full_p = f"{scene_data['prompt']}, {style} style, high quality"
            img = self.pipe(full_p, num_inference_steps=4, guidance_scale=0.0).images[0]
            img.save(img_p)

        await self.render_ffmpeg(img_p, aud_p, vid_p, scene_data["text"], False)
        return vid_p

    async def run_workflow(self, topic, num_scenes, style):
        script = await self.generate_script(topic, num_scenes, style)
        tasks = [self.process_scene(i, s, style) for i, s in enumerate(script)]
        scene_files = await asyncio.gather(*tasks)

        list_txt = os.path.join(config.OUT_DIR, "list.txt")
        with open(list_txt, "w") as f:
            for s in sorted(scene_files): f.write(f"file '{s}'\n")

        final_out = os.path.join(config.BASE_PATH, f"result_{int(time.time())}.mp4")
        subprocess.run(f"ffmpeg -y -f concat -safe 0 -i {list_txt} -c copy {final_out}", shell=True)
        return final_out