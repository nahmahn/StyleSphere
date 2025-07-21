
#  StyleSphere - Your AI Fashion Universe

StyleSphere is a state-of-the-art multimodal AI-powered fashion assistant and virtual try-on engine. It blends cutting-edge computer vision, natural language understanding, and retrieval-augmented generation to redefine the fashion shopping and customization experience.

---
## Demo 
- https://youtu.be/Cubr62y-uS4
- https://youtu.be/0bOf6Q3-YWw
  
##  Core Modules Overview

### 1.  Virtual Try-On Engine (HR-VITON + CBAM)
<br>VTON OUTPUT LINK:-https://drive.google.com/file/d/1YvKs7Fe__dFkOpAqQRJ5YtjecSsrwOzp/view?usp=drive_link</br>
Model Checkpoints:-https://drive.google.com/drive/folders/16TuKl3-vgtnLhyMu5OpwLPIsvL30XHrS?usp=drive_link
- **Core Model**: HR-VITON for realistic try-on at 1024×768 resolution.
- **Architecture**: 
  - GMM (Geometric Matching Module) for cloth warping.
  - SPADE-based generator for image synthesis.
- **Enhancement**: CBAM (Convolutional Block Attention Module) added to generator’s ResBlocks.
- **Why CBAM?** Focuses attention on fabric folds, textures, edges — reduces background interference.
- **Fine-Tuning**: Only CBAM layers are tuned to reduce training time and preserve stability.

---

### 2.  Region-Specific Evaluation Framework
- **Problem**: Global metrics (SSIM, LPIPS) don’t reflect clothing quality well.
- **Solution**:
  - Human Parsing with SCHP.
  - Binary mask generation: clothing vs. non-clothing.
  - Compute:
    - SSIM/LPIPS for clothing region.
    - SSIM/LPIPS for identity preservation.
  - CLIP-based evaluation: Embedding similarity between generated and ground truth images.

---

### 3.  Custom Texture Overlay Module
- **Goal**: Apply any fabric texture (floral, denim) onto a garment.
- **Input**: Garment image, binary mask, user-chosen pattern.
- **Method**:
  - Extract luminance from original for lighting/folds.
  - Blend with texture for realism.
  - Soft blending to retain shading/depth.
- **Use Cases**: Fashion prototyping, fabric visualization, user customization.

---

### 4.  Sleeve Length Editing
- **Motivation**: Fine-grained sleeve control (e.g., convert short to long sleeves).
- **Pipeline**:
  - Parse arms with SegFormer.
  - Use Stable Diffusion inpainting with prompt ("add long sleeves").
- **Limitations**: Occasional artifacts; mitigated by fine-tuning diffusion.

---

### 5.  Clothes Extractor (Try-Off Module + GAN)
- **Objective**: Extract garment (like a t-shirt) from a user-worn photo.
- **Steps**:
  - Predict cloth mask using SCSE-enhanced U-Net.
  - Feed image + mask to ResNet-18 GAN.
  - Losses: L1 + SSIM + LPIPS + Feature Matching.
- **Output**: Standalone product image.
- **Limitations**: Struggles with small prints/logos.
<br>https://drive.google.com/drive/folders/1EtKPcDtMyzW-RDJz3ceCtb9TRU9xX6kz<br>
---

### 6.  StyleRAG - Multimodal Fashion Assistant
- **Purpose**: Conversational assistant for fashion queries using text + images.
- **Components**:
  - **Data Ingestion**: BLIP captions, OCR text, tags.
  - **Storage**: CLIP embeddings stored in Pinecone.
  - **Agents**:
    - `fashion_search`: Multimodal retrieval (image + text).
    - `fashion_knowledge`: LLaMA3-70B for deep Q&A.
    - `chit_chat`: Friendly conversation via LLaMA3-8B.
  - **Orchestrator**: Routes queries to correct agent based on type.

---

### 7.  StyleSphere Pro – Fashion Similarity Search Engine
- **Backend**:
  - **Framework**: Flask.
  - **Search Engine**: Pinecone for ANN vector search.
  - **Model**: CLIP (ViT-B/32) for text-image embedding.
- **Frontend**:
  - Text-based real-time search (with debounce).
  - Category & tag-based filters.
  - Product grid + hover previews (person-view).
- **Applications**: Fashion discovery, visual search, e-commerce integration.

---

##  Tech Stack

| Layer       | Tools/Libraries                             |
|-------------|---------------------------------------------|
| Backend     | Flask, Pinecone, sentence-transformers      |
| Frontend    | HTML/CSS, JavaScript, Chart.js              |
| Models      | HR-VITON, CBAM, CLIP, BLIP, SCHP, U-Net, SD |
| Embeddings  | CLIP (ViT-B/32)                             |
| Storage     | Pinecone Vector DB                          |
| Evaluation  | SSIM, LPIPS, CLIP Similarity                |

---

##  Features

- High-resolution virtual try-on
- Semantic similarity-based fashion search
- Texture customizer for user-provided fabrics
- AI-powered sleeve length editor
- Try-off module to extract product from person image
- Multimodal AI assistant for fashion Q&A
- Real-time clothing search with filters

---

### Contributors
- nahmahn Naman Jain
- ghostiee-11 Aman Kumar
- Prisha8 Prisha Gulati
