import streamlit as st
import requests
import time
import base64

st.title("Higgsfield Multimodal Generator")

option = st.selectbox("Choose generation type", ["Text to Image", "Text to Video", "Image to Video"])

headers = {
    "hf-api-key": "93b61826-44b8-427e-addd-9744bfda8d32",
    "hf-secret": "a39ac8a8a3e77de51946842692e413a9f5f646e6fa36579e76acd5bd21e8cc7b",
    "Content-Type": "application/json"
}

def poll_job(job_id, result_type):
    result_url = f"https://platform.higgsfield.ai/v1/job-sets/{job_id}"
    with st.spinner("Generating..."):
        while True:
            res = requests.get(result_url, headers=headers)
            if res.status_code != 200:
                st.error("Error polling job")
                break
            status = res.json()['status']
            if status == 'completed':
                url = res.json()['result']['url']
                if result_type == 'image':
                    st.image(url)
                elif result_type == 'video':
                    st.video(url)
                break
            elif status == 'failed':
                st.error("Generation failed")
                break
            time.sleep(2)

if option == "Text to Image":
    prompt = st.text_input("Enter prompt for image")
    if st.button("Generate Image"):
        url = "https://platform.higgsfield.ai/v1/models/nano-banana/generations"
        data = {"params": {"prompt": prompt}}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            job_id = response.json()['id']
            st.write(f"Job ID: {job_id}")
            poll_job(job_id, 'image')
        else:
            st.error("Failed to start generation")

elif option == "Text to Video":
    prompt = st.text_input("Enter prompt for video")
    if st.button("Generate Video"):
        url = "https://platform.higgsfield.ai/v1/models/kling-21-master-t2v/generations"
        data = {"params": {"prompt": prompt}}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            job_id = response.json()['id']
            st.write(f"Job ID: {job_id}")
            poll_job(job_id, 'video')
        else:
            st.error("Failed to start generation")

elif option == "Image to Video":
    uploaded_file = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
    if uploaded_file and st.button("Generate Video from Image"):
        # Encode image to base64 for API (assuming API accepts base64 or URL; adjust if needed)
        image_data = base64.b64encode(uploaded_file.read()).decode()
        url = "https://platform.higgsfield.ai/v1/models/kling-2-5/generations"  # Example i2v model
        data = {"params": {"image": f"data:image/png;base64,{image_data}"}}  # Adjust based on API docs
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            job_id = response.json()['id']
            st.write(f"Job ID: {job_id}")
            poll_job(job_id, 'video')
        else:
            st.error("Failed to start generation")
