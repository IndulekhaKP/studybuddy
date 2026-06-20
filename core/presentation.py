import json

def generate_html_slides(slides_data: list[dict]) -> str:
    """Generates a standalone, beautifully styled HTML/CSS/JS presentation.
    
    Args:
        slides_data: A list of dicts like: [{"title": "...", "points": ["...", "..."]}]
    """
    slides_json = json.dumps(slides_data)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StudyBuddy Quick-Learning Presentation</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0b0f19;
            --text-color: #f3f4f6;
            --accent-color: #8b5cf6;
            --secondary-accent: #06b6d4;
            --card-bg: rgba(255, 255, 255, 0.05);
            --card-border: rgba(255, 255, 255, 0.1);
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'Outfit', sans-serif;
            background: linear-gradient(135deg, #0b0f19 0%, #111827 100%);
            color: var(--text-color);
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            overflow: hidden;
        }}
        
        .slides-container {{
            position: relative;
            width: 80%;
            max-width: 900px;
            height: 500px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        
        .slide {{
            position: absolute;
            width: 100%;
            height: 100%;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            backdrop-filter: blur(12px);
            padding: 40px;
            opacity: 0;
            transform: scale(0.95);
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            pointer-events: none;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }}
        
        .slide.active {{
            opacity: 1;
            transform: scale(1);
            pointer-events: auto;
            z-index: 10;
        }}
        
        .slide-title {{
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(90deg, var(--accent-color) 0%, var(--secondary-accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 25px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 15px;
        }}
        
        .slide-content {{
            font-size: 1.25rem;
            line-height: 1.8;
            font-weight: 300;
        }}
        
        .slide-content ul {{
            list-style: none;
        }}
        
        .slide-content li {{
            margin-bottom: 15px;
            position: relative;
            padding-left: 30px;
        }}
        
        .slide-content li::before {{
            content: "✦";
            position: absolute;
            left: 0;
            color: var(--secondary-accent);
            font-weight: 800;
        }}
        
        .controls {{
            margin-top: 30px;
            display: flex;
            align-items: center;
            gap: 20px;
            z-index: 100;
        }}
        
        .btn {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--card-border);
            color: var(--text-color);
            padding: 12px 24px;
            font-family: 'Outfit', sans-serif;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 9999px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .btn:hover {{
            background: var(--accent-color);
            border-color: var(--accent-color);
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(139, 92, 246, 0.3);
        }}
        
        .slide-number {{
            font-size: 1.1rem;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.5);
        }}
        
        .logo {{
            position: absolute;
            top: 30px;
            left: 40px;
            font-size: 1.5rem;
            font-weight: 800;
            background: linear-gradient(90deg, var(--accent-color) 0%, var(--secondary-accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .instruction {{
            position: absolute;
            bottom: 30px;
            font-size: 0.85rem;
            color: rgba(255, 255, 255, 0.3);
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="logo">🎓 StudyBuddy</div>
    
    <div class="slides-container" id="slides-wrapper">
        <!-- Slides will be inserted here dynamically -->
    </div>
    
    <div class="controls">
        <button class="btn" id="prev-btn">◀ Previous</button>
        <span class="slide-number" id="slide-counter">1 / 5</span>
        <button class="btn" id="next-btn">Next ▶</button>
    </div>
    
    <div class="instruction">Use Left/Right arrow keys or click the buttons to navigate.</div>

    <script>
        const slidesData = {slides_json};
        const wrapper = document.getElementById("slides-wrapper");
        const prevBtn = document.getElementById("prev-btn");
        const nextBtn = document.getElementById("next-btn");
        const counter = document.getElementById("slide-counter");
        
        let currentSlide = 0;
        
        // Generate Slides HTML
        slidesData.forEach((slide, index) => {{
            const slideEl = document.createElement("div");
            slideEl.className = `slide ${{index === 0 ? 'active' : ''}}`;
            
            let pointsHtml = "";
            if (Array.isArray(slide.points)) {{
                pointsHtml = "<ul>" + slide.points.map(p => `<li>${{p}}</li>`).join("") + "</ul>";
            }} else if (slide.content) {{
                pointsHtml = `<p>${slide.content}</p>`;
            }}
            
            slideEl.innerHTML = `
                <h2 class="slide-title">${slide.title}</h2>
                <div class="slide-content">${pointsHtml}</div>
            `;
            wrapper.appendChild(slideEl);
        }});
        
        const slides = document.querySelectorAll(".slide");
        
        function updateSlides() {{
            slides.forEach((slide, index) => {{
                if (index === currentSlide) {{
                    slide.classList.add("active");
                }} else {{
                    slide.classList.remove("active");
                }}
            }});
            counter.innerText = `${currentSlide + 1} / ${slides.length}`;
        }}
        
        prevBtn.addEventListener("click", () => {{
            if (currentSlide > 0) {{
                currentSlide--;
                updateSlides();
            }}
        }});
        
        nextBtn.addEventListener("click", () => {{
            if (currentSlide < slides.length - 1) {{
                currentSlide++;
                updateSlides();
            }}
        }});
        
        document.addEventListener("keydown", (e) => {{
            if (e.key === "ArrowLeft") {{
                if (currentSlide > 0) {{
                    currentSlide--;
                    updateSlides();
                }}
            }} else if (e.key === "ArrowRight") {{
                if (currentSlide < slides.length - 1) {{
                    currentSlide++;
                    updateSlides();
                }}
            }}
        }});
        
        updateSlides();
    </script>
</body>
</html>"""
    return html
