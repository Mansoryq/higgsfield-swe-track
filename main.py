import streamlit as st
import requests
import time

st.title("Higgsfield Multimodal Generator")

option = st.selectbox("Choose generation type", ["Text to Image", "Text to Video", "Image to Video"])


HF_API_KEY = "93b61826-44b8-427e-addd-9744bfda8d32"
HF_SECRET = "a39ac8a8a3e77de51946842692e413a9f5f646e6fa36579e76acd5bd21e8cc7b"

headers = {
    "hf-api-key": HF_API_KEY,
    "hf-secret": HF_SECRET,
    "Content-Type": "application/json"
}

def poll_job(job_id, result_type):
    result_url = f"https://cloud.higgsfield.ai/v1/job-sets/{job_id}"
    with st.spinner("Generating..."):
        while True:
            res = requests.get(result_url, headers=headers)
            if res.status_code != 200:
                st.error(f"Polling failed: {res.status_code} – {res.text}")
                return
            data = res.json()
            status = data.get("status")
            if status == "completed":
                url = data["result"]["url"]
                if result_type == "image":
                    st.image(url)
                elif result_type == "video":
                    st.video(url)
                return
            elif status == "failed":
                error_msg = data.get("error", "Unknown error")
                st.error(f"Generation failed: {error_msg}")
                return
            time.sleep(3)


GENERATION_URL = "https://cloud.higgsfield.ai/v1/generations"


if option == "Text to Image":
    prompt = st.text_input("Enter prompt for image")
    if st.button("Generate Image"):
        payload = {
            "model": "black-forest-labs/flux-1.1-pro",  
            "params": {"prompt": prompt}
        }
        response = requests.post(GENERATION_URL, headers=headers, json=payload)
        if response.status_code == 200:
            job_id = response.json()["id"]
            st.write(f"Job ID: {job_id}")
            poll_job(job_id, "image")
        else:
            st.error(f"Failed to start: {response.status_code} – {response.text}")


elif option == "Text to Video":
    prompt = st.text_input("Enter prompt for video")
    if st.button("Generate Video"):
        payload = {
            "model": "minimax-t2v", 
            "params": {"prompt": prompt}
        }
        response = requests.post(GENERATION_URL, headers=headers, json=payload)
        if response.status_code == 200:
            job_id = response.json()["id"]
            st.write(f"Job ID: {job_id}")
            poll_job(job_id, "video")
        else:
            st.error(f"Failed to start: {response.status_code} – {response.text}")


elif option == "Image to Video":
    st.write("Upload image to imgur.com, get direct link (e.g., https://i.imgur.com/xyz.jpg)")
    image_url = st.text_input("Direct image URL")
    prompt = st.text_input("Optional prompt")
    if image_url and st.button("Generate Video"):
        payload = {
            "model": "kling-2-5",
            "params": {
                "image": image_url,
                "prompt": prompt or ""
            }
        }
        response = requests.post(GENERATION_URL, headers=headers, json=payload)
        if response.status_code == 200:
            job_id = response.json()["id"]
            st.write(f"Job ID: {job_id}")
            poll_job(job_id, "video")
        else:
            st.error(f"Failed to start: {response.status_code} – {response.text}")
