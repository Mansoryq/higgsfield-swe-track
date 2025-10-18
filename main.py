import streamlit as st
import requests
import time

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
                st.error(f"Error polling job: {res.text}")
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
        url = "https://platform.higgsfield.ai/v1/text2image/soul"
        payload = {
            "params": {
                "prompt": prompt,
                "width_and_height": "1152x2048",
                "enhance_prompt": False,
                "style_id": "464ea177-8d40-4940-8d9d-b438bab269c7",
                "style_strength": 1,
                "quality": "1080p",
                "seed": 500000,
                "batch_size": 1
            }
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            job_id = response.json()['id']
            st.write(f"Job ID: {job_id}")
            poll_job(job_id, 'image')
        else:
            st.error(f"Failed to start generation: {response.status_code} - {response.text}")

elif option == "Text to Video":
    prompt = st.text_input("Enter prompt for video")
    if st.button("Generate Video"):
        url = "https://cloud.higgsfield.ai/v1/models/kling-21-master-t2v/generations"
        data = {"params": {"prompt": prompt}}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            job_id = response.json()['id']
            st.write(f"Job ID: {job_id}")
            poll_job(job_id, 'video')
        else:
            st.error(f"Failed to start generation: {response.status_code} - {response.text}")

elif option == "Image to Video":
    motions_response = requests.get("https://platform.higgsfield.ai/v1/motions", headers=headers)
    if motions_response.status_code == 200:
        motions = motions_response.json() 
        motion_options = [motion['id'] for motion in motions] if motions else []
        selected_motion = st.selectbox("Select motion", motion_options)
    else:
        st.error("Failed to load motions")
        selected_motion = None
    
    st.write("Загрузи изображение на imgur.com (бесплатно), скопируй URL и вставь ниже.")
    image_url = st.text_input("Image URL from imgur")
    if selected_motion and image_url and st.button("Generate Video from Image"):
        url = "https://platform.higgsfield.ai/v1/motions"
        payload = {
            "motion_id": selected_motion,
            "params": {
                "image": image_url
            }
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            job_id = response.json()['id']
            st.write(f"Job ID: {job_id}")
            poll_job(job_id, 'video')
        else:
            st.error(f"Failed to start generation: {response.status_code} - {response.text}")
