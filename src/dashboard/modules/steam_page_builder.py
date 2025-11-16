"""
Steam Page Builder Module
Helps users design the perfect Steam store page with best practices and live preview.
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import re
from pathlib import Path
from datetime import datetime


def convert_markdown_to_html(markdown_text):
    """Convert basic Markdown to HTML for Steam page display."""
    if not markdown_text:
        return ''
    
    html = markdown_text
    
    # Convert headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Convert bold text
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    # Convert italic text
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # Convert bullet points (both • and - style)
    lines = html.split('\n')
    converted_lines = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        # Check for bullet points with • or -
        if stripped.startswith('• ') or stripped.startswith('â€¢ ') or (stripped.startswith('- ') and not stripped.startswith('--')):
            if not in_list:
                converted_lines.append('<ul>')
                in_list = True
            # Remove bullet and wrap in <li>
            item_text = re.sub(r'^[•â€¢\-]\s+', '', stripped)
            converted_lines.append(f'<li>{item_text}</li>')
        else:
            if in_list:
                converted_lines.append('</ul>')
                in_list = False
            if stripped:
                # Wrap non-empty lines in <p> tags if they're not already HTML tags
                if not stripped.startswith('<'):
                    converted_lines.append(f'<p>{stripped}</p>')
                else:
                    converted_lines.append(stripped)
            else:
                converted_lines.append('')
    
    if in_list:
        converted_lines.append('</ul>')
    
    html = '\n'.join(converted_lines)
    
    return html


# Steam Asset Requirements
STEAM_ASSET_REQUIREMENTS = {
    "Header Capsule": {
        "size": "920px × 430px",
        "required": True,
        "usage": "Top of store page, 'Recommended For You', Daily Deals",
        "best_practices": [
            "Use key art and logo from marketing materials",
            "Logo must be clearly legible",
            "No quotes or text beyond game title",
            "Graphically-centric, convey gameplay essence"
        ],
        "common_mistakes": [
            "Logo too small or hard to read",
            "Too much text",
            "Doesn't match game's art style",
            "Generic or stock imagery"
        ]
    },
    "Small Capsule": {
        "size": "462px × 174px",
        "required": True,
        "usage": "Search results, top-sellers, new releases lists",
        "best_practices": [
            "Logo should nearly fill the capsule",
            "Must be legible at smallest size (120×45)",
            "Focus on brand recognition",
            "Can differ from other capsules"
        ],
        "common_mistakes": [
            "Logo too small to read in lists",
            "Too much detail that gets lost",
            "Inconsistent with main branding"
        ]
    },
    "Main Capsule": {
        "size": "1232px × 706px",
        "required": True,
        "usage": "Store home page main carousel",
        "best_practices": [
            "Use signature key art",
            "Clear, bold logo placement",
            "Show what makes game unique",
            "Match retail/marketing materials"
        ],
        "common_mistakes": [
            "Too busy or cluttered",
            "Logo gets lost in background",
            "Doesn't tell what game is about"
        ]
    },
    "Vertical Capsule": {
        "size": "748px × 896px",
        "required": True,
        "usage": "Featured on front page during sales",
        "best_practices": [
            "Vertical composition works well",
            "Logo clearly visible",
            "Strong visual hierarchy"
        ],
        "common_mistakes": [
            "Just cropped horizontal art",
            "Poor use of vertical space"
        ]
    },
    "Screenshots": {
        "size": "1920px × 1080px minimum (16:9)",
        "required": True,
        "quantity": "Minimum 5",
        "usage": "Store page screenshot gallery",
        "best_practices": [
            "Show ACTUAL gameplay only",
            "Include UI to show how game plays",
            "High resolution, widescreen",
            "Mark 4+ as 'suitable for all ages'",
            "Show variety of gameplay",
            "Capture exciting moments"
        ],
        "common_mistakes": [
            "Concept art instead of gameplay",
            "Pre-rendered cinematics",
            "Marketing copy on images",
            "Awards or text overlays",
            "Menu screens (unless unique)",
            "Low quality or wrong aspect ratio"
        ]
    },
    "Page Background": {
        "size": "1438px × 810px",
        "required": False,
        "usage": "Store page background",
        "best_practices": [
            "Subtle, ambient artwork",
            "Not too bright or busy",
            "Complements page content"
        ],
        "common_mistakes": [
            "Too bright, competes with content",
            "Distracting animations"
        ]
    }
}

# Description Best Practices
DESCRIPTION_BEST_PRACTICES = {
    "Short Description": {
        "limit": "300 characters",
        "best_practices": [
            "Hook players immediately",
            "One sentence that sells the game",
            "Include genre + unique selling point",
            "Make it quotable for streamers"
        ],
        "examples_good": [
            "Build, survive, and thrive in a zombie apocalypse where every decision matters",
            "A roguelike deckbuilder where you'll die a lot, but laugh even more"
        ],
        "examples_bad": [
            "This is a game about...",
            "Join millions of players...",
            "Amazing graphics and gameplay!"
        ]
    },
    "Long Description": {
        "best_practices": [
            "Use visual editor for formatting",
            "Start with core gameplay loop",
            "Bullet points for features",
            "Include GIFs showing gameplay",
            "End with call to action",
            "NO links to other websites",
            "NO fake Steam UI buttons",
            "NO links to other Steam games"
        ],
        "structure": [
            "1. Opening hook (2-3 sentences)",
            "2. Core gameplay explanation",
            "3. Key features (bulleted)",
            "4. Unique selling points",
            "5. What players will love",
            "6. Call to action (wishlist/buy)"
        ],
        "common_mistakes": [
            "Wall of text, no formatting",
            "Too long, loses attention",
            "Generic marketing speak",
            "Comparing to other games",
            "External links",
            "Fake UI elements"
        ]
    }
}

# Chris Zukowski Best Practices (from research)
CHRIS_ZUKOWSKI_TIPS = {
    "Capsule Art": [
        "Your logo is MORE important than your art",
        "Players see capsules for 0.5 seconds - make it count",
        "Test capsule at smallest size first",
        "Avoid purple/blue (most common colors)",
        "Show genre through art style",
        "Don't put review scores on capsules"
    ],
    "Screenshots": [
        "First screenshot is most important",
        "Show your best feature first",
        "Gameplay > beauty",
        "No HUD-less screenshots",
        "Show what makes you different"
    ],
    "Description": [
        "First 3 lines appear above fold - hook here",
        "Use bold, italics, headers for scanning",
        "Players don't read, they scan",
        "Show, don't tell (use GIFs)",
        "Address player concerns directly"
    ],
    "Tags": [
        "Use all 20 tags",
        "Put most important tags first",
        "Mix genre + feature + theme tags",
        "Tags help discoverability"
    ],
    "Video": [
        "First 10 seconds are critical",
        "Start with gameplay, not logos",
        "Keep it under 90 seconds",
        "Show core loop clearly"
    ]
}


def show_steam_page_builder():
    """Main Steam Page Builder interface."""
    st.header("🎨 Steam Page Builder")
    st.markdown("*Design the perfect Steam store page with expert guidance*")
    
    # Initialize projects list in session state
    if 'steam_page_projects' not in st.session_state:
        st.session_state.steam_page_projects = load_all_projects()
    
    if 'current_project_id' not in st.session_state:
        st.session_state.current_project_id = None
    
    # Project Management Section
    show_project_manager()
    
    # Only show editor if a project is selected
    if st.session_state.current_project_id:
        st.markdown("---")
        show_project_editor()
    else:
        st.info("👆 Select or create a project to start designing your Steam page")


def show_project_manager():
    """Project selection and management interface."""
    st.markdown("### 📁 Your Steam Page Projects")
    
    projects = st.session_state.steam_page_projects
    
    if projects:
        # Display projects table
        st.markdown("**Existing Projects:**")
        
        project_data = []
        for proj_id, proj in projects.items():
            project_data.append({
                "Game": proj['game_name'],
                "Variation": proj['variation_name'],
                "Status": proj.get('status', 'Draft'),
                "Modified": proj['modified_at'][:10],
                "ID": proj_id
            })
        
        if project_data:
            # Create a more interactive display
            for idx, proj_info in enumerate(project_data):
                col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 2])
                
                with col1:
                    st.markdown(f"**{proj_info['Game']}**")
                with col2:
                    st.markdown(f"*{proj_info['Variation']}*")
                with col3:
                    badge_color = "🟢" if proj_info['Status'] == 'Complete' else "🟡"
                    st.markdown(f"{badge_color} {proj_info['Status']}")
                with col4:
                    st.markdown(f"{proj_info['Modified']}")
                with col5:
                    col_edit, col_dup, col_del = st.columns(3)
                    with col_edit:
                        if st.button("✏️", key=f"edit_{proj_info['ID']}", 
                                    help="Edit"):
                            st.session_state.current_project_id = proj_info['ID']
                            st.rerun()
                    with col_dup:
                        if st.button("📋", key=f"dup_{proj_info['ID']}", 
                                    help="Duplicate"):
                            duplicate_project(proj_info['ID'])
                            st.rerun()
                    with col_del:
                        if st.button("🗑️", key=f"del_{proj_info['ID']}", 
                                    help="Delete"):
                            delete_project(proj_info['ID'])
                            st.rerun()
                
                st.markdown("---")
    else:
        st.info("No projects yet. Create your first Steam page!")
    
    # Create new project button
    st.markdown("### ➕ Create New Project")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        new_game_name = st.text_input(
            "Game Name",
            placeholder="e.g., Cosmic Conquest",
            key="new_game_name"
        )
    with col2:
        new_variation = st.text_input(
            "Variation Name",
            placeholder="e.g., Main Page, Holiday Theme, Free Weekend",
            value="Main Page",
            key="new_variation"
        )
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Create Project", type="primary", use_container_width=True):
            if new_game_name:
                new_proj = create_new_project(new_game_name, new_variation)
                st.session_state.steam_page_projects[new_proj['id']] = new_proj
                st.session_state.current_project_id = new_proj['id']
                save_project(new_proj)
                st.success(f"Created project: {new_game_name} - {new_variation}")
                st.rerun()
            else:
                st.error("Please enter a game name")


def show_project_editor():
    """Show editor for currently selected project."""
    project_id = st.session_state.current_project_id
    project = st.session_state.steam_page_projects.get(project_id)
    
    if not project:
        st.error("Project not found")
        return
    
    # Project header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"## {project['game_name']} - {project['variation_name']}")
    with col2:
        if st.button("← Back to Projects", use_container_width=True):
            st.session_state.current_project_id = None
            st.rerun()
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Checklist",
        "✏️ Edit Content",
        "👁️ Preview",
        "💡 Best Practices"
    ])
    
    with tab1:
        show_requirements_checklist(project)
    
    with tab2:
        show_content_editor_for_project(project)
    
    with tab3:
        show_preview_window(project)
    
    with tab4:
        show_best_practices_guide()


def init_blank_project():
    """Initialize a blank Steam page project with placeholder data."""
    import uuid
    
    project_id = str(uuid.uuid4())[:8]
    
    return {
        "id": project_id,
        "game_name": "Mystic Realms: Chronicles",
        "variation_name": "Main Page",
        "status": "Draft",
        "descriptions": {
            "short": "Embark on an epic fantasy adventure where your choices shape the fate of the realm. Build alliances, master magic, and defeat ancient evils in this open-world RPG.",
            "long": """## About This Game

Welcome to **Mystic Realms: Chronicles** - an immersive fantasy RPG where every decision matters.

### Core Gameplay
Explore a vast, living world filled with danger and wonder. Your character's journey is unique, shaped by the choices you make and the paths you take.

### Key Features
• **Dynamic Quest System** - Over 200+ hours of branching storylines
• **Deep Character Customization** - 12 classes, 50+ skills, endless builds
• **Strategic Combat** - Real-time combat with tactical pause
• **Living World** - NPCs remember your actions and react accordingly
• **Multiplayer Co-op** - Team up with friends for epic raids
• **Mod Support** - Full Steam Workshop integration

### What Players Are Saying
*"The best RPG I've played in years!"* - Hundreds of positive reviews

### Join the Adventure
Wishlist now and be among the first to explore Mystic Realms!"""
        },
        "tags": [
            "RPG", "Fantasy", "Open World", "Singleplayer", "Multiplayer",
            "Co-op", "Story Rich", "Character Customization", "Magic",
            "Adventure", "Action", "Third-Person", "Atmospheric",
            "Choices Matter", "Exploration"
        ],
        "price": "$29.99",
        "release_date": "Q2 2026",
        "developer": "Epic Game Studios",
        "publisher": "Epic Game Studios",
        "assets": {
            "header_capsule": "header_920x430.png",
            "small_capsule": "small_462x174.png",
            "main_capsule": "main_1232x706.png",
            "vertical_capsule": "vertical_748x896.png",
            "screenshots": [
                "screenshot_1_combat.png",
                "screenshot_2_exploration.png",
                "screenshot_3_magic.png",
                "screenshot_4_city.png",
                "screenshot_5_boss_fight.png"
            ],
            "trailer_url": "https://youtu.be/example"
        },
        "features": [
            "Massive open world spanning 50+ unique regions",
            "Choice-driven narrative with multiple endings",
            "Deep character progression with 12 unique classes",
            "Real-time tactical combat system",
            "Online co-op for up to 4 players",
            "Full mod support via Steam Workshop",
            "Rich lore with 100+ in-game books and artifacts"
        ],
        "system_requirements": {
            "minimum": "Windows 10, 8GB RAM, GTX 1060",
            "recommended": "Windows 11, 16GB RAM, RTX 3060"
        },
        "created_at": datetime.now().isoformat(),
        "modified_at": datetime.now().isoformat()
    }


def create_new_project(game_name, variation_name):
    """Create a new project with the given name and variation."""
    import uuid
    
    project = init_blank_project()
    project['id'] = str(uuid.uuid4())[:8]
    project['game_name'] = game_name
    project['variation_name'] = variation_name
    project['status'] = "Draft"
    project['created_at'] = datetime.now().isoformat()
    project['modified_at'] = datetime.now().isoformat()
    
    return project


def duplicate_project(project_id):
    """Duplicate an existing project as a new variation."""
    import uuid
    
    original = st.session_state.steam_page_projects.get(project_id)
    if not original:
        return
    
    # Create a copy
    new_project = original.copy()
    new_project['id'] = str(uuid.uuid4())[:8]
    new_project['variation_name'] = f"{original['variation_name']} (Copy)"
    new_project['created_at'] = datetime.now().isoformat()
    new_project['modified_at'] = datetime.now().isoformat()
    
    st.session_state.steam_page_projects[new_project['id']] = new_project
    save_project(new_project)
    st.success(f"Duplicated: {new_project['game_name']} - {new_project['variation_name']}")


def delete_project(project_id):
    """Delete a project."""
    if project_id in st.session_state.steam_page_projects:
        project = st.session_state.steam_page_projects[project_id]
        
        # Delete from file system
        projects_dir = Path("data/steam_pages")
        filename = f"steam_page_{project_id}.json"
        filepath = projects_dir / filename
        
        if filepath.exists():
            filepath.unlink()
        
        # Remove from session
        del st.session_state.steam_page_projects[project_id]
        
        # Clear current selection if deleted
        if st.session_state.current_project_id == project_id:
            st.session_state.current_project_id = None
        
        st.success("Project deleted")


def load_all_projects():
    """Load all projects from disk."""
    projects_dir = Path("data/steam_pages")
    projects_dir.mkdir(parents=True, exist_ok=True)
    
    projects = {}
    
    for filepath in projects_dir.glob("steam_page_*.json"):
        try:
            with open(filepath, 'r') as f:
                project = json.load(f)
                if 'id' in project:
                    projects[project['id']] = project
        except Exception as e:
            st.warning(f"Could not load {filepath.name}: {e}")
    
    return projects


def show_requirements_checklist(project):
    """Display comprehensive requirements checklist."""
    st.markdown("### 📋 Steam Asset Requirements Checklist")
    
    # Calculate completion
    total_items = len(STEAM_ASSET_REQUIREMENTS)
    completed = 0
    
    for asset_name, requirements in STEAM_ASSET_REQUIREMENTS.items():
        asset_key = asset_name.lower().replace(" ", "_")
        
        with st.expander(
            f"{'✅' if project['assets'].get(asset_key) else '❌'} "
            f"{asset_name} - {requirements['size']}"
        ):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown(f"**Required:** {'Yes' if requirements['required'] else 'Optional'}")
                st.markdown(f"**Size:** {requirements['size']}")
                st.markdown(f"**Usage:** {requirements['usage']}")
                
                if project['assets'].get(asset_key):
                    completed += 1
                    st.success(f"✓ {project['assets'][asset_key]}")
                else:
                    st.warning("⚠ Not yet uploaded")
            
            with col2:
                st.markdown("**✅ Best Practices:**")
                for tip in requirements['best_practices']:
                    st.markdown(f"• {tip}")
                
                st.markdown("**❌ Common Mistakes:**")
                for mistake in requirements['common_mistakes']:
                    st.markdown(f"• {mistake}")
    
    # Progress bar
    progress = completed / total_items
    st.progress(progress)
    st.markdown(f"**Progress:** {completed}/{total_items} required assets completed")
    
    if progress == 1.0:
        st.success("🎉 All required assets completed!")
        st.balloons()


def show_content_editor_for_project(project):
    """Content editing interface for a specific project."""
    st.markdown("### ✏️ Edit Your Steam Page Content")
    
    # Basic Info
    with st.expander("📌 Basic Information", expanded=True):
        project['game_name'] = st.text_input(
            "Game Name",
            value=project['game_name'],
            help="Your game's title",
            key=f"game_name_{project['id']}"
        )
        
        project['variation_name'] = st.text_input(
            "Variation Name",
            value=project['variation_name'],
            help="e.g., Main Page, Holiday Sale, Free Weekend",
            key=f"variation_{project['id']}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            project['developer'] = st.text_input(
                "Developer",
                value=project['developer'],
                key=f"dev_{project['id']}"
            )
        with col2:
            project['publisher'] = st.text_input(
                "Publisher",
                value=project['publisher'],
                key=f"pub_{project['id']}"
            )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            project['price'] = st.text_input(
                "Price",
                value=project['price'],
                help="e.g., $19.99, Free to Play",
                key=f"price_{project['id']}"
            )
        with col2:
            project['release_date'] = st.text_input(
                "Release Date",
                value=project['release_date'],
                help="e.g., December 2025, Coming Soon",
                key=f"release_{project['id']}"
            )
        with col3:
            project['status'] = st.selectbox(
                "Status",
                ["Draft", "Review", "Ready", "Complete"],
                index=["Draft", "Review", "Ready", "Complete"].index(project.get('status', 'Draft')),
                key=f"status_{project['id']}"
            )
    
    # Descriptions
    with st.expander("📝 Descriptions", expanded=True):
        st.markdown("#### Short Description")
        st.info("💡 This appears in search results and lists. Make it count!")
        
        char_limit = 300
        project['descriptions']['short'] = st.text_area(
            "Short Description (300 characters max)",
            value=project['descriptions']['short'],
            max_chars=char_limit,
            height=100,
            help="Hook players in one sentence",
            key=f"short_desc_{project['id']}"
        )
        
        char_count = len(project['descriptions']['short'])
        st.caption(f"{char_count}/{char_limit} characters")
        
        if char_count > 0:
            if char_count < 100:
                st.warning("⚠️ Too short - add more detail")
            elif char_count > 250:
                st.success("✓ Good length!")
        
        st.markdown("#### Long Description")
        st.info("💡 Use formatting to make it scannable.")
        
        project['descriptions']['long'] = st.text_area(
            "Long Description",
            value=project['descriptions']['long'],
            height=300,
            help="Detailed game description with formatting",
            key=f"long_desc_{project['id']}"
        )
        
        st.markdown("**Formatting Tips:**")
        st.code("""
Use headers: ## Header Text
Bold: **bold text**
Italic: *italic text*
Lists: • bullet points
        """)
    
    # Tags
    with st.expander("🏷️ Tags (Select up to 20)", expanded=False):
        st.info("💡 Tags are crucial for discoverability. Use all 20!")
        
        # Common tag categories
        tag_categories = {
            "Genre": [
                "Action", "Adventure", "RPG", "Strategy", "Simulation",
                "Puzzle", "Casual", "Racing", "Sports"
            ],
            "Features": [
                "Singleplayer", "Multiplayer", "Co-op",
                "Online Co-Op", "Local Co-Op", "PvP", "PvE"
            ],
            "Themes": [
                "Fantasy", "Sci-fi", "Horror", "Survival",
                "Open World", "Sandbox", "Story Rich"
            ],
            "Gameplay": [
                "Roguelike", "Deckbuilder", "Turn-Based",
                "Real-Time", "First-Person", "Third-Person"
            ],
            "Art Style": [
                "Pixel Art", "2D", "3D", "Stylized",
                "Realistic", "Cartoon", "Anime"
            ]
        }
        
        selected_tags = []
        for category, tags in tag_categories.items():
            st.markdown(f"**📁 {category}**")
            cols = st.columns(3)
            for idx, tag in enumerate(tags):
                with cols[idx % 3]:
                    if st.checkbox(
                        tag,
                        value=tag in project['tags'],
                        key=f"tag_{tag}_{project['id']}"
                    ):
                        selected_tags.append(tag)
            st.markdown("")  # Add spacing
        
        project['tags'] = selected_tags
        st.markdown(f"**Selected: {len(selected_tags)}/20 tags**")
        
        if len(selected_tags) < 10:
            st.warning("⚠️ Add more tags for better discoverability")
        elif len(selected_tags) >= 15:
            st.success("✓ Good tag coverage!")
    
    # Features List
    with st.expander("⭐ Key Features", expanded=False):
        st.info("💡 Bullet points that highlight your game's special features")
        
        num_features = st.number_input(
            "Number of features to showcase",
            min_value=3,
            max_value=10,
            value=len(project['features']),
            key=f"num_features_{project['id']}"
        )
        
        # Adjust features list
        while len(project['features']) < num_features:
            project['features'].append("")
        while len(project['features']) > num_features:
            project['features'].pop()
        
        for i in range(num_features):
            project['features'][i] = st.text_input(
                f"Feature {i+1}",
                value=project['features'][i],
                key=f"feature_{i}_{project['id']}",
                placeholder="e.g., Build and customize your own spaceship"
            )
    
    # Asset Upload
    with st.expander("📸 Assets", expanded=False):
        st.markdown("Track your game's visual assets")
        st.caption("Note: Enter file names to track what you need.")
        
        for asset_name, requirements in STEAM_ASSET_REQUIREMENTS.items():
            asset_key = asset_name.lower().replace(" ", "_")
            
            st.markdown(f"**{asset_name}** - {requirements['size']}")
            project['assets'][asset_key] = st.text_input(
                f"File name for {asset_name}",
                value=project['assets'].get(asset_key, ""),
                placeholder=f"e.g., {asset_key}.png",
                key=f"asset_{asset_key}_{project['id']}"
            )
            st.caption(requirements['usage'])
            st.markdown("---")
    
    # Save button
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button(
            "💾 Save Project",
            key=f"save_{project['id']}",
            type="primary",
            use_container_width=True
        ):
            save_project(project)
            st.success(f"✅ Saved '{project['game_name']}'")


def show_preview_window(project):
    """Live preview of Steam page with authentic Steam styling."""
    st.markdown("### 👁️ Steam Store Page Preview")
    st.caption("Preview of how your game page will look on Steam")
    
    # Extract project data
    game_name = project.get('game_name', 'Your Game Title')
    developer = project.get('developer', 'Developer Name')
    release_date = project.get('release_date', 'Coming Soon')
    short_desc = project.get('descriptions', {}).get('short', '')
    long_desc = project.get('descriptions', {}).get('long', '')
    tags = project.get('tags', [])
    price = project.get('price', '$XX.XX')
    
    # Build tags HTML (show first 10 in sidebar)
    tags_html = ''.join([
        f'<span class="steam-tag">{tag}</span>'
        for tag in tags[:10]
    ])
    
    # Build long description HTML - convert Markdown to HTML
    long_desc_html = convert_markdown_to_html(long_desc) if long_desc else ''
    
    # Build complete HTML content with embedded styles
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
body {{
    margin: 0;
    padding: 0;
    background-color: #1b2838;
    font-family: "Motiva Sans", Arial, Helvetica, sans-serif;
}}
.steam-preview-container {{
    background-color: #1b2838;
    color: #c6d4df;
}}
.steam-page-title {{
    font-size: 26px;
    font-weight: 300;
    color: #ffffff;
    padding: 20px 25px 10px 25px;
    margin: 0;
}}
.steam-breadcrumb {{
    font-size: 11px;
    color: #8f98a0;
    padding: 0 25px 15px 25px;
}}
    .steam-breadcrumb a {{
        color: #67c1f5;
        text-decoration: none;
    }}
    .steam-content-wrapper {{
        display: flex;
        gap: 20px;
        padding: 0 25px 25px 25px;
    }}
    .steam-left-col {{
        flex: 1;
        min-width: 0;
    }}
    .steam-right-col {{
        width: 340px;
        flex-shrink: 0;
    }}
    .steam-hero-area {{
        background: #000000;
        height: 380px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 15px;
        border-radius: 3px;
        color: #556772;
        font-size: 14px;
        flex-direction: column;
    }}
    .hero-icon {{
        font-size: 64px;
        margin-bottom: 15px;
        opacity: 0.3;
    }}
    .steam-screenshot-row {{
        display: flex;
        gap: 5px;
        margin-bottom: 20px;
        overflow-x: auto;
    }}
    .steam-screenshot-thumb {{
        width: 116px;
        height: 65px;
        background: #16202d;
        border-radius: 2px;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #556772;
        font-size: 10px;
    }}
    .steam-about-section {{
        background: rgba(0, 0, 0, 0.2);
        padding: 20px;
        border-radius: 3px;
        margin-bottom: 20px;
    }}
    .steam-section-title {{
        color: #ffffff;
        font-size: 14px;
        font-weight: 600;
        margin: 0 0 12px 0;
        text-transform: uppercase;
    }}
    .steam-about-text {{
        color: #acb2b8;
        font-size: 13px;
        line-height: 1.7;
    }}
    .steam-sidebar-box {{
        background: rgba(0, 0, 0, 0.2);
        border-radius: 3px;
        overflow: hidden;
        margin-bottom: 15px;
    }}
    .steam-game-image-area {{
        width: 100%;
        height: 192px;
        background: #16202d;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #556772;
        font-size: 12px;
        flex-direction: column;
    }}
    .game-img-icon {{
        font-size: 48px;
        margin-bottom: 10px;
        opacity: 0.5;
    }}
    .steam-sidebar-desc {{
        padding: 15px;
        font-size: 13px;
        line-height: 1.6;
        color: #c6d4df;
        border-bottom: 1px solid rgba(0, 0, 0, 0.3);
    }}
    .steam-sidebar-features {{
        padding: 15px;
        font-size: 12px;
        color: #acb2b8;
        border-bottom: 1px solid rgba(0, 0, 0, 0.3);
    }}
    .steam-sidebar-features div {{
        margin: 8px 0;
    }}
    .steam-feature-label {{
        color: #67c1f5;
        margin-right: 8px;
    }}
    .steam-sidebar-tags {{
        padding: 15px;
        border-bottom: 1px solid rgba(0, 0, 0, 0.3);
    }}
    .steam-tag {{
        display: inline-block;
        background: rgba(103, 193, 245, 0.2);
        color: #67c1f5;
        padding: 4px 8px;
        margin: 3px 3px 3px 0;
        border-radius: 2px;
        font-size: 11px;
    }}
    .steam-purchase-box {{
        padding: 15px;
        background: rgba(0, 0, 0, 0.3);
    }}
    .steam-info-panel {{
        background: rgba(0, 0, 0, 0.2);
        border-radius: 3px;
        margin-bottom: 15px;
        padding: 15px;
    }}
    .steam-info-title {{
        color: #ffffff;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 12px;
    }}
    .steam-info-content {{
        color: #c6d4df;
        font-size: 12px;
        line-height: 1.6;
    }}
    .steam-info-item {{
        margin: 8px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .steam-info-icon {{
        color: #67c1f5;
        font-size: 14px;
    }}
    .language-table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 8px;
    }}
    .language-table th {{
        text-align: left;
        color: #8f98a0;
        font-size: 11px;
        font-weight: 500;
        padding: 6px 8px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }}
    .language-table td {{
        color: #c6d4df;
        font-size: 12px;
        padding: 6px 8px;
    }}
    .language-table tr:hover {{
        background: rgba(103, 193, 245, 0.05);
    }}
    .checkmark {{
        color: #67c1f5;
    }}
    .steam-price {{
        background: #000000;
        color: #c7d5e0;
        padding: 10px 15px;
        font-size: 18px;
        display: inline-block;
        border-radius: 2px;
        margin-bottom: 10px;
    }}
    .steam-buy-button {{
        background: #5c7e10;
        color: #d2e885;
        padding: 12px;
        text-align: center;
        border-radius: 2px;
        font-size: 14px;
        font-weight: 500;
    }}

    /* System Requirements */
    .system-req-tabs {{
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
    }}
    .sys-tab {{
        background: rgba(0, 0, 0, 0.3);
        padding: 8px 16px;
        border-radius: 3px;
        color: #c6d4df;
        font-size: 13px;
        cursor: pointer;
    }}
    .sys-tab.active {{
        background: #67c1f5;
        color: #1b2838;
    }}
    .sys-req-content {{
        color: #acb2b8;
        font-size: 12px;
        line-height: 1.8;
    }}
    .sys-req-label {{
        color: #c6d4df;
        font-weight: 600;
    }}

    /* Reviews section */
    .steam-reviews-section {{
        background: rgba(0, 0, 0, 0.2);
        padding: 20px;
        border-radius: 3px;
        margin-bottom: 20px;
    }}
    .review-score {{
        color: #66c0f4;
        font-size: 14px;
        font-weight: 600;
    }}

    /* Content section */
    .steam-content-section {{
        background: rgba(0, 0, 0, 0.2);
        padding: 20px;
        border-radius: 3px;
        margin-bottom: 20px;
    }}

    /* Buy section (large standalone) */
    .buy-section {{
        background: linear-gradient(to bottom, rgba(0,0,0,0.2) 5%, rgba(0,0,0,0.3) 95%);
        border: 1px solid #000000;
        border-radius: 4px;
        margin-bottom: 20px;
        padding: 0;
    }}
    .buy-section-title {{
        background: rgba(0,0,0,0.5);
        padding: 12px 15px;
        font-size: 14px;
        color: #ffffff;
        font-weight: 600;
        border-bottom: 1px solid #000000;
    }}
    .buy-section-content {{
        padding: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .buy-price-large {{
        font-size: 24px;
        color: #c7d5e0;
    }}
    .buy-button-large {{
        background: linear-gradient(to bottom, #799905 5%, #536904 95%);
        border: 1px solid #000000;
        color: #d2e885;
        padding: 12px 30px;
        border-radius: 2px;
        font-size: 15px;
        font-weight: 500;
        cursor: pointer;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }}
    .buy-button-large:hover {{
        background: linear-gradient(to bottom, #8bb804 5%, #678d04 95%);
    }}

    @media (max-width: 910px) {{
        .steam-content-wrapper {{
            flex-direction: column;
        }}
        .steam-right-col {{
            width: 100%;
        }}
    }}
    </style>
    </head>
    <body>
    <div class="steam-preview-container">
        <div class="steam-page-title">{game_name}</div>
        <div class="steam-breadcrumb">
            <a href="#">All Games</a> &gt;
            <a href="#">Action Games</a> &gt;
            {game_name}
        </div>
        
        <div class="steam-content-wrapper">
            <!-- LEFT COLUMN -->
            <div class="steam-left-col">
                <!-- Hero/Main Image Area -->
                <div class="steam-hero-area">
                    <div class="hero-icon">🎮</div>
                    <div>Main Game Artwork / Video (616×353)</div>
                    <div style="font-size: 11px; opacity: 0.5; margin-top: 8px;">
                        Your trailer or primary screenshot
                    </div>
                </div>
                
                <!-- Screenshot Thumbnails -->
                <div class="steam-screenshot-row">
                    <div class="steam-screenshot-thumb">📷 1</div>
                    <div class="steam-screenshot-thumb">📷 2</div>
                    <div class="steam-screenshot-thumb">📷 3</div>
                    <div class="steam-screenshot-thumb">📷 4</div>
                    <div class="steam-screenshot-thumb">📷 5</div>
                </div>
                
                <!-- Buy Section -->
                <div class="buy-section">
                    <div class="buy-section-title">Buy {game_name}</div>
                    <div class="buy-section-content">
                        <div class="buy-price-large">{price}</div>
                        <div class="buy-button-large">Add to Cart</div>
                    </div>
                </div>
                
                <!-- About This Game Section with Formatting -->
                <div class="steam-about-section">
                    <div class="steam-section-title">About This Game</div>
                    <div class="steam-about-text about-formatting">
                        {long_desc_html if long_desc_html else short_desc if short_desc else '<p><em style="opacity:0.6">Add your game description in the Edit Content tab...</em></p>'}
                    </div>
                </div>
                
                <!-- System Requirements -->
                <div class="steam-content-section">
                    <div class="steam-section-title">System Requirements</div>
                    <div class="system-req-tabs">
                        <div class="sys-tab active">Windows</div>
                        <div class="sys-tab">macOS</div>
                    </div>
                    <div class="sys-req-content">
                        <p><span class="sys-req-label">Minimum:</span></p>
                        <p><strong>OS:</strong> Windows 7 SP1<br>
                        <strong>Processor:</strong> Dual Core 2.4 GHz<br>
                        <strong>Memory:</strong> 4 GB RAM<br>
                        <strong>Graphics:</strong> 1GB VRAM / DirectX 10+ support<br>
                        <strong>Storage:</strong> 15 GB available space</p>
                        
                        <p style="margin-top:15px;"><span class="sys-req-label">Recommended:</span></p>
                        <p><strong>OS:</strong> Windows 10<br>
                        <strong>Processor:</strong> Dual Core 3.0 GHz+<br>
                        <strong>Memory:</strong> 8 GB RAM<br>
                        <strong>Graphics:</strong> 2GB VRAM / DirectX 10+ support<br>
                        <strong>Storage:</strong> 20 GB available space</p>
                    </div>
                </div>
                
                <!-- Reviews Section -->
                <div class="steam-reviews-section">
                    <div class="steam-section-title">Reviews</div>
                    <div class="review-score">Very Positive</div>
                    <p style="color:#8f98a0; font-size:12px; margin-top:5px;">
                        Based on player reviews - Add actual review data in Edit Content tab
                    </p>
                </div>
                
                <!-- Content For This Game -->
                <div class="steam-content-section">
                    <div class="steam-section-title">Content For This Game</div>
                    <p style="color:#acb2b8; font-size:13px;">
                        Browse all (0) - Add DLC and additional content info in Edit Content tab
                    </p>
                </div>
                
                <!-- Recent Events -->
                <div class="steam-content-section">
                    <div class="steam-section-title">Recent Events & Announcements</div>
                    <p style="color:#acb2b8; font-size:13px;">
                        View all - Add news and update announcements in Edit Content tab
                    </p>
                </div>
            </div>
            
            <!-- RIGHT COLUMN (Sidebar) -->
            <div class="steam-right-col">
                <div class="steam-sidebar-box">
                    <!-- Game Image -->
                    <div class="steam-game-image-area">
                        <div class="game-img-icon">🎮</div>
                        <div>Header Capsule<br>(460×215)</div>
                    </div>
                    
                    <!-- Short Description -->
                    <div class="steam-sidebar-desc">
                        {short_desc if short_desc else '<em style="opacity:0.6">Add a short description...</em>'}
                    </div>
                    
                    <!-- Features/Meta Info -->
                    <div class="steam-sidebar-features">
                        <div>
                            <span class="steam-feature-label">RELEASE DATE:</span>
                            {release_date}
                        </div>
                        <div>
                            <span class="steam-feature-label">DEVELOPER:</span>
                            {developer}
                        </div>
                        <div>
                            <span class="steam-feature-label">PUBLISHER:</span>
                            {project.get('publisher', developer)}
                        </div>
                    </div>
                    
                    <!-- Tags -->
                    <div class="steam-sidebar-tags">
                        {tags_html if tags_html else '<div style="opacity:0.6; font-size:11px;"><em>Add tags...</em></div>'}
                    </div>
                    
                    <!-- Purchase Box -->
                    <div class="steam-purchase-box">
                        <div class="steam-price">{price}</div>
                        <div class="steam-buy-button">Add to Cart</div>
                    </div>
                </div>
                
                <!-- Features Panel -->
                <div class="steam-info-panel">
                    <div class="steam-info-title">Features</div>
                    <div class="steam-info-content">
                        <div class="steam-info-item">
                            <span class="steam-info-icon">👤</span>
                            Single-player
                        </div>
                        <div class="steam-info-item">
                            <span class="steam-info-icon">🎮</span>
                            Full controller support
                        </div>
                        <div class="steam-info-item">
                            <span class="steam-info-icon">☁️</span>
                            Steam Cloud
                        </div>
                        <div class="steam-info-item">
                            <span class="steam-info-icon">🏆</span>
                            Steam Achievements
                        </div>
                    </div>
                </div>
                
                <!-- Languages Panel -->
                <div class="steam-info-panel">
                    <div class="steam-info-title">Languages</div>
                    <div class="steam-info-content">
                        <table class="language-table">
                            <thead>
                                <tr>
                                    <th></th>
                                    <th>Interface</th>
                                    <th>Audio</th>
                                    <th>Subtitles</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>English</td>
                                    <td class="checkmark">✔</td>
                                    <td class="checkmark">✔</td>
                                    <td class="checkmark">✔</td>
                                </tr>
                                <tr>
                                    <td>French</td>
                                    <td class="checkmark">✔</td>
                                    <td></td>
                                    <td class="checkmark">✔</td>
                                </tr>
                                <tr>
                                    <td>German</td>
                                    <td class="checkmark">✔</td>
                                    <td></td>
                                    <td class="checkmark">✔</td>
                                </tr>
                                <tr>
                                    <td>Spanish</td>
                                    <td class="checkmark">✔</td>
                                    <td></td>
                                    <td class="checkmark">✔</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Achievements Panel -->
                <div class="steam-info-panel">
                    <div class="steam-info-title">Steam Achievements</div>
                    <div class="steam-info-content">
                        <div style="display:flex; gap:8px; margin-bottom:10px;">
                            <div style="width:48px; height:48px; background:rgba(103,193,245,0.1); border-radius:3px; display:flex; align-items:center; justify-content:center; font-size:24px;">🏆</div>
                            <div style="width:48px; height:48px; background:rgba(103,193,245,0.1); border-radius:3px; display:flex; align-items:center; justify-content:center; font-size:24px;">⭐</div>
                            <div style="width:48px; height:48px; background:rgba(103,193,245,0.1); border-radius:3px; display:flex; align-items:center; justify-content:center; font-size:24px;">💎</div>
                            <div style="width:48px; height:48px; background:rgba(103,193,245,0.1); border-radius:3px; display:flex; align-items:center; justify-content:center; font-size:24px;">🎯</div>
                        </div>
                        <div style="color:#67c1f5; font-size:11px;">View all 50+ achievements</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    </body>
    </html>
    """
    
    # Use components.html for proper rendering
    components.html(html_content, height=1000, scrolling=True)



def show_best_practices_guide():
    """Comprehensive best practices guide."""
    st.markdown("### 💡 Steam Page Best Practices")
    st.markdown("*Expert tips from industry professionals and Steam guidelines*")
    
    # Chris Zukowski Tips
    st.markdown("## 🎯 Key Insights from Chris Zukowski")
    st.info("Chris Zukowski is a leading game marketing consultant specializing in Steam optimization")
    
    for category, tips in CHRIS_ZUKOWSKI_TIPS.items():
        with st.expander(f"📘 {category}"):
            for tip in tips:
                st.markdown(f"• {tip}")
    
    # Description Guide
    st.markdown("## 📝 Writing Your Description")
    
    for section, details in DESCRIPTION_BEST_PRACTICES.items():
        with st.expander(f"📄 {section}"):
            if 'limit' in details:
                st.markdown(f"**Character Limit:** {details['limit']}")
            
            st.markdown("**✅ Best Practices:**")
            for practice in details['best_practices']:
                st.markdown(f"• {practice}")
            
            if 'examples_good' in details:
                st.markdown("**Good Examples:**")
                for example in details['examples_good']:
                    st.success(f"✓ {example}")
            
            if 'examples_bad' in details:
                st.markdown("**Bad Examples:**")
                for example in details['examples_bad']:
                    st.error(f"✗ {example}")
            
            if 'structure' in details:
                st.markdown("**Recommended Structure:**")
                for item in details['structure']:
                    st.markdown(f"• {item}")
    
    # Asset Guidelines
    st.markdown("## 🎨 Asset Creation Guidelines")
    
    st.markdown("""
    ### General Capsule Rules:
    - **Logo is king**: Your logo should be readable at all sizes
    - **Test at smallest size**: If it works small, it works everywhere
    - **Consistency**: Use same art style across all capsules
    - **No text**: Beyond your game title/logo
    - **Gameplay clarity**: Art should hint at what game is about
    
    ### Screenshot Guidelines:
    - **Gameplay only**: No concept art or cinematics
    - **Show UI**: Players want to see how game actually looks
    - **Variety**: Different areas, mechanics, scenarios
    - **Quality**: 1920×1080 minimum, 16:9 ratio
    - **First matters**: Most important screenshot goes first
    
    ### Common Mistakes to Avoid:
    - ❌ Illegible text at small sizes
    - ❌ Generic stock imagery
    - ❌ Fake review scores or quotes
    - ❌ Misleading gameplay representation
    - ❌ Too dark or too busy designs
    - ❌ Inconsistent branding
    """)
    
    # Resources
    st.markdown("## 📚 Official Resources")
    
    st.markdown("""
    - **Steam Partner Documentation**: Complete asset requirements and templates
    - **Chris Zukowski's Blog**: How To Market A Game (howtomarketagame.com)
    - **Steam Asset Templates**: Download official PSD templates
    - **Community Feedback**: Test your page with real players early
    """)
    
    # Quick Tips
    st.markdown("## ⚡ Quick Tips")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("""
        **DO:**
        - Use all 20 tags
        - Show actual gameplay
        - Test capsule readability
        - Format description nicely
        - Update regularly
        - Get feedback early
        """)
    
    with col2:
        st.error("""
        **DON'T:**
        - Use concept art as screenshots
        - Add text to capsules
        - Link to external sites in description
        - Fake Steam UI elements
        - Forget to localize
        - Rush the process
        """)


def save_project(project):
    """Save project to JSON file."""
    projects_dir = Path("data/steam_pages")
    projects_dir.mkdir(parents=True, exist_ok=True)
    
    project['modified_at'] = datetime.now().isoformat()
    filename = f"steam_page_{project['id']}.json"
    filepath = projects_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(project, f, indent=2, ensure_ascii=False)
    
    # Update session state
    if 'steam_page_projects' not in st.session_state:
        st.session_state.steam_page_projects = {}
    st.session_state.steam_page_projects[project['id']] = project
    
    return filepath


def load_project(project_id):
    """Load a specific project from JSON file."""
    projects_dir = Path("data/steam_pages")
    filepath = projects_dir / f"steam_page_{project_id}.json"
    
    if not filepath.exists():
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
