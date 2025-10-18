import streamlit as st
import requests
import time
import os

st.title("Higgsfield Multimodal Generator")

option = st.selectbox("Choose generation type", ["Text to Image", "Text to Video", "Image to Video"])


headers = {
    "hf-api-key": st.secrets.get("HF_API_KEY", "93b61826-44b8-427e-addd-9744bfda8d32"),
    "hf-secret": st.secrets.get("HF_SECRET", "a39ac8a8a3e77de51946842692e413a9f5f646e6fa36579e76acd5bd21e8cc7b"),
    "Content-Type": "application/json"
}

def poll_job(job_id, result_type):
    result_url = f"https://cloud.higgsfield.ai/v1/job-sets/{job_id}" 
    with st.spinner("Generating..."):
        while True:
            res = requests.get(result_url, headers=headers)
            if res.status_code != 200:
                st.error(f"Error polling job: {res.status_code} - {res.text}")
                break
            data = res.json()
            status = data.get('status')
            if status == 'completed':
                url = data['result']['url']
                if result_type == 'image':
                    st.image(url)
                elif result_type == 'video':
                    st.video(url)
                break
            elif status == 'failed':
                st.error(f"Generation failed: {data.get('error', 'Unknown error')}")
                break
            time.sleep(3) 


if option == "Text to Image":
    prompt = st.text_input("Enter prompt for image")
    if st.button("Generate Image"):
        url = "https://cloud.higgsfield.ai/v1/text2image/nano-banana"  
        data = {"prompt": prompt}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            job_id = response.json()['id']
            st.write(f"Job ID: {job_id}")
            poll_job(job_id, 'image')
        else:
            st.error(f"Failed to start generation: {response.status_code} - {response.text}")

# === Text to Video ===
elif option == "Text to Video":
    prompt = st.text_input("Enter prompt for video")
    if st.button("Generate Video"):
        url = "https://cloud.higgsfield.ai/v1/generate/minimax-t2v" 
        data = {"prompt": prompt}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            job_id = response.json()['id']
            st.write(f"Job ID: {job_id}")
            poll_job(job_id, 'video')
        else:
            st.error(f"Failed to start generation: {response.status_code} - {response.text}")


elif option == "Image to Video":
    st.write("Upload your image to imgur.com (free), copy the direct image URL (ending in .jpg/.png), and paste below.")
    image_url = st.text_input("Image URL (must be direct link)")
    prompt = st.text_input("Optional prompt for video")
    if image_url and st.button("Generate Video from Image"):
        url = "https://cloud.higgsfield.ai/v1/generate/kling-2-5" 
        data = {
            "image": image_url,
            "prompt": prompt or ""
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            job_id = response.json()['id']
            st.write(f"Job ID: {job_id}")
            poll_job(job_id, 'video')
        else:
            st.error(f"Failed to start generation: {response.status_code} - {response.text}")
