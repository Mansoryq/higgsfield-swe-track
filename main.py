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
        url = "https://platform.higgsfield.ai/v1/generations"
        data = {"model": "nano-banana", "params": {"prompt": prompt}}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            job_id = response.json()['id']
            st.write(f"Job ID: {job_id}")
            poll_job(job_id, 'image')
        else:
            st.error(f"Failed to start generation: {response.status_code} - {response.text}")

elif option == "Text to Video":
    prompt = st.text_input("Enter prompt for video")
    if st.button("Generate Video"):
        url = "https://platform.higgsfield.ai/v1/generations"
        data = {"model": "kling-21-master-t2v", "params": {"prompt": prompt}}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            job_id = response.json()['id']
            st.write(f"Job ID: {job_id}")
            poll_job(job_id, 'video')
        else:
            st.error(f"Failed to start generation: {response.status_code} - {response.text}")

elif option == "Image to Video":
    uploaded_file = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
    prompt = st.text_input("Optional prompt for video")
    if uploaded_file and st.button("Generate Video from Image"):
        # Для демо, предполагаем, что API ожидает image_url. Если base64, измени на {"image": f"data:image/png;base64,{image_data}"}
        # Но обычно для i2v нужен URL, так что загрузи изображение куда-то (например, imgur) или используй API upload.
        st.error("Для Image to Video нужен image_url. Загрузи изображение на внешний сервис (например, imgur.com) и вставь URL ниже.")
        image_url = st.text_input("Image URL")
        if image_url:
            url = "https://platform.higgsfield.ai/v1/generations"
            data = {"model": "kling-2-5", "params": {"image": image_url, "prompt": prompt or ""}}
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                job_id = response.json()['id']
                st.write(f"Job ID: {job_id}")
                poll_job(job_id, 'video')
            else:
                st.error(f"Failed to start generation: {response.status_code} - {response.text}")
