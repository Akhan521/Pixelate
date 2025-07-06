# ![pixelate-logo](https://github.com/user-attachments/assets/406abdbe-6fc0-496f-95fd-e087c12b16ca) Pixelate: An Inclusive Pixel-Art Platform for All Creators

Built by: [Aamir Khan](https://github.com/Akhan521), [Abdi Nava](https://github.com/abdinava), [Alexis Manalastas](https://github.com/amana032)


## 🎨 What is Pixelate?

Pixelate is an inclusive pixel-art sprite editor, designed to help colorblind artists create art through its thoughtful, accessibility features. Existing image editing tools on the market do not offer tailored support for color-vision deficienct users, which make up more than 300 million people worldwide. Pixelate addresses this issue by offering tools such as an AI conversational assistant, smart color-vision filters, and color-approximation tools tailored to the three most common types of colorblindness: protanopia, deuteranopia, and tritanopia. Additionally, we foster community engagement through our custom gallery feature. It is with great pleasure and enthusiasm that we introduce to you, Pixelate!

---

## 💭 Why We Built Pixelate

Most art tools today are not designed with accessibility in mind, especially for artists who experience color vision deficiencies (CVD). Over 300 million people worldwide live with some form of colorblindness, and yet creative tools rarely offer built-in support.

**Pixelate** was born out of our desire to change that. We wanted to build something that empowered *every* artist to express themselves, regardless of how they see color.

Our project combines empathy-driven design, technical implementation, and real-time AI assistance to deliver an inclusive pixel-art experience, where accessibility isn't an afterthought but a core feature.

---

## 🧠 What We Learned

Throughout this project, we took on multiple technical and design challenges. Here's what we gained:

### 🔧 Full-Stack Development
- Designed and implemented a desktop GUI using **PyQt6** with custom canvas tools
- Integrated **Firebase (Firestore + Auth)** for secure login and persistent gallery storage
- Used local storage and `.pix` custom format for fast, user-friendly saving/loading

### 🎨 Inclusive Design
- Researched and implemented **real-time smart filters** for Protanopia, Deuteranopia, and Tritanopia
- Built a **color approximation tool** that clearly affirms what colors are being used, for greater artistic confidence
- Crafted UI components to ensure contrast and usability for all users

### 🤖 AI Integration
- Designed an **AI Assistant (Pixi)** that helps users generate pixel-art ideas and troubleshoot common questions
- Built a natural, conversational interface using prompts tailored for artists

### 📸 UX & Community
- Developed a **custom gallery** where users can upload and share their work
- Implemented real-time **like/unlike features**, tracked by user account
- Focused on making the app feel fun, encouraging, and easy to use for all skill levels

---

## 🚀 Features at a Glance

| Feature | Description |
|--------|-------------|
| 🖌️ Pixel Editor | Draw and edit pixel art in a responsive canvas |
| 🧠 AI Assistant | Chat with Pixi, your AI assistant, to get drawing ideas or help |
| 🌍 Colorblind Filters | Modify how your art looks for better color distinguishability |
| 🎯 Color Approximator | Approximates colors used with great accuracy |
| 💾 Custom Format | Save your art as a `.pix` file with color metadata |
| 🖼️ Public Gallery | Upload, view, like, and share pixel art with others |
| 🔐 Secure Login | Firebase Authentication with persistent sessions |

---

## 🌟 Pixelate in Action

<div align="center">
  <img src="https://github.com/user-attachments/assets/7d0299c8-23b5-4cd5-a4c8-55c83b1935f1" alt="Pixelate Demo" width="80%">
</div>

---

## 🛠 Installation & Usage

You can run Pixelate locally on your machine by following these simple steps:

### ✅ Prerequisites
- **Python 3.8 or higher**  
  → [Download Python](https://www.python.org/downloads/)
- **Git** 
  → [Download Git](https://git-scm.com/)

---

### 💻 Setup Instructions

0. **Open Your Terminal**  
   - On **Windows**: Search for "PowerShell" or "Command Prompt" in the Start Menu.
   - On **macOS/Linux**: Use the Terminal app from Launchpad or Spotlight.

1. **Clone The Repository**
   ```bash
   git clone https://github.com/Akhan521/Pixelate.git
   cd Pixelate
   ```

2. Create A Virtual Environment + Activate It:
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3. Install Dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run The App:
    ```bash
    python app/main.py
    ```

5. 🎉 That’s it! Pixelate should launch, and you’re ready to start creating accessible pixel art!

---

## 📁 Project Structure
```bash
📁 Pixelate/
├── app/                            # Main PyQt6 application
│   ├── canvas/                     # Drawing canvas, color tools, sprite creation
│   ├── gallery/                    # Upload, manage, and display public pixel art
│   ├── pixi_ai/                    # AI assistant and image generation logic
│   ├── tools/                      # Colorblind filters and helper utilities
│   └── user_auth/                  # User login, registration, auth dialogs
│
├── backend/                        # FastAPI backend server
│   └── auth/                       # Firebase user and storage logic (auth, firestore, uploads)
│
├── fonts/                          # Custom pixel font(s) for UI
├── icons/                          # UI icons and asset graphics
```

---

## 💡 Reflections

This project was about building with purpose. From the very beginning, not only did we ask ourselves *“how can we make pixel art?”* but more importantly, *“who are we making it for?”*.

Pixelate challenged us to think beyond just features and functionality:

- **How does accessibility shape design?**
- **How can we ensure people with color vision deficiencies feel seen and supported?**
- **How do you keep interfaces inclusive without adding complexity?**
- **How can we use AI to assist without overwhelming?**

These questions guided every design decision, from the smart color-vision filters to our AI assistant and custom gallery. We learned that **great design isn't just smart, it's empathetic.**

Along the way, we leveled up our technical skills in:
- End-to-End full-stack development with PyQt6 and FastAPI
- Real-time filtering and image processing
- Firebase integration for authentication and cloud sync
- Designing modular systems and scalable architecture
- Integrating AI in ways that feel human and helpful

But the biggest win wasn’t technical, it was learning how to **build for others**. We’re proud of what we created, and even prouder of the intention, thoughtfulness, and inclusivity we poured into every line of code.

---

## 👥 Get to Know Us

- **Aamir Khan**  
  💼 [LinkedIn](https://www.linkedin.com/in/aamir-khan-aak521/) | 💻 [GitHub](https://github.com/Akhan521) | 🌐 [Portfolio](https://aamir-khans-portfolio.vercel.app/)

- **Abdi Nava**  
  💼 [LinkedIn](https://www.linkedin.com/in/abdinava/) | 💻 [GitHub](https://github.com/abdinava)

- **Alexis Manalastas**  
  💻 [GitHub](https://github.com/amana032)

---

## ⭐ Support Us

If you found this project helpful, interesting, or inspiring, feel free to ⭐ the repository! 

We’d love to hear your feedback or ideas, so reach out anytime!


