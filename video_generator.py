"""
video_generator.py
A Python application that uses the Gemini API to generate images, compile them into videos using MMPG, and handle video splitting and mixing.
Author: DaveDDev
"""

import os
import requests
import subprocess
from typing import List

# ========== CONFIG ==========
API_KEY = os.getenv('GEMINI_API_KEY') or "YOUR_GEMINI_API_KEY"
GEMINI_ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'
MMPG_PATH = 'mmpg'  # Ensure mmpg (https://github.com/DaveDDev/mmpg) is installed and in PATH

# ========== GEMINI IMAGE GENERATION ==========
def gen_image(prompt: str, out_path: str):
    """Generate an image using Gemini API and save it as out_path."""
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
    }
    params = {"key": API_KEY}
    resp = requests.post(GEMINI_ENDPOINT, params=params, json=data, headers=headers)
    resp.raise_for_status()
    img_data = resp.json()['candidates'][0]['content']['parts'][0].get('inlineData', {}).get('data', None)
    if img_data is None:
        raise Exception("No image data returned!")
    with open(out_path, "wb") as f:
        f.write(bytes(img_data, 'utf-8'))
    print(f"Saved image to {out_path}")

# ========== VIDEO COMPILATION USING MMPG ==========
def images_to_video(image_files: List[str], output_video: str, fps: int = 30):
    """Compile images into a video using MMPG."""
    cmd = [MMPG_PATH, "-i"] + image_files + ["-o", output_video, "-f", str(fps)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"MMPG failed: {result.stderr}")
    print(f"Video saved to {output_video}")

# ========== VIDEO SPLITTING ==========
def split_video(input_video: str, segment_length: int, out_pattern: str):
    """Split a video into segments of a given length (in seconds) using ffmpeg."""
    cmd = ["ffmpeg", "-i", input_video, "-c", "copy", "-map", "0", "-segment_time", str(segment_length), "-f", "segment", out_pattern]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"ffmpeg split failed: {result.stderr}")
    print(f"Video split into segments: {out_pattern}")

# ========== VIDEO MIXING ==========
def mix_videos(input_videos: List[str], output_video: str):
    """Mix multiple videos together side by side using ffmpeg."""
    cmd = ["ffmpeg", "-i"] + input_videos + ["-filter_complex", f"hstack=inputs={len(input_videos)}", output_video]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"ffmpeg mix failed: {result.stderr}")
    print(f"Mixed video saved to {output_video}")

# ========== USAGE EXAMPLES ==========
if __name__ == "__main__":
    # Example 1: Generate images
    prompts = ["A fantasy castle at sunset", "A futuristic cityscape"]
    img_files = []
    for i, prompt in enumerate(prompts):
        img_path = f"image_{i+1}.png"
        # Uncomment the next line to generate images
        # gen_image(prompt, img_path)
        img_files.append(img_path)

    # Example 2: Compile images to video
    # images_to_video(img_files, "output_video.mp4")

    # Example 3: Split video into 5-sec segments
    # split_video("output_video.mp4", 5, "segment_%03d.mp4")

    # Example 4: Mix videos side by side
    # mix_videos(["segment_001.mp4", "segment_002.mp4"], "mixed_output.mp4")
