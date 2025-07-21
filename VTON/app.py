
import cv2
import numpy as np
import streamlit as st
from PIL import Image
import os
import subprocess
import time


# --- Pattern Application Logic ---
def apply_pattern_to_cloth(cloth_path, pattern_path, mask_path, output_path):
    cloth = cv2.imread(cloth_path)
    pattern = cv2.imread(pattern_path)
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if cloth is None or pattern is None or mask is None:
        raise ValueError(f"Could not load one or more input images for pattern application.\nCloth: {cloth_path}\nPattern: {pattern_path}\nMask: {mask_path}")
    # Resize pattern
    pattern_resized = cv2.resize(pattern, (cloth.shape[1], cloth.shape[0]), interpolation=cv2.INTER_CUBIC)
    # Ensure mask is binary
    mask_bin = (mask > 127).astype(np.uint8) * 255
    # Convert cloth to grayscale for luminance
    cloth_gray = cv2.cvtColor(cloth, cv2.COLOR_BGR2GRAY)
    cloth_gray_3c = cv2.cvtColor(cloth_gray, cv2.COLOR_GRAY2BGR)
    luminance = cloth_gray_3c.astype(np.float32)
    luminance = luminance / (luminance.max() + 1e-5)
    pattern_float = pattern_resized.astype(np.float32) / 255.0
    patterned = pattern_float * luminance
    alpha = 0.7
    patterned = patterned * alpha + pattern_float * (1 - alpha)
    patterned_uint8 = np.clip(patterned * 255, 0, 255).astype(np.uint8)
    mask_3c = cv2.merge([mask_bin]*3)
    inv_mask_3c = cv2.bitwise_not(mask_3c)
    cloth_bg = cv2.bitwise_and(cloth, inv_mask_3c)
    cloth_fg = cv2.bitwise_and(patterned_uint8, mask_3c)
    result = cv2.add(cloth_bg, cloth_fg)
    cv2.imwrite(output_path, result)
    return output_path

# Directories
PERSON_DIR = 'data/test/image'
CLOTH_DIR = 'data/test/cloth'
CLOTH_MASK_DIR = 'data/test/cloth-mask'
PATTERN_DIR = 'styles'
OUTPUT_DIR = 'output/streamlit_results'
TEMP_PATTERNED_CLOTH_DIR = 'output/patterned_cloth'
SINGLE_PAIR_FILE = 'data/single_pair.txt'

# Ensure output and temp directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_PATTERNED_CLOTH_DIR, exist_ok=True)

# List available images and patterns
person_images = sorted([f for f in os.listdir(PERSON_DIR) if f.endswith('.jpg') or f.endswith('.png')])
cloth_images = sorted([f for f in os.listdir(CLOTH_DIR) if f.endswith('.jpg') or f.endswith('.png')])
pattern_images = sorted([f for f in os.listdir(PATTERN_DIR) if f.lower().endswith('.jpg') or f.lower().endswith('.png')])



# --- Sidebar ---
st.sidebar.title('HR-VITON Try-On Demo')
st.sidebar.markdown('Select a person and a clothing image. Optionally, apply a new fabric pattern.')
person_img_name = st.sidebar.selectbox('Select Person Image', person_images)
cloth_img_name = st.sidebar.selectbox('Select Cloth Image', cloth_images)
apply_pattern = st.sidebar.checkbox('Apply new fabric pattern?', value=True)
if apply_pattern:
    pattern_img_name = st.sidebar.selectbox('Select Fabric Pattern', pattern_images)


# --- Main Title and Description ---
st.title('👗 HR-VITON Virtual Try-On')
st.markdown('''
Upload a person and a clothing image from the test set to see the virtual try-on result. Powered by HR-VITON.
''')

# --- Show Input Images in Columns ---
st.subheader('Selected Images')
if apply_pattern:
    col1, col2, col3 = st.columns(3)
else:
    col1, col2 = st.columns(2)
with col1:
    st.image(os.path.join(PERSON_DIR, person_img_name), caption=f'Person: {person_img_name}', width=256)
with col2:
    st.image(os.path.join(CLOTH_DIR, cloth_img_name), caption=f'Cloth: {cloth_img_name}', width=256)
if apply_pattern:
    with col3:
        # Generate and show the patterned cloth preview
        cloth_path = os.path.join(CLOTH_DIR, cloth_img_name)
        mask_path = os.path.join(CLOTH_MASK_DIR, cloth_img_name)
        pattern_path = os.path.join(PATTERN_DIR, pattern_img_name)
        patterned_cloth_name = f"patterned_{os.path.splitext(cloth_img_name)[0]}_{os.path.splitext(pattern_img_name)[0]}.jpg"
        patterned_cloth_path = os.path.join(TEMP_PATTERNED_CLOTH_DIR, patterned_cloth_name)
        try:
            if not os.path.exists(patterned_cloth_path):
                apply_pattern_to_cloth(cloth_path, pattern_path, mask_path, patterned_cloth_path)
            st.image(patterned_cloth_path, caption='Patterned Cloth Preview', width=256)
        except Exception as e:
            st.warning(f'Patterned cloth preview unavailable: {e}')



def run_viton_inference(person_img_name, cloth_img_name, pattern_img_name=None, apply_pattern=True):
    import shutil
    if apply_pattern and pattern_img_name is not None:
        # 1. Generate patterned cloth (mask path always from original cloth)
        cloth_path = os.path.join(CLOTH_DIR, cloth_img_name)
        mask_path = os.path.join(CLOTH_MASK_DIR, cloth_img_name)
        pattern_path = os.path.join(PATTERN_DIR, pattern_img_name)
        patterned_cloth_name = f"patterned_{os.path.splitext(cloth_img_name)[0]}_{os.path.splitext(pattern_img_name)[0]}.jpg"
        patterned_cloth_path = os.path.join(TEMP_PATTERNED_CLOTH_DIR, patterned_cloth_name)
        apply_pattern_to_cloth(cloth_path, pattern_path, mask_path, patterned_cloth_path)
        # 2. Write single pair file in data/
        with open(SINGLE_PAIR_FILE, 'w') as f:
            f.write(f'{person_img_name} {os.path.basename(patterned_cloth_path)}\n')
        # 3. Copy patterned cloth to data/test/cloth for inference
        dest_cloth_path = os.path.join(CLOTH_DIR, os.path.basename(patterned_cloth_path))
        shutil.copy(patterned_cloth_path, dest_cloth_path)
        # 3b. Copy the original mask to data/test/cloth-mask with the new patterned cloth name
        dest_mask_path = os.path.join(CLOTH_MASK_DIR, os.path.basename(patterned_cloth_path))
        shutil.copy(mask_path, dest_mask_path)
        # 4. Prepare output subdir for this pair
        pair_id = f"{os.path.splitext(person_img_name)[0]}_{os.path.splitext(cloth_img_name)[0]}_{os.path.splitext(pattern_img_name)[0]}"
        pair_output_dir = os.path.join(OUTPUT_DIR, pair_id)
        os.makedirs(pair_output_dir, exist_ok=True)
        # 5. Call test_generator.py with this pair and correct checkpoint paths
        cmd = [
            'python', 'test_generator.py',
            '--data_list', 'single_pair.txt',
            '--output_dir', pair_output_dir,
            '--dataroot', 'data',
            '--datamode', 'test',
            '--batch-size', '1',
            '--cuda', 'False',
            '--tocg_checkpoint', 'checkpoints/mtviton.pth',
            '--gen_checkpoint', 'checkpoints/gen.pth'
        ]
        subprocess.run(cmd, check=True)
        # 6. Find the output image
        result_img_path = os.path.join(pair_output_dir, f'{os.path.splitext(person_img_name)[0]}_{os.path.splitext(os.path.basename(patterned_cloth_path))[0]}.png')
        return result_img_path
    else:
        # Use original cloth and mask, no pattern applied
        with open(SINGLE_PAIR_FILE, 'w') as f:
            f.write(f'{person_img_name} {cloth_img_name}\n')
        pair_id = f"{os.path.splitext(person_img_name)[0]}_{os.path.splitext(cloth_img_name)[0]}_original"
        pair_output_dir = os.path.join(OUTPUT_DIR, pair_id)
        os.makedirs(pair_output_dir, exist_ok=True)
        cmd = [
            'python', 'test_generator.py',
            '--data_list', 'single_pair.txt',
            '--output_dir', pair_output_dir,
            '--dataroot', 'data',
            '--datamode', 'test',
            '--batch-size', '1',
            '--cuda', 'False',
            '--tocg_checkpoint', 'checkpoints/mtviton.pth',
            '--gen_checkpoint', 'checkpoints/gen.pth'
        ]
        subprocess.run(cmd, check=True)
        result_img_path = os.path.join(pair_output_dir, f'{os.path.splitext(person_img_name)[0]}_{os.path.splitext(cloth_img_name)[0]}.png')
        return result_img_path

# --- Run Inference Button ---
if st.button('✨ Run Virtual Try-On'):
    with st.spinner('Running virtual try-on inference. This may take a few seconds...'):
        try:
            if apply_pattern:
                result_img_path = run_viton_inference(person_img_name, cloth_img_name, pattern_img_name, apply_pattern=True)
            else:
                result_img_path = run_viton_inference(person_img_name, cloth_img_name, None, apply_pattern=False)
            st.success('Inference complete! See the result below.')
            st.subheader('Virtual Try-On Result')
            st.image(result_img_path, caption='Try-On Result', width=300)
        except Exception as e:
            st.error(f'Error during inference: {e}')

# --- Footer ---
st.markdown('---')